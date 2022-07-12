# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import redirect, url_for, request

from always_cms.libs import notifications

from .routes import admin

@admin.route('/admin/notifications/<notification_id>')
@login_required
def redirect_notification(notification_id):
    notification = notifications.get(notification_id)
    if notification == None:
        return redirect(url_for('admin.index'))
    else:
        notifications.delete(notification_id)
        if notification.object_id == 'user':
            return redirect(url_for('admin.users_list'))
        if notification.object_id == 'comment':
            return redirect(url_for('admin.comments_list'))
    return redirect(url_for('admin.index'))