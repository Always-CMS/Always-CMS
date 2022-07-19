# -*- coding: utf-8 -*-

from flask_login import login_required, current_user
from flask_babel import gettext
from flask import render_template, redirect, url_for, request, flash

from always_cms.libs import configurations, roles
from always_cms.libs.roles import require_permission

from .routes import admin


@admin.route('/admin/roles')
@login_required
@require_permission('roles.list')
def roles_list():
    return render_template('roles.html', title_page="Roles", roles=roles.get_all())


@admin.route('/admin/roles/new')
@login_required
@require_permission('roles.edit')
def roles_new():
    return render_template('new-role.html', title_page="Roles")


@admin.route('/admin/roles/new', methods=['POST'])
@login_required
@require_permission('roles.edit')
def roles_new_post():
    role = request.form.get('role')
    
    new_role = roles.add(role)
    if new_role:
        return redirect(url_for('admin.roles_edit', role_id=new_role.id))
    return redirect(url_for('admin.roles_new'))
        

@admin.route('/admin/roles/edit/<role_id>')
@login_required
@require_permission('roles.edit')
def roles_edit(role_id):
    allowed_abilities = list()
    
    for ability in roles.get_abilities_by_role(role_id):
        allowed_abilities.append(ability.id)
    
    return render_template('edit-role.html', title_page="Roles", role=roles.get(role_id), abilities=roles.get_all_abilities(), allowed_abilities=allowed_abilities)


@admin.route('/admin/roles/edit/<role_id>', methods=['POST'])
@login_required
@require_permission('roles.edit')
def roles_edit_post(role_id):
    role = request.form.get('role')
    allowed_abilities = request.form.getlist('abilities')

    get_role = roles.get(role_id)

    if get_role.role == current_user.role:
        flash(gettext("You cannot edit your own role."), 'warning')
        return redirect(url_for('admin.roles_list'))
    elif role:
        roles.edit(role_id, role)
    else:
        abilities=roles.get_all_abilities()
        for ability in abilities:
            if request.form.get(ability.name):
                roles.add_ability(role_id, ability.id)
            else:
                roles.delete_ability(role_id, ability.id)
        flash(gettext('Your abilities has been successfully edited.'), 'success')
    return redirect(url_for('admin.roles_edit', role_id=role_id))


@admin.route('/admin/roles/delete/<role_id>')
@login_required
@require_permission('roles.edit')
def roles_delete(role_id):
    roles.delete(role_id)
    return redirect(url_for('admin.roles_list'))