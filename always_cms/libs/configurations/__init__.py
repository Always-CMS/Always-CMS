# -*- coding: utf-8 -*-

from collections import namedtuple

from always_cms.libs import plugins
from always_cms.app import db, minify
from always_cms.models import Configuration


def get_all():
    config = {}
    for configuration in Configuration.query.all():
        config[configuration.name] = configuration.value
    return namedtuple("Configuration", config.keys())(*config.values())


def get(name):
    return Configuration.query.filter_by(name=name).first()


def add(name, value):
    data = plugins.do_filter("before_configuration_add", locals())
    new_configuration = Configuration(name=data['name'], value=data['value'])
    db.session.add(new_configuration)
    db.session.commit()
    plugins.do_event("after_configuration_add", new_configuration)
    return new_configuration


def edit(name, value):
    data = plugins.do_filter("before_configuration_edit", locals())
    Configuration.query.filter_by(
        name=data['name']).update(dict(value=data['value']))
    db.session.commit()
    plugins.do_event("after_configuration_edit", data)
    return True


def delete(name):
    plugins.do_event("before_configuration_delete", locals())
    Configuration.query.filter_by(name=name).delete()
    db.session.commit()
    plugins.do_event("after_configuration_delete", locals())
    return True


def set_minifier(state):
    if state == "True":
        minify.html = True
        minify.js = True
        minify.cssless = True
    else:
        minify.html = False
        minify.js = False
        minify.cssless = False
