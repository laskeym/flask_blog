from app import app, db

import datetime

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


class Posts(db.Model):
    __tablename__ = 'Posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    headline = db.Column(db.String)
    body = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    created_by = db.Column(db.Integer)
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
