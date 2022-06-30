# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import render_template, redirect, url_for, request
from flask_babel import gettext

from always_cms.libs import terms
from always_cms.libs.roles import require_permission

from .routes import admin


@admin.route('/admin/terms')
@login_required
@require_permission('terms.list')
def terms_list():
    return render_template('terms.html', title_page=gettext("Categories and Terms"), terms_list=terms.get_all('all'))


@admin.route('/admin/terms/new')
@login_required
@require_permission('terms.edit')
def terms_new():
    return render_template('new-term.html', title_page=gettext("Categories and Terms"))


@admin.route('/admin/terms/new', methods=['POST'])
@login_required
@require_permission('terms.edit')
def terms_new_post():
    name = request.form.get('name')
    description = request.form.get('description')
    classification = request.form.get('classification')

    terms.add(classification, name, description)

    return redirect(url_for('admin.terms_new'))


@admin.route('/admin/terms/edit/<term_id>')
@login_required
@require_permission('terms.edit')
def terms_edit(term_id):
    return render_template('edit-term.html', title_page=gettext("Terms"), term=terms.get(term_id))


@admin.route('/admin/terms/edit/<term_id>', methods=['POST'])
@login_required
@require_permission('terms.edit')
def terms_edit_post(term_id):
    name = request.form.get('name')
    description = request.form.get('description')
    classification = request.form.get('classification')

    terms.edit(term_id, classification, name, description)

    return redirect(url_for('admin.terms_edit', term_id=term_id))


@admin.route('/admin/terms/delete/<term_id>')
@login_required
@require_permission('terms.edit')
def terms_delete(term_id):
    terms.delete(term_id)
    return redirect(url_for('admin.terms_list'))
