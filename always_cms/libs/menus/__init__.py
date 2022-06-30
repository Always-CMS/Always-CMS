# -*- coding: utf-8 -*-

from flask import flash
from flask_babel import gettext

from always_cms.libs import plugins
from always_cms.app import db
from always_cms.models import Configuration, Menu, MenuItem


def get_all():
    return Menu.query.all()


def get(location):
    menu = Menu.query.filter_by(location=location).first()
    items = MenuItem.query.filter(MenuItem.menu_id==menu.id, MenuItem.parent_id==None).all()
    return items


def get_by_id(menu_id):
    return Menu.query.filter_by(id=menu_id).first()


def get_items(menu_id, parent_id=None):
    return MenuItem.query.filter(MenuItem.menu_id==menu_id, MenuItem.parent_id==parent_id).all()


def get_item(item_id):
    return MenuItem.query.filter_by(id=item_id).first()


def add(name, location):
    data = locals()
    
    data = plugins.do_filter("before_menu_add", data)
    
    if Menu.query.filter_by(location=data['location']).first():
        flash(gettext('This location is already in use. Please change location.'), 'warning')
    else:
        new_menu = Menu(name=data['name'], location=data['location'])
        # add the new menu to the database
        db.session.add(new_menu)
        db.session.commit()
        plugins.do_event("after_menu_add", new_menu)
        flash(gettext('Your menu has been successfully created.'), 'success')
        return new_menu

    return False


def add_item(name, link, target, menu_id, parent_id=None):
    data = locals()

    data = plugins.do_filter("before_menu_item_add", data)

    new_menu_item = MenuItem(name=data['name'], link=data['link'], target=data['target'], menu_id=data['menu_id'], parent_id=data['parent_id'])
    # add the new menu item to the database
    db.session.add(new_menu_item)
    db.session.commit()
    plugins.do_event("after_menu_item_add", new_menu_item)
    flash(gettext('Your item has been successfully created.'), 'success')
    return new_menu_item    


def edit(menu_id, name, location):
    data = locals()

    data = plugins.do_filter("before_menu_edit", data)

    Menu.query.filter_by(
        id=data['menu_id']).update(dict(name=data['name'], location=data['location']))
    db.session.commit()
    flash(gettext('Your menu has been successfully edited.'), 'success')
    plugins.do_event("after_menu_edit", data)


def edit_item(item_id, name, link, target):
    data = locals()

    data = plugins.do_filter("before_menu_item_edit", data)

    MenuItem.query.filter_by(
        id=data['item_id']).update(dict(name=data['name'], link=data['link'], target=data['target']))
    db.session.commit()
    flash(gettext('Your item has been successfully edited.'), 'success')
    plugins.do_event("after_menu_item_edit", data)


def delete(menu_id):
    plugins.do_event("before_menu_delete", locals())
    menu = Menu.query.filter_by(id=menu_id).first()
    if menu:
        MenuItem.query.filter_by(menu_id=menu_id).delete()
        Menu.query.filter_by(id=menu_id).delete()
        db.session.commit()
        flash(gettext('Your menu has been successfully deleted.'), 'success')
        plugins.do_event("after_menu_delete", locals())

def delete_item(item_id):
    plugins.do_event("before_menu_item_delete", locals())
    MenuItem.query.filter_by(id=item_id).delete()
    db.session.commit()
    flash(gettext('Your item has been successfully deleted.'), 'success')
    plugins.do_event("after_menu_item_delete", locals())