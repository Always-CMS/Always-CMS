# -*- coding: utf-8 -*-

from flask import flash, request, redirect, url_for, abort, render_template
from flask_login import current_user, login_user
from flask_babel import gettext
from werkzeug.security import generate_password_hash, check_password_hash
from pyotp import TOTP
from uuid import uuid4

from always_cms.libs import configurations, plugins, validator, comments, mail
from always_cms.app import db
from always_cms.models import User, UserMeta


def get_all():
    return User.query.all()


def get(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return user
    else:
        abort(404)


def get_meta(user_id):
    user = get(user_id)
    result = {}
    for meta in user.meta:
        result[meta.name] = meta.value
    return result


def add():
    warning = False
    if configurations.get('users_can_register').value == "False":
        flash(gettext(
            'Registrations are disabled. Please contact the administrator.'), 'warning')
        warning = True
    if not request.form.get('name'):
        flash(gettext('Please enter your name to register.'), 'warning')
        warning = True
    if not request.form.get('email'):
        flash(gettext('Please enter an email address to register.'), 'warning')
        warning = True
    if not validator.email( request.form.get('email') ):
        flash(gettext('Please enter a valid email address to register.'), 'warning')
        warning = True
    if not request.form.get('password'):
        flash(gettext('Please enter a password to register.'), 'warning')
        warning = True
    if request.form.get('password') != request.form.get('repeat_password'):
        flash(gettext('Your passwords must match to register.'), 'warning')
        warning = True
    if not request.form.get('terms'):
        flash(gettext('Please accept the terms of use to register.'), 'warning')
        warning = True

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).first():
        flash(gettext(
            'This email address is already associated with a user. Please use another one.'), 'warning')
        warning = True

    if warning is True:
        return False

    if User.query.count() == 0:
        role = 'Administrator'
    else:
        role = 'Membership'

    # create a new user with the form data.
    new_user = User(name=name, email=email, password=generate_password_hash(
        password, method='sha256'), role=role)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    user_meta_registration_key = UserMeta(user_id=new_user.id, name='registration_key', value=uuid4.hex)

    if configurations.get('registration_confirmation').value == "False":
        user_meta_registration_confirmed = UserMeta(user_id=new_user.id, name='registration_confirmed', value='True')
    else:
        user_meta_registration_confirmed = UserMeta(user_id=new_user.id, name='registration_confirmed', value='False')
        mail.send('test', 'mon message', [email])
    
    db.session.add_all([user_meta_registration_confirmed, user_meta_registration_key])
    db.session.commit()

    flash(gettext('Your account has been successfully created. You can login.'), 'success')
    return True


def add_meta(user_id, name, value):
    data = plugins.do_filter("before_user_meta_add", locals())
    # create a new user meta
    new_user_meta = UserMeta(user_id=user_id, name=name, value=value)

    # add the new user meta to the database
    db.session.add(new_user_meta)
    db.session.commit()
    plugins.do_event("after_user_meta_add", locals())
    return True


def signin(email, password, remember):
    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user:
        flash(gettext('Please check your login details and try again.'), 'warning')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for('admin.login'))
    if password is not None and not check_password_hash(user.password, password):
        flash(gettext('Please check your login details and try again.'), 'warning')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for('admin.login'))
    elif password is not None and check_password_hash(user.password, password) and user and user.mfa_hash is None:
        meta = get_meta(user.id)
        if meta['registration_confirmed'] == 'False':
            flash(gettext('Please confirm your email address by clicking on the link sent to you before sign in.'), 'warning')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('admin.login'))
        else:
            # if the above check passes, then we know the user has the right credentials
            login_user(user, remember=remember)
            return redirect(url_for('admin.index'))
    if user and user.mfa_hash is not None and request.form.get('otp_code') is None:
        flash(gettext("Please validate your OTP code."), 'success')
        return render_template('login.html', email=email, remember=remember, mfa_hash='true')
    if user and user.mfa_hash is not None and request.form.get('otp_code'):
        otp_code = request.form.get('otp_code')
        if TOTP(user.mfa_hash).verify(otp_code, valid_window=2):
            # if the above check passes, then we know the user has the right credentials
            login_user(user, remember=remember)
            return redirect(url_for('admin.index'))
        else:
            flash(gettext("Please check your OTP code and try again."), 'warning')
            return render_template('login.html', email=email, remember=remember, mfa_hash='true')


