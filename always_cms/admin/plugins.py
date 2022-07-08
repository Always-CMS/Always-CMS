# -*- coding: utf-8 -*-
""" Module used for manage plugins"""

from flask_login import login_required
from flask import render_template, redirect, url_for

from always_cms.libs.plugins import get_all_plugins, get_plugin_from_all
from always_cms.libs.roles import require_permission
from always_cms.app import plugin_manager

from .routes import admin


@admin.route('/admin/plugins')
@login_required
@require_permission('plugins.list')
def plugins():
    return render_template('plugins.html', title_page="Plugins", plugins=get_all_plugins())


@admin.route("/admin/plugins/disable/<plugin>")
@login_required
@require_permission('plugins.disable')
def plugin_disable(plugin):
    plugin = get_plugin_from_all(plugin)
    plugin_manager.disable_plugins([plugin])
    return redirect(url_for('admin.plugins'))


@admin.route("/admin/plugins/enable/<plugin>")
@login_required
@require_permission('plugins.enable')
def plugin_enable(plugin):
    plugin = get_plugin_from_all(plugin)
    plugin_manager.enable_plugins([plugin])
    return redirect(url_for('admin.plugins'))



@admin.route("/admin/plugins/config/<plugin>")
@login_required
@require_permission('plugins.enable')
def plugin_configuration(plugin):
    plugin = get_plugin_from_all(plugin)
    plugin.configuration()
    return plugin.configuration()
