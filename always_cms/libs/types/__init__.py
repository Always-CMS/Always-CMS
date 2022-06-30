# -*- coding: utf-8 -*-

from flask import flash, abort
from flask_babel import gettext
from slugify import slugify

from always_cms.libs import plugins
from always_cms.app import db
from always_cms.models import Type, Post


def get_all():
    return Type.query.all()


def get(type_id):
    get_type = Type.query.filter_by(id=type_id).first()
    if get_type:
        return get_type
    else:
        abort(404)


def add(name, description):

    data = locals()
    data['slug'] = slugify(name)

    data = plugins.do_filter("before_type_add", data)

    get_type = Type.query.filter_by(slug=data['slug']).first()

    if data['name'] is None:
        flash(gettext('The name is invalid. Please modify it.'), 'warning')
    elif get_type is not None:
        flash(gettext('This permalink is already in use. Please change name.'), 'warning')
    elif Type.query.filter_by(name=data['name']).first():
        flash(gettext('This name is already in use. Please choose another.'), 'warning')
    else:
        new_type = Type(
            name=data['name'], description=data['description'], slug=data['slug'])
        db.session.add(new_type)
        db.session.commit()
        plugins.do_event("after_type_add", new_type)
        flash(gettext('Your type has been successfully created.'), 'success')
        return new_type

    return False


def edit(type_id, name, description):

    data = locals()
    data['slug'] = slugify(name)

    data = plugins.do_filter("before_type_edit", data)

    get_type_by_slug = Type.query.filter_by(slug=data['slug']).first()

    get_type_by_name = Type.query.filter_by(name=data['name']).first()

    if data['name'] is None:
        flash(gettext('The name is invalid. Please modify it.'), 'warning')
    elif get_type_by_slug is not None and str(get_type_by_slug.id) != data['type_id']:
        flash(gettext('This permalink is already in use. Please change name.'), 'warning')
    elif get_type_by_name is not None and str(get_type_by_name.id) != data['type_id']:
        flash(gettext('This name is already in use. Please choose another.'), 'warning')
    else:
        Type.query.filter_by(id=data['type_id']).update(
            dict(slug=data['slug'], name=data['name'], description=data['description']))
        db.session.commit()
        flash(gettext('Your type has been successfully edited.'), 'success')
        data = plugins.do_event("after_type_edit", data)
        return True
    return False


def delete(type_id):
    plugins.do_event("before_type_delete", locals())
    if Post.query.filter_by(type_id=type_id).count() == 0:
        Type.query.filter_by(id=type_id).delete()
        db.session.commit()
        flash(gettext('Your type has been successfully deleted.'), 'success')
        plugins.do_event("after_type_delete", locals())
    else:
        flash(gettext('This type is used on some posts. It must no longer be used on messages in order to be deleted.'), 'warning')
    return True
