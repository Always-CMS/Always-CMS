# -*- coding: utf-8 -*-

from flask import flash, abort, request, current_app, jsonify, url_for
from flask_babel import gettext
from os import path, remove
from random import randint
from shutil import copyfile
from werkzeug.utils import secure_filename
from flask_ckeditor import upload_success, upload_fail

from always_cms.libs import plugins
from always_cms.libs.medias import pillow, s3
from always_cms.libs import configurations
from always_cms.app import db
from always_cms.models import Media, MediaMeta


def get_all():
    return Media.query.all()


def get(media_id):
    media = Media.query.filter_by(id=media_id).first()
    if media:
        return media
    else:
        abort(404)


def get_url(media_id):
    media = get(media_id)
    meta = get_meta(media_id)
    if 'location' in meta and meta['location'] == "s3":
        return "{}/{}/{}".format(configurations.get('s3_endpoint_url').value, configurations.get('s3_bucket_name').value, media_id)
    else:
        return url_for('main.uploaded_files', filename='{}.{}'.format(media.id, media.extension) )


def get_meta(media_id):
    media = get(media_id)
    result = {}
    for meta in media.meta:
        result[meta.name] = meta.value
    return result


def add(file=None):
    ckeditor = False
    # check if the post request has the file part
    if file is None and 'file' not in request.files and 'upload' not in request.files:
        return jsonify(error='No selected file'), 400
    if file is None:
        if 'file' in request.files:
            file = request.files['file']
        elif file is None:
            file = request.files['upload']
            ckeditor = True
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        if ckeditor:
            return upload_fail(message='No selected file')
        else:
            return jsonify(error='No selected file'), 400
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in current_app.config['ALLOWED_EXTENSIONS']:
        if ckeditor:
            return upload_fail(message='File format not allowed')
        else:
            return jsonify(error='File format not allowed'), 400

    title = secure_filename(file.filename.rsplit('.', 1)[0])

    # create a new media with the form data.
    new_media = Media(title=title, extension=extension)

    # add the new media to the database
    db.session.add(new_media)
    db.session.commit()


    if configurations.get('default_upload_location').value == 'local':
        file_path = path.join(
            current_app.config['UPLOAD_FOLDER'], "{}.{}".format(new_media.id, extension))
        file.save(file_path)
        add_meta(new_media.id, 'location', 'local')
    elif configurations.get('default_upload_location').value == 's3':
        s3_handler = s3.S3()
        s3_handler.upload(new_media.id, file.stream)
        s3_handler.get(new_media.id)
        add_meta(new_media.id, 'location', 's3')
    if ckeditor:
        return upload_success(file_path, filename=title)
    else:
        return jsonify(success='File uploaded successfully'), 200


def add_meta(media_id, name, value):
    data = plugins.do_filter("before_media_meta_add", locals())
    # create a new media meta
    new_media_meta = MediaMeta(media_id=media_id, name=name, value=value)

    # add the new media meta to the database
    db.session.add(new_media_meta)
    db.session.commit()
    plugins.do_event("after_media_meta_add", locals())
    return True


def init_media_edit(media_id, force=False):
    media = get(media_id)
    meta = get_meta(media_id)
    media_path = path.join(current_app.config['UPLOAD_FOLDER'], "{}.{}".format(media.id, media.extension))

    if 'location' in meta and meta['location'] == 'local':
        if path.exists(media_path):
            new_media_path = path.join(
                current_app.config['UPLOAD_FOLDER'], "{}-work.{}".format(media.id, media.extension))
            if not path.exists(new_media_path) or force == True:
                copyfile(media_path, new_media_path)
        return new_media_path
    elif 'location' in meta and meta['location'] == 's3':
        new_media_path = path.join(
            current_app.config['UPLOAD_FOLDER'], "{}-work.{}".format(media.id, media.extension))
        if not path.exists(new_media_path) or force == True:
            s3_handler = s3.S3()
            s3_handler.download(media_id, new_media_path)
        return new_media_path
    return False


def replace_original(media_id):
    media = get(media_id)
    meta = get_meta(media_id)
    media_path = path.join(current_app.config['UPLOAD_FOLDER'], "{}-work.{}".format(media.id, media.extension))

    if 'location' in meta and meta['location'] == 'local':
        if path.exists(media_path):
            new_media_path = path.join(
                current_app.config['UPLOAD_FOLDER'], "{}.{}".format(media.id, media.extension))
            copyfile(media_path, new_media_path)
            remove(media_path)
            return True
    elif 'location' in meta and meta['location'] == 's3':
        if path.exists(media_path):
            s3_handler = s3.S3()
            s3_handler.upload_from_file(media_id, media_path)
            return True
    return False

def duplicate(media_id):
    media = get(media_id)

    media_path = path.join(current_app.config['UPLOAD_FOLDER'], "{}.{}".format(media.id, media.extension))

    if path.exists(media_path):
        # create a new media with the form data.
        new_media = Media(title='{} - {} - #{}'.format(media.title, 'Copy', randint(0, 10000)), extension=media.extension)

        # add the new media to the database
        db.session.add(new_media)
        db.session.commit()

        new_media_path = path.join(
            current_app.config['UPLOAD_FOLDER'], "{}.{}".format(new_media.id, media.extension))
        copyfile(media_path, new_media_path)

        return new_media.id
    return False


def edit(media_id, alt_text, description):
    data = plugins.do_filter("before_media_edit", locals())
    Media.query.filter(Media.id==media_id).update(dict(alt_text=alt_text, description=description))
    db.session.commit()
    plugins.do_event("after_media_edit", locals())
    return True


def edit_meta(media_id, name, value):
    data = plugins.do_filter("before_media_meta_edit", locals())
    MediaMeta.query.filter(MediaMeta.media_id==media_id, MediaMeta.name==name).update(dict(value=value))
    db.session.commit()
    plugins.do_event("after_media_meta_edit", locals())
    return True


def delete(media_id):
    plugins.do_event("before_media_delete", locals())
    media = Media.query.filter_by(id=media_id).first()
    if media:
        meta = get_meta(media_id)
        if 'location' in meta and meta['location'] == 's3':
            s3_handler = s3.S3()
            s3_handler.delete(media_id)
        else:
            file_path = path.join(
                current_app.config['UPLOAD_FOLDER'], "{}.{}".format(media.id, media.extension))
            if path.exists(file_path):
                remove(file_path)
        Media.query.filter_by(id=media_id).delete()
        db.session.commit()
        flash(gettext('Your media has been successfully deleted.'), 'success')
        plugins.do_event("after_media_delete", locals())
        return True
    else:
        abort(404)
