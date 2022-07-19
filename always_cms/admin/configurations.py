# -*- coding: utf-8 -*-
""" Module used for manage configurations data"""

from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, request, flash

from always_cms.libs.roles import require_permission
from always_cms.libs import configurations, mail, roles

from .routes import admin


@admin.route('/admin/configuration')
@login_required
@require_permission('configuration')
def configurations_edit():
    return render_template('configuration.html', title_page="Configurations", config=configurations.get_all(), roles=roles.get_all())


@admin.route('/admin/configuration', methods=['POST'])
@login_required
@require_permission('configuration')
def configurations_edit_post():
    for key in request.form:
        if key != 'csrf_token':
            if key != 'mail_password' or request.form.get(key) is not None:
                if key == 'minify_template':
                    configurations.set_minifier(request.form.get(key))
                configurations.edit(key, request.form.get(key))

    flash('Your configuration has been successfully edited.', 'success')
    return redirect(url_for('admin.configurations_edit'))


@admin.route('/admin/configuration/emailtesting')
@login_required
@require_permission('configuration')
def configurations_mail_test():
    if mail.send('test', 'message', [ current_user.email ]):
        flash('Test email sent successfully.', 'success')
    else:
        flash('Failed to send email.', 'warning')
    return redirect(url_for('admin.configurations_edit'))