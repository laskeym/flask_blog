from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, login
from app.search import add_to_index, remove_from_index, query_index

import datetime

from flask_login import UserMixin
import sqlalchemy as sa

from flask import Markup
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

from slugify import slugify
import timeago


SITE_WIDTH = 800
oembed_providers = bootstrap_basic(OEmbedCache())


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)
        ).paginate(page, per_page, False), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class Posts(SearchableMixin, db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'headline', 'body']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    headline = db.Column(db.String)
    body = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # views = db.Column(db.Integer)
    # likes = db.Column(db.Integer)

    @classmethod
    def all(cls):
        return cls.query.order_by(sa.desc(cls.created_date))  # Return object

    @classmethod
    def by_id(cls, id):
        return cls.query.filter_by(id=id).first_or_404()

    @property
    def slug(self):
        return slugify(self.title)

    @property
    def time_in_words(self):
        return timeago.format(self.created_date)

    @property
    def html_content(self):
        hilite = CodeHiliteExtension(linenums=False,
                                     css_class='highlight my-3')
        extras = ExtraExtension()
        markdown_content = markdown(self.body, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=SITE_WIDTH)

        return Markup(oembed_content)


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    posts = db.relationship('Posts', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)