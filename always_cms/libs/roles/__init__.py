# -*- coding: utf-8 -*-

from functools import wraps
from flask import current_app, flash
from flask_babel import gettext
from flask_login import current_user
from werkzeug.exceptions import Forbidden

from always_cms.models import Role, Ability, RoleAbility, User
from always_cms.libs import plugins, configurations
from always_cms.app import db


def require_permission(permission):

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            is_allowed = False

            user_role = current_user.role_id

            abilities = Ability.query.join(RoleAbility).join(Role).filter(
                Role.id == user_role, RoleAbility.role_id == Role.id, Ability.id == RoleAbility.ability_id).all()

            for ability in abilities:
                if ability.name == permission:
                    is_allowed = True
                    break

            if is_allowed:
                return func(*args, **kwargs)
            else:
                raise Forbidden('Not allowed')

        return wrapper
    return decorate


def require_permission_in_template(permission):

    is_allowed = False

    user_role = current_user.role_id

    abilities = Ability.query.join(RoleAbility).join(Role).filter(
        Role.id == user_role, RoleAbility.role_id == Role.id, Ability.id == RoleAbility.ability_id).all()

    for ability in abilities:
        if ability.name == permission:
            is_allowed = True
            break

    if is_allowed:
        return True
    else:
        return False


def default_context_processors():
    return {
        'require_permission': require_permission_in_template,
    }


def register_context_processors():
    """Register default context processors to app."""
    current_app.context_processor(default_context_processors)


def get_ability(ability_name):
    return Ability.query.filter_by(name=ability_name).first()


def get_all():
    return Role.query.all()


def get_all_abilities():
    return Ability.query.all()


def get_abilities_by_role(role_id):
    abilities = Ability.query.join(RoleAbility).filter(
        RoleAbility.role_id == role_id, Ability.id == RoleAbility.ability_id).all()
    return abilities


def get(role_id):
    return Role.query.filter_by(id=role_id).first()


def add(role):
    data = locals()

    data = plugins.do_filter("before_role_add", data)

    if not data['role']:
        flash(gettext('This role is empty. Please change role.'), 'warning')
    elif Role.query.filter_by(role=role).first():
        flash(gettext('This role is already in use. Please change role.'), 'warning')
    else:
        new_role = Role(role=data['role'])

        # add the new role to the database
        db.session.add(new_role)
        db.session.commit()

        plugins.do_event("after_role_add", new_role)
        flash(gettext('Your role has been successfully created.'), 'success')
        return new_role
    return False


def add_ability(role_id, ability_id):
    data = locals()
    data = plugins.do_filter("before_ability_add", data)
    get_role = get(data['role_id'])
    user_role = current_user.role_id
    if not get_role.id == user_role:
        if not RoleAbility.query.filter_by(role_id=data['role_id'], ability_id=data['ability_id']).first():
            new_ability = RoleAbility(role_id=data['role_id'], ability_id=data['ability_id'])
            # add the new role to the database
            db.session.add(new_ability)
            db.session.commit()
            plugins.do_event("after_ability_add", new_ability)


def edit(role_id, role):
    data = locals()

    data = plugins.do_filter("before_role_edit", data)

    get_role = get(data['role_id'])

    user_role = current_user.role_id

    if not data['role']:
        flash(gettext('This role is empty. Please change role.'), 'warning')
    elif get_role is not None and str(get_role.id) != data['role_id']:
        flash(gettext('This role is already in use. Please change role.'), 'warning')
    elif get_role.id == user_role:
        flash(gettext("You cannot edit your own role."), 'warning')
    else:
        Role.query.filter_by(id=data['role_id']).update(dict(role=data['role']))
        db.session.commit()
        plugins.do_event("after_role_edit", locals())
        flash(gettext('Your role has been successfully edited.'), 'success')
        return True
    return False


def delete(role_id):
    role = get(role_id)
    if User.query.filter_by(role=role.role).count() != 0:
        flash(gettext('This role is used by users. You can\'t delete it.'), 'warning')
    elif configurations.get('default_users_role').value == str(role_id):
        flash(gettext('You can\'t delete the default users role. Please change it.'), 'warning')
    else:
        plugins.do_event("before_role_delete", locals())
        RoleAbility.query.filter_by(role_id=role_id).delete()
        db.session.commit()        
        Role.query.filter_by(id=role_id).delete()
        db.session.commit()
        flash(gettext('Your role has been successfully deleted.'), 'success')
        plugins.do_event("after_role_delete", locals())        


def delete_ability(role_id, ability_id):
    data = locals()
    data = plugins.do_filter("before_ability_delete", data)
    get_role = get(data['role_id'])
    user_role = current_user.role_id
    if not get_role.id == user_role:
        RoleAbility.query.filter_by(role_id=data['role_id'], ability_id=data['ability_id']).delete()
        db.session.commit()
    plugins.do_event("after_ability_delete", locals())
