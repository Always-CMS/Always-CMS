# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import render_template, redirect, url_for, request

from always_cms.libs import types, terms, posts
from always_cms.libs.roles import require_permission
from always_cms.models import PostTerm, Term, Model

from .routes import admin


@admin.route('/admin/posts')
@admin.route('/admin/posts/<type_slug>')
@login_required
@require_permission('posts.list')
def posts_list(type_slug=None):
    if type_slug is None:
        return render_template('posts.html', title_page="Posts", posts=posts.get_all())
    else:
        return render_template('posts.html', title_page="Posts", posts=posts.get_all_by_type_slug(type_slug))


@admin.route('/admin/posts/new')
@login_required
@require_permission('posts.edit')
def posts_new():
    models = Model.query.all()
    return render_template('new-post.html', title_page="Posts", categories=terms.get_all('category'),
                           tags=terms.get_all('tag'), types=types.get_all(), models=models)


@admin.route('/admin/posts/new', methods=['POST'])
@login_required
@require_permission('posts.edit')
def posts_new_post():
    title = request.form.get('title')
    body = request.form.get('ckeditor')
    description = request.form.get('description')
    status = request.form.get('status')
    categories = request.form.getlist('categories')
    tags = request.form.getlist('tags')
    type_id = request.form.get('type')
    model_id = request.form.get('model')
    schedule = request.form.get('schedule')

    new_post = posts.add(title, body, description, status,
                         categories, tags, type_id, model_id, schedule)
    if new_post:
        return redirect(url_for('admin.posts_edit', post_id=new_post.id))
    return redirect(url_for('admin.posts_new'))


@admin.route('/admin/posts/edit/<post_id>')
@login_required
@require_permission('posts.edit')
def posts_edit(post_id):
    categories = Term.query.filter_by(
        classification='category').outerjoin(PostTerm).all()
    models = Model.query.all()
    post_term = Term.query.join(PostTerm).filter(
        Term.id == PostTerm.term_id, PostTerm.post_id == post_id).all()
    return render_template('edit-post.html', title_page="Posts", post=posts.get(post_id), categories=categories,
                           tags=terms.get_all('tag'), post_term=post_term, types=types.get_all(), models=models)


@admin.route('/admin/posts/edit/<post_id>', methods=['POST'])
@login_required
@require_permission('posts.edit')
def posts_edit_post(post_id):
    title = request.form.get('title')
    body = request.form.get('ckeditor')
    description = request.form.get('description')
    status = request.form.get('status')
    categories = request.form.getlist('categories')
    tags = request.form.getlist('tags')
    type_id = request.form.get('type')
    model_id = request.form.get('model')
    schedule = request.form.get('schedule')
    posts.edit(post_id, title, body, description, status,
               categories, tags, type_id, model_id, schedule)
    return redirect(url_for('admin.posts_edit', post_id=post_id))


@admin.route('/admin/posts/delete/<post_id>')
@login_required
@require_permission('posts.edit')
def posts_delete(post_id):
    posts.delete(post_id)
    return redirect(url_for('admin.posts_list'))


@admin.route('/admin/posts/duplicate/<post_id>')
@login_required
@require_permission('posts.edit')
def posts_duplicate(post_id):
    post = posts.get(post_id)
    new_post = posts.add('{} - {}'.format(post.title, 'Clone'), post.body,
                         post.description, 'draft', [], [], post.type_id, post.model_id)
    return redirect(url_for('admin.posts_edit', post_id=new_post.id))
