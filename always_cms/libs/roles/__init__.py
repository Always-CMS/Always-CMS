# -*- coding: utf-8 -*-

from functools import wraps
from flask import current_app
from flask_login import current_user
from werkzeug.exceptions import Forbidden

from always_cms.models import Role, Ability, RoleAbility


def require_permission(permission):

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            is_allowed = False

            user_role = current_user.role

            abilities = Ability.query.join(RoleAbility).join(Role).filter(
                Role.role == user_role, RoleAbility.role_id == Role.id, Ability.id == RoleAbility.ability_id).all()

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

    user_role = current_user.role

    abilities = Ability.query.join(RoleAbility).join(Role).filter(
        Role.role == user_role, RoleAbility.role_id == Role.id, Ability.id == RoleAbility.ability_id).all()

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
    """Register default context processors to app.
    """
    current_app.context_processor(default_context_processors)
