from app import app, db
from app.models import Posts
from app.forms import NewPost

from flask import render_template, flash, redirect, url_for, request

import codecs
import markdown


@app.route('/')
@app.route('/blog')
def index():
    posts = Posts.all().paginate(1, 20, False)

    return render_template('index.html', posts=posts.items)


@app.route('/blog/<int:post_id>/<slug>')
def blog_view(post_id, slug):
    post = Posts.by_id(post_id)

    return render_template('blog_view.html', post=post)


@app.route('/blog/create', methods=['GET', 'POST'])
def blog_create():
    form = NewPost()
    if form.validate_on_submit():
        new_post = Posts(title=form.data['title'],
                         body=form.data['body'])
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
    db.session.delete(post)
    db.session.commit()

    flash('Post removed successfully!')

    url = url_for('index')
    return redirect(url)


@app.route('/blog/<int:post_id>/<slug>/edit', methods=['GET', 'POST'])
def blog_edit(post_id, slug):
    post = Posts.by_id(post_id)
    form = NewPost(**post.__dict__)

    if form.validate_on_submit():
        post.title = form.data['title']
        post.body = form.data['body']
        db.session.commit()

        flash('Post updated successfully!')

        url = url_for('blog_view',
                      post_id=post.id,
                      slug=post.slug)
        return redirect(url)

    return render_template('blog_edit.html', form=form, post=post)
