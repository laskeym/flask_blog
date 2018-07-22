from werkzeug.urls import url_parse

from app import app, db
from app.models import Posts, Users, FatJunction, Tag
from app.forms import NewPost, SearchForm, LoginForm, RegistrationForm

from flask import render_template, flash, redirect, url_for, request, current_app

from flask_login import current_user, login_user, logout_user

import codecs
import markdown


@app.route('/')
@app.route('/blog')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Posts.all().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    form = SearchForm()

    return render_template('index.html', posts=posts,
                           next_url=next_url, prev_url=prev_url,
                           form=form)


@app.route('/blog/<int:post_id>/<slug>')
def blog_view(post_id, slug):
    post = Posts.by_id(post_id)

    tags = Tag.query.join(FatJunction, FatJunction.tag_id==Tag.id) \
                         .filter(FatJunction.blog_id==post.id).all()

    return render_template('blog_view.html', post=post, tags=tags)


@app.route('/blog/create', methods=['GET', 'POST'])
def blog_create():
    form = NewPost()
    if form.validate_on_submit():
        new_post = Posts(title=form.data['title'],
                         headline=form.data['headline'],
                         body=form.data['body'],
                         created_by=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('New post created successfully!')

        url = url_for('blog_view',
                      post_id=new_post.id,
                      slug=new_post.slug)
        return redirect(url)

    return render_template('blog_create.html', form=form)


@app.route('/blog/delete', methods=['GET'])
def blog_delete():
    post = Posts.by_id(request.args.get('post_id'))
    if post.author.id != current_user.id:
        return redirect(url_for('index'))

    db.session.delete(post)
    db.session.commit()

    flash('Post removed successfully!')

    url = url_for('index')
    return redirect(url)


@app.route('/blog/<int:post_id>/<slug>/edit', methods=['GET', 'POST'])
def blog_edit(post_id, slug):
    post = Posts.by_id(post_id)
    if post.author.id != current_user.id:
        return redirect(url_for('index'))

    form = NewPost(**post.__dict__)
    if form.validate_on_submit():
        post.title = form.data['title']
        post.headline = form.data['headline']
        post.body = form.data['body']
        db.session.commit()

        flash('Post updated successfully!')

        url = url_for('blog_view',
                      post_id=post.id,
                      slug=post.slug)
        return redirect(url)

    return render_template('blog_edit.html', form=form, post=post)


@app.route('/blog/search')
def search():
    """
    Blog Search View
    """
    form = SearchForm()
    if not form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts, total = Posts.search(request.args['q'], page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('search', q=form.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', q=form.data, page=page - 1) \
        if page > 1 else None


    return render_template('search.html',
                           posts=posts, next_url=next_url, prev_url=prev_url)


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    """
    Sign In Page
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('sign_in'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('sign_in.html', form=form)


@app.route('/sign-out')
def logout():
    """
    Logout Page
    """
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration Page
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    # Validate form
    if form.validate_on_submit():
        # Create new user and hash password
        new_user = Users(email=form.data['email'], first_name=form.data['first_name'],
        last_name=form.data['last_name'])
        new_user.set_password(form.data['password'])

        db.session.add(new_user)
        db.session.commit()

        flash('Registration Successful!', 'success')

        return redirect(url_for('sign_in'))
    return render_template('register.html', form=form)