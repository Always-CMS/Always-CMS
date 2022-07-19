# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import render_template, redirect, url_for, request, flash

from always_cms.libs import comments, plugins
from always_cms.libs.roles import require_permission
from always_cms.app import db
from always_cms.models import Comment

from .routes import admin


@admin.route('/admin/comments')
@login_required
@require_permission('comments.list')
def comments_list():
    return render_template('comments.html', title_page="Comments", comments=comments.get_all())


@admin.route('/admin/comments/approval/<comment_id>')
@login_required
@require_permission('comments.edit')
def comments_approval(comment_id):
    comments.approval(comment_id)
    return redirect(url_for('admin.comments_list'))


@admin.route('/admin/comments/rejected/<comment_id>')
@login_required
@require_permission('comments.edit')
def comments_rejected(comment_id):
    comments.rejected(comment_id)
    return redirect(url_for('admin.comments_list'))


@admin.route('/admin/comments/delete/<comment_id>')
@login_required
@require_permission('comments.edit')
def comments_delete(comment_id):
    comments.delete(comment_id)
    return redirect(url_for('admin.comments_list'))
