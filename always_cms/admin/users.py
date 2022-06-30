# -*- coding: utf-8 -*-

from flask_login import logout_user, login_required, current_user
from flask_babel import gettext
from flask import render_template, redirect, url_for, request, flash
from pyotp import random_base32

from always_cms.libs import configurations, users
from always_cms.libs.roles import require_permission

from .routes import admin


@admin.route('/admin/signup')
def signup():
    if configurations.get('users_can_register').value == "False":
        flash('Registrations are disabled. Please contact the administrator.', 'warning')
        return redirect(url_for('admin.login'))
    return render_template('signup.html')


@admin.route('/admin/signup', methods=['POST'])
def signup_post():
    if users.add():
        return redirect(url_for('admin.login'))
    else:
        return redirect(url_for('admin.signup'))


@admin.route('/admin/signup/confirmation/<user_id>/<registration_key>')
def signup_confirmation(user_id, registration_key):
    user_meta = users.get_meta(user_id)
    if user_meta['registration_confirmed'] == 'False':
        if user_meta['registration_key'] == registration_key:
            users.edit_meta(user_id, 'registration_confirmed', 'True')
            flash(gettext('Your email address has been successfully validated. You can now sign in.'), 'success')
        else:
            flash(gettext('Your validation code is invalid. Try again.'), 'warning')
    else:
        flash(gettext('Your email address is already validated.'), 'warning')
    return redirect(url_for('admin.login'))


@admin.route('/admin/forgot')
def forgot_password():
    return render_template('forgot-password.html')


@admin.route('/admin/forgot', methods=['POST'])
def forgot_password_post():
    email = request.form.get('email')
    users.request_new_password(email)
    return redirect(url_for('admin.login'))


@admin.route('/admin/login')
def login():
    return render_template('login.html')


@admin.route('/admin/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    return users.signin(email, password, remember)


@admin.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route('/admin/users/edit/<user_id>')
@admin.route('/admin/profile')
@login_required
@require_permission('users.edit')
def profile(user_id=None):
    if user_id is None:
        user_id = current_user.id
    user = users.get(user_id)
    if user.mfa_hash:
        return render_template('profile.html', title_page="Profile", user=user)
    else:
        mfa_hash = random_base32()
        qrcode_data = "otpauth://totp/{}:{}?secret={}&issuer={}".format(
            configurations.get('sitename').value, user.email, mfa_hash, configurations.get('sitename').value)
        return render_template('profile.html', title_page="Profile", mfa_hash=mfa_hash,
                               qrcode_data=qrcode_data, user=user)


@admin.route('/admin/users/edit/<user_id>', methods=['POST'])
@admin.route('/admin/profile', methods=['POST'])
@login_required
@require_permission('users.edit')
def profile_post(user_id=None):
    if user_id is None:
        users.edit(current_user.id)
        return redirect(url_for('admin.profile'))
    users.edit(user_id)
    return redirect(url_for('admin.profile', user_id=user_id))


@admin.route('/admin/users')
@login_required
@require_permission('users.list')
def users_list():
    return render_template('users.html', title_page="Users", users=users.get_all())


@admin.route('/admin/users/delete/<user_id>')
@login_required
@require_permission('users.edit')
def users_delete(user_id):
    users.delete(user_id)
    return redirect(url_for('admin.users_list'))
