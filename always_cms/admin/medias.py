# -*- coding: utf-8 -*-

from os import path

from flask_login import login_required
from flask import render_template, redirect, url_for, request, current_app

from always_cms.libs.medias.pillow import load_image, dupe_image, get_default_slider, apply_enhancers, apply_hue_shift, get_dominant_colors
from always_cms.libs.medias.pillow import apply_blur, apply_sharpen, apply_edge_enhance, apply_smooth
from always_cms.libs.medias.pillow import get_image_size, rotate_image, resize_image, crop_image

from always_cms.libs import medias
from always_cms.libs.roles import require_permission
from always_cms.app import csrf

from .routes import admin


@admin.route('/admin/medias')
@login_required
@require_permission('medias.list')
def medias_list():
    editor = request.args.get('CKEditor')
    return render_template('medias.html', title_page="Medias", medias=medias.get_all(), editor=editor)


@admin.route('/admin/medias', methods=['POST'])
@login_required
@require_permission('medias.edit')
def uploads():
    return medias.add()


@admin.route('/admin/medias/edit/<media_id>')
@login_required
@require_permission('medias.edit')
def medias_edit(media_id):
    medias.init_media_edit(media_id)
    media = medias.get(media_id)
    media_path = path.join(current_app.config['UPLOAD_FOLDER'], "{}-work.{}".format(media.id, media.extension))
    
    image = load_image(media_path)
    slider = get_default_slider()
    width, height = get_image_size(image)
    colors = get_dominant_colors(media_path)

    return render_template('edit-media.html', title_page="Medias", media=medias.get(media_id), slider=slider, width=width, height=height, colors=colors)


@admin.route('/admin/medias/edit/<media_id>', methods=['POST'])
@login_required
@require_permission('medias.edit')
def medias_edit_post(media_id):
    media = medias.get(media_id)

    media_path = path.join(current_app.config['UPLOAD_FOLDER'], "{}-work.{}".format(media.id, media.extension))

    image = load_image(media_path)
    slider = get_default_slider()
    width, height = get_image_size(image)
    colors = get_dominant_colors(media_path)

    if request.form.get('edit') == "values":
        alt_text = request.form.get('alt_text')
        description = request.form.get('description')
        medias.edit(media_id, alt_text, description)
    elif request.form.get('edit') == "reload_source":
        medias.init_media_edit(media_id, force=True)
    elif request.form.get('edit') == "replace_original":
        medias.replace_original(media_id)
    elif request.form.get('edit') == "enhance":
        slider['color'] = float(request.form.get('color'))
        slider['bright'] = float(request.form.get('bright'))
        slider['contrast'] = float(request.form.get('contrast'))
        slider['sharp'] = float(request.form.get('sharp'))
        apply_enhancers(image, media_path, slider)
    elif request.form.get('edit') == "hue":
        hue_angle = float(request.form.get('hue_angle'))
        apply_hue_shift(media_path, hue_angle)

    if request.form.get('blur_button'):
        apply_blur(media_path, request.form.get('blur_button'))
    elif request.form.get('sharpen_button'):
        apply_sharpen(media_path, request.form.get('sharpen_button'))
    elif request.form.get('edge_button'):
        apply_edge_enhance(media_path, request.form.get('edge_button'))
    elif request.form.get('smooth_button'):
        apply_smooth(media_path, request.form.get('smooth_button'))
    elif request.form.get('rotate_button'):
        angle = int(request.form.get('angle'))
        rotate_image(media_path, angle)
    elif request.form.get('resize_button'):
        n_width = int(request.form.get('width'))
        n_height = int(request.form.get('height'))
        resize_image(media_path, n_width, n_height)
    elif request.form.get('crop_button'):
        start_x = int(request.form.get('start_x'))
        start_y = int(request.form.get('start_y'))
        end_x = int(request.form.get('end_x'))
        end_y = int(request.form.get('end_y'))
        crop_image(media_path, start_x, start_y, end_x, end_y)

    return redirect(url_for('admin.medias_edit', media_id=media_id))


@admin.route('/admin/medias/delete/<media_id>')
@login_required
@require_permission('medias.edit')
def medias_delete(media_id):
    medias.delete(media_id)
    return redirect(url_for('admin.medias_list'))
