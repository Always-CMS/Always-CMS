# -*- coding: utf-8 -*-

from flask_login import login_required
from flask import render_template, redirect, url_for, flash, current_app

from always_cms.libs.templates import get_all_templates, get_template, list_template_files, get_content_file
from always_cms.libs.roles import require_permission
from always_cms.app import db
from always_cms.models import Configuration

from .routes import admin


@admin.route('/admin/themes')
@login_required
@require_permission('themes.list')
def themes():
    return render_template('themes.html',
                           title_page="Themes",
                           templates=get_all_templates()
                           )


@admin.route("/admin/themes/enable/<theme>")
@login_required
@require_permission('themes.enable')
def theme_enable(theme):
    new_theme = get_template(theme)
    if new_theme:
        old_theme = get_template(current_app.config['TEMPLATE'])
        old_theme.enabled = False

        current_app.config['TEMPLATE'] = new_theme.identifier
        Configuration.query.filter_by(name='template').update(
            dict(value=new_theme.identifier))
        db.session.commit()
        new_theme.enabled = True
        flash('The theme was successfully activated.', 'success')
    else:
        flash('The selected theme is invalid.', 'warning')
    return redirect(url_for('admin.themes'))
