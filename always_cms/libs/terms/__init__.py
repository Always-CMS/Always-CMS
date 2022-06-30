# -*- coding: utf-8 -*-

from flask import flash, abort
from flask_babel import gettext
from slugify import slugify

from always_cms.libs import plugins
from always_cms.app import db
from always_cms.models import Term, PostTerm


def get_all(classification='category'):
    if classification.lower() == 'all':
        return Term.query.all()
    return Term.query.filter_by(classification=classification).all()


def get(term_id):
    term = Term.query.filter_by(id=term_id).first()
    if term:
        return term
    else:
        abort(404)


def add(classification, name, description):

    data = locals()
    data['slug'] = slugify(name)

    data = plugins.do_filter("before_term_add", data)

    get_term = Term.query.filter_by(slug=data['slug']).first()

    if data['name'] is None:
        flash(gettext('The name is invalid. Please modify it.'), 'warning')
    elif get_term is not None:
        flash(gettext('This permalink is already in use. Please change name.'), 'warning')
    elif Term.query.filter_by(name=data['name']).first():
        flash(gettext('This name is already in use. Please choose another.'), 'warning')
    elif classification not in ['category', 'tag']:
        flash(
            gettext('This classification is not valid. Please select another.'), 'warning')
    else:
        new_term = Term(classification=data['classification'], name=data['name'],
                        description=data['description'], slug=data['slug'])
        db.session.add(new_term)
        db.session.commit()
        plugins.do_event("after_term_add", new_term)
        flash(gettext('Your category or term has been successfully created.'), 'success')
        return new_term

    return False


def edit(term_id, classification, name, description):

    data = locals()
    data['slug'] = slugify(name)

    data = plugins.do_filter("before_term_edit", data)

    get_term = Term.query.filter_by(slug=data['slug']).first()

    if get_term is not None and str(get_term.id) != term_id:
        flash(gettext('This permalink is already in use. Please change name.'), 'warning')
    elif classification not in ['category', 'tag']:
        flash(
            gettext('This classification is not valid. Please select another.'), 'warning')
    else:
        Term.query.filter_by(id=data['term_id']).update(dict(
            classification=data['classification'],
            name=data['name'],
            description=data['description'],
            slug=data['slug']
        ))
        db.session.commit()
        flash(gettext('Your term has been successfully edited.'), 'success')
        plugins.do_event("after_term_edit", data)
        return True
    return False


def delete(term_id):
    plugins.do_event("before_term_delete", locals())
    if PostTerm.query.filter_by(term_id=term_id).count() == 0:
        Term.query.filter_by(id=term_id).delete()
        db.session.commit()
        flash(gettext('Your term has been successfully deleted.'), 'success')
        plugins.do_event("after_term_delete", locals())
    else:
        flash(gettext('This term is used on some posts. It must no longer be used on messages in order to be deleted.'), 'warning')
    return True


def link_to_post(term_id, post_id):
    data = plugins.do_filter("before_term_link_to_post", locals())
    new_link = PostTerm(term_id=data['term_id'], post_id=data['post_id'])
    db.session.add(new_link)
    db.session.commit()
    plugins.do_event("after_term_link_to_post", new_link)
    return True


def unlink_to_post(term_id, post_id):
    data = plugins.do_filter("before_term_unlink_to_post", locals())
    PostTerm.query.filter_by(
        term_id=data['term_id'], post_id=data['post_id']).delete()
    db.session.commit()
    plugins.do_event("after_term_unlink_to_post", locals())
    return True
