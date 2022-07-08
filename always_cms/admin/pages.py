# -*- coding: utf-8 -*-
""" Page module is used for manipulate Page objects"""

from flask_login import login_required
from flask import render_template, redirect, url_for, request

from always_cms.libs import terms, pages
from always_cms.libs.roles import require_permission

from .routes import admin


@admin.route('/admin/pages')
@login_required
@require_permission('pages.list')
def pages_list():
    return render_template('pages.html', title_page="Pages", pages=pages.get_all())


@admin.route('/admin/pages/new')
@login_required
@require_permission('pages.edit')
def pages_new():
    return render_template('new-post.html', title_page="Pages",
                           categories=terms.get_all('category'), tags=terms.get_all('tag'))


@admin.route('/admin/pages/new', methods=['POST'])
@login_required
@require_permission('pages.edit')
def pages_new_post():
    title = request.form.get('title')
    body = request.form.get('ckeditor')
    description = request.form.get('description')
    status = request.form.get('status')
    schedule = request.form.get('schedule')
    new_page = pages.add(title, body, description, status, schedule)
    if new_page:
        return redirect(url_for('admin.pages_edit', page_id=new_page.id))
    return redirect(url_for('admin.pages_new'))


@admin.route('/admin/pages/edit/<page_id>')
@login_required
@require_permission('pages.edit')
def pages_edit(page_id):
    return render_template('edit-post.html', title_page="Pages", post=pages.get(page_id))


@admin.route('/admin/pages/edit/<page_id>', methods=['POST'])
@login_required
@require_permission('pages.edit')
def pages_edit_post(page_id):
    title = request.form.get('title')
    body = request.form.get('ckeditor')
    description = request.form.get('description')
    status = request.form.get('status')
    schedule = request.form.get('schedule')
    pages.edit(page_id, title, body, description, status, schedule)
    return redirect(url_for('admin.pages_edit', page_id=page_id))


@admin.route('/admin/pages/delete/<page_id>')
@login_required
@require_permission('pages.edit')
def pages_delete(page_id):
    pages.delete(page_id)
    return redirect(url_for('admin.pages_list'))


@admin.route('/admin/pages/duplicate/<page_id>')
@login_required
@require_permission('pages.edit')
def pages_duplicate(page_id):
    page = pages.get(page_id)
    # add the new post to the database
    new_page = pages.add('{} - {}'.format(page.title, 'Clone'),
                         page.body, page.description, 'draft')
    return redirect(url_for('admin.pages_edit', page_id=new_page.id))