def request_new_password(email):
    flash(gettext('If your email address has been found, a link has been sent to reset your password.'), 'success')
    user = User.query.filter_by(email=email).first()
    if user:
        forgot_password_key = uuid4.hex
        add_meta(user.id, 'forgot_password_key', forgot_password_key)
        mail.send('title', 'message', email)
        return True
    return False


def set_new_password(forgot_password_key, password):
    return True


def edit(user_id):
    block = request.form.get("block")

    if block == "identity":
        return edit_identity(user_id)
    elif block == "security":
        return edit_security(user_id)
    else:
        return False


def edit_identity(user_id):

    user = get(user_id)

    name = request.form.get("name")
    email = request.form.get("email")

    if name is None:
        flash(gettext("This name is not valid."), "danger")
        return False
    else:
        if user.name != name:
            User.query.filter_by(id=user.id).update(dict(name=name))
            flash(gettext("The name was successfully updated."), "success")

    if email is None or validator.email(email) is False:
        flash(gettext("This email is not valid."), "danger")
        return False
    else:
        if user.email != email:
            if User.query.filter_by(email=email).first():
                flash(gettext("This email is already used."), "danger")
                return False
            else:
                User.query.filter_by(id=user.id).update(dict(email=email))
                flash(gettext("The email was successfully updated."), "success")

    db.session.commit()
    return True


def edit_security(user_id):

    user = get(user_id)

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    repeat_new_password = request.form.get("repeat_new_password")

    if current_password is not None:
        if check_password_hash(user.password, current_password):
            if new_password == repeat_new_password:
                User.query.filter_by(id=user.id).update(
                    dict(password=generate_password_hash(new_password, method='sha256')))
                db.session.commit()
                flash(gettext("Your password has been updated."), "success")
                return True
            else:
                flash(gettext("New passwords are not the same."), "danger")
        else:
            flash(gettext("The current password is invalid."), "danger")

    mfa_hash = request.form.get(
        "mfa_hash") if request.form.get("mfa_hash") else None
    otp_code = int(request.form.get("otp_code")
                   ) if request.form.get("otp_code") else None

    if mfa_hash is not None and otp_code is not None:
        # verifying submitted OTP with PyOTP
        if TOTP(mfa_hash).verify(otp_code, valid_window=2):
            # inform users if OTP is valid
            flash(gettext("The TOTP 2FA token is valid."), "success")
            User.query.filter_by(id=user.id).update(dict(mfa_hash=mfa_hash))
            db.session.commit()
            return redirect(url_for("admin.profile"))
        else:
            # inform users if OTP is invalid
            flash(gettext("You have supplied an invalid 2FA token."), "danger")
            return redirect(url_for("admin.profile"))
    elif request.form.get("disable_mfa") == "true":
        User.query.filter_by(id=user.id).update(dict(mfa_hash=db.null()))
        db.session.commit()
        flash(gettext("Your MFA has been disabled."), "success")
        return True
    return False


def edit_meta(user_id, name, value):
    data = plugins.do_filter("before_user_meta_edit", locals())
    UserMeta.query.filter(UserMeta.user_id==user_id, UserMeta.name==name).update(dict(value=value))
    db.session.commit()
    plugins.do_event("after_user_meta_edit", locals())
    return True


def delete(user_id):
    plugins.do_event("before_user_delete", locals())
    if get(user_id):
        if user_id != str(current_user.id):
            flash(gettext("Your user has been successfully deleted."), 'success')
            comments.change_user_id(None, user_id)
            User.query.filter_by(id=user_id).delete()
            db.session.commit()
            plugins.do_event("after_user_delete", locals())
            return True
        else:
            flash(gettext("You cannot delete your own user account."), 'warning')
    return False


def count():
    return User.query.count()
