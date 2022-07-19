# -*- coding: utf-8 -*-

from flask import flash
from flask_login import current_user
from sqlalchemy import or_, and_

from always_cms.libs import plugins, comments, users, roles
from always_cms.app import db
from always_cms.models import Notification, RoleAbility, Role, User, Ability


def get_all():
    return Notification.query.all()


def get_available():
    user_role = current_user.role
    user_id = current_user.id
    return Notification.query.filter_by(user_id=user_id).union( Notification.query.join(Ability).join(RoleAbility).join(Role).filter(Role.role == user_role, RoleAbility.role_id == Role.id, Notification.ability_id == RoleAbility.ability_id) )


def get(notification_id):
    notification = Notification.query.filter_by(id=notification_id).first()
    if notification == None or ( notification.user_id != None and notification.user_id != current_user.id and notification.ability_id != None and not require_permission(notification.ability.name) ):
        return None
    else:
        return notification


def add(object_type, object_id, message, user_id = None, ability_id = None):
    
    data = plugins.do_filter("before_notification_add", locals())
    
    if data['user_id'] == None and data['ability_id'] == None:
        return False
    
    if data['user_id'] != None and not users.get(data['user_id']):
        return False
    
    if data['object_type'] not in ['comment', 'user', 'system']:
        return False
    
    if data['object_type'] == 'comment' and not comments.get(data['object_id']):
        return False
    elif data['object_type'] == 'comment':
        data['object_comment_id'] = data['object_id']
        data['object_user_id'] = None
    
    if data['object_type'] == 'user' and not users.get(data['object_id']):
        return False
    elif data['object_type'] == 'user':
        data['object_comment_id'] = None
        data['object_user_id'] = data['object_id']
    
    new_notification = Notification(object_type=data['object_type'],
    message=data['message'],
    object_comment_id=data['object_comment_id'],
    object_user_id=data['object_user_id'],
    user_id=data['user_id'],
    ability_id=data['ability_id'])
    
    db.session.add(new_notification)
    db.session.commit()

    plugins.do_event("after_notification_add", new_notification)

    return new_notification


def delete(notification_id):
    plugins.do_event("before_notification_delete", locals())
    Notification.query.filter_by(id=notification_id).delete()
    db.session.commit()
    plugins.do_event("after_notification_delete", locals())
    return True