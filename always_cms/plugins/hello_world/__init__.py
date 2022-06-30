from flask import flash, Blueprint, render_template, render_template_string, request
from always_cms.libs.plugins import AppPlugin, add_event, add_field_new_post

__plugin__ = "HelloWorld"
__version__ = "1.0.0"

hello = Blueprint("hello", __name__, template_folder="templates")


@hello.route("/")
def index():
    return render_template("hello.html")


def before_post_add(data):
    print(data, flush=True)
    print(request.form.get('plugin_field'), flush=True)
    return data


def field_new_post():
    return '''<div class="form-group">
              <label for="plugin_field">%s</label>
              <input type="text" class="form-control" id="plugin_field" name="plugin_field" placeholder="%s">
            </div>''' % ('test', 'test2')


class HelloWorld(AppPlugin):

    def setup(self):
        self.register_blueprint(hello, url_prefix="/hello")
        add_field_new_post(field_new_post)
        add_event("before_post_add", before_post_add)
