# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import render_template, redirect, url_for, flash, current_app, request

from always_cms.libs.roles import require_permission
from always_cms.libs import menus

from .routes import admin


@admin.route('/admin/menus')
@login_required
@require_permission('menus.list')
def menus_list():
    return render_template('menus.html', title_page="Menus", menus=menus.get_all())


@admin.route("/admin/menus/item/<menu_id>")
@admin.route("/admin/menus/item/<menu_id>/<item_id>")
@login_required
@require_permission('menus.edit')
def menus_item_list(menu_id, item_id=None):
    return render_template('menus-items.html', title_page="Menus items", items=menus.get_items(menu_id, item_id), menu_id=menu_id, item_id=item_id)


@admin.route("/admin/menus/new")
@login_required
@require_permission('menus.edit')
def menus_new():
    return render_template('new-menu.html', title_page="Menus")


@admin.route("/admin/menus/new", methods=['POST'])
@login_required
@require_permission('menus.edit')
def menus_new_post():
    name = request.form.get('name')
    location = request.form.get('location')

    new_menu = menus.add(name, location)
    if new_menu:
        return redirect(url_for('admin.menus_edit', menu_id=new_menu.id))
    return redirect(url_for('admin.menus_new'))


@admin.route("/admin/menus/item/new/<menu_id>")
@admin.route("/admin/menus/item/new/<menu_id>/<parent_id>")
@login_required
@require_permission('menus.edit')
def menus_item_new(menu_id, parent_id=None):
    return render_template('new-menu-item.html', title_page="Menus item")


@admin.route("/admin/menus/item/new/<menu_id>", methods=['POST'])
@admin.route("/admin/menus/item/new/<menu_id>/<parent_id>", methods=['POST'])
@login_required
@require_permission('menus.edit')
def menus_item_new_post(menu_id, parent_id=None):
    name = request.form.get('name')
    link = request.form.get('link')
    target = request.form.get('target')

    new_menu_item = menus.add_item(name, link, target, menu_id, parent_id)
    if new_menu_item:
        return redirect(url_for('admin.menus_item_list', menu_id=menu_id, item_id=parent_id))
    return redirect(url_for('admin.menus_new'))


@admin.route("/admin/menus/edit/<menu_id>")
@login_required
@require_permission('menus.edit')
def menus_edit(menu_id):
    menu = menus.get_by_id(menu_id)
    return render_template('edit-menu.html', title_page="Menus", menu=menu)


@admin.route("/admin/menus/edit/<menu_id>", methods=['POST'])
@login_required
@require_permission('menus.edit')
def menus_edit_post(menu_id):
    name = request.form.get('name')
    location = request.form.get('location')

    menus.edit(menu_id, name, location)
    return redirect(url_for('admin.menus_edit', menu_id=menu_id))


@admin.route("/admin/menus/item/edit/<item_id>")
@login_required
@require_permission('menus.edit')
def menus_item_edit(item_id):
    item = menus.get_item(item_id)
    return render_template('edit-menu-item.html', title_page="Menus item", item=item)


@admin.route("/admin/menus/item/edit/<item_id>", methods=['POST'])
@login_required
@require_permission('menus.edit')
def menus_item_edit_post(item_id):
    name = request.form.get('name')
    link = request.form.get('link')
    target = request.form.get('target')

    menus.edit_item(item_id, name, link, target)
    return redirect(url_for('admin.menus_item_edit', item_id=item_id))


@admin.route("/admin/menus/delete/<menu_id>")
@login_required
@require_permission('menus.edit')
def menus_delete(menu_id):
    menus.delete(menu_id)
    return redirect(url_for('admin.menus_list'))

@admin.route("/admin/menus/item/delete/<item_id>")
@login_required
@require_permission('menus.edit')
def menus_item_delete(item_id):
    menus.delete_item(item_id)
    return redirect(url_for('admin.menus_list'))