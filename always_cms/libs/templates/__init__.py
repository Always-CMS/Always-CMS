# -*- coding: utf-8 -*-

import os

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack
from flask import json, current_app


class TemplateError(Exception):
    pass


def get_template(identifier):
    """Returns a template instance from all templates (includes also the disabled
    ones) for the given name.
    """
    ctx = stack.top
    return ctx.app.extensions.get('template_manager')._all_templates[identifier]


def get_all_templates():
    """Returns all templates as a list including the disabled ones."""
    ctx = stack.top
    return ctx.app.extensions.get('template_manager')._all_templates.values()


class Template(object):
    """Every template should implement this class. It handles the registration
    for the template hooks, creates or modifies additional relations or
    registers template specific thinks
    """

    #: If setup is called, this will be set to ``True``.
    enabled = False

    def __init__(self, path):
        #: The template's root path. All the files in the template are under this
        #: path.
        self.path = os.path.abspath(path)

        with open(os.path.join(path, 'info.json')) as fd:
            self.info = i = json.load(fd)

        #: The template's name, as given in info.json. This is the human
        #: readable name.
        self.name = i['name']

        #: The template's identifier. This is an actual Python identifier,
        #: and in most situations should match the name of the directory the
        #: template is in.
        self.identifier = i['identifier']

        #: The human readable description. This is the default (English)
        #: version.
        self.description = i.get('description')

        #: This is a dictionary of localized versions of the description.
        #: The language codes are all lowercase, and the ``en`` key is
        #: preloaded with the base description.
        self.description_lc = dict(
            (k.split('_', 1)[1].lower(), v) for k, v in i.items()
            if k.startswith('description_')
        )
        self.description_lc.setdefault('en', self.description)

        #: The author's name, as given in info.json. This may or may not
        #: include their email, so it's best just to display it as-is.
        self.author = i['author']

        #: A short phrase describing the license, like "GPL", "BSD", "Public
        #: Domain", or "Creative Commons BY-SA 3.0".
        self.license = i.get('license')

        #: A URL pointing to the license text online.
        self.license_url = i.get('license_url')

        #: The URL to the template's or author's Web site.
        self.website = i.get('website')

        #: The template's version string.
        self.version = i.get('version')

        #: Any additional options. These are entirely application-specific,
        #: and may determine other aspects of the application's behavior.
        self.options = i.get('options', {})


class TemplateManager(object):
    """Collects all Templates and maps the metadata to the template"""

    def __init__(self, app=None, **kwargs):
        """Initializes the TemplateManager. It is also possible to initialize the
        TemplateManager via a factory. For example::

            template_manager = TemplateManager()
            template_manager.init_app(app)

        :param app: The flask application.

        :param template_folder: The template folder where the templates resides.

        :param base_app_folder: The base folder for the application. It is used
                                to build the templates package name.
        """
        # All templates - including the disabled ones
        self._all_templates = None

        # All available templates including the disabled ones
        self._available_templates = dict()

        # All found templates
        self._found_templates = list()

        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, base_app_folder=None, template_folder="templates"):
        app.template_manager = self
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['template_manager'] = self
        self.app = app

        if base_app_folder is None:
            base_app_folder = self.app.root_path.split(os.sep)[-1]

        self.template_folder = os.path.join(
            self.app.root_path, template_folder)
        self.base_template_package = ".".join(
            [base_app_folder, template_folder]
        )

        self.load_templates()

    @property
    def all_templates(self):
        """Returns all templates including disabled ones."""
        if self._all_templates is None:
            self.load_templates()
        return self._all_templates

    def load_templates(self):
        """Loads all templates. They are still disabled.
        Returns a list with all loaded templates. They should now be accessible
        via self.templates.
        """
        self._templates = {}
        self._all_templates = {}
        for template_path in self.find_templates():

            template_instance = Template(template_path)

            if self.app.config['TEMPLATE'] == template_instance.identifier:
                template_instance.enabled = True

            try:
                self._templates[template_instance.identifier] = template_instance
            except KeyError:
                pass

            self._all_templates[template_instance.identifier] = template_instance

    def find_templates(self):
        """Find all possible templates in the template folder."""
        for item in os.listdir(self.template_folder):
            if os.path.isdir(os.path.join(self.template_folder, item)) \
                    and os.path.exists(
                        os.path.join(self.template_folder, item, "info.json")):

                try:
                    self._found_templates.append(
                        os.path.join(self.template_folder, item))

                except AttributeError:
                    pass

        return self._found_templates


def list_template_files(template):
    path = "%s/templates/%s/" % (current_app.root_path, template)
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            file = os.path.join(r, file)
            file = file.replace("%s/templates" % current_app.root_path, "")
            files.append(file)
    return files


def get_content_file(template, file):
    if file in list_template_files(template):
        path = "%s/templates/" % current_app.root_path
        with open("%s/%s" % (path, file)) as f:
            return f.readlines()
    else:
        return False
