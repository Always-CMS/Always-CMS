# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import render_template, redirect, url_for, request
from flask_babel import gettext

from always_cms.libs import types
from always_cms.libs.roles import require_permission

from .routes import admin


@admin.route('/admin/types')
@login_required
@require_permission('types.list')
def types_list():
    return render_template('types.html', title_page=gettext("Types"), types=types.get_all())


@admin.route('/admin/types/new')
@login_required
@require_permission('types.edit')
def types_new():
    return render_template('new-type.html', title_page=gettext("Types"))


@admin.route('/admin/types/new', methods=['POST'])
@login_required
@require_permission('types.edit')
def types_new_post():
    name = request.form.get('name')
    description = request.form.get('description')
    types.add(name, description)
    return redirect(url_for('admin.types_new'))


@admin.route('/admin/types/edit/<type_id>')
@login_required
@require_permission('types.edit')
def types_edit(type_id):
    return render_template('edit-type.html', title_page=gettext("Types"), type=types.get(type_id))


@admin.route('/admin/types/edit/<type_id>', methods=['POST'])
@login_required
@require_permission('types.edit')
def types_edit_post(type_id):
    name = request.form.get('name')
    description = request.form.get('description')
    types.edit(type_id, name, description)
    return redirect(url_for('admin.types_edit', type_id=type_id))


@admin.route('/admin/types/delete/<type_id>')
@login_required
@require_permission('types.edit')
def types_delete(type_id):
    types.delete(type_id)
    return redirect(url_for('admin.types_list'))
