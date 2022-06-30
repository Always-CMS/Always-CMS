# -*- coding: utf-8 -*-

from flask_login import current_user
from flask import flash, abort
from flask_babel import gettext
from slugify import slugify
from sqlalchemy.sql import func

from always_cms.libs import plugins
from always_cms.app import db
from always_cms.models import Post, PostTerm, Type


def get_schedule(schedule, status):
    if status == 'publish':
        if not schedule:
            schedule = func.now()
    else:
        schedule = db.null()
    return schedule


def get_all():
    return Post.query.all()


def get_all_by_type_slug(type_slug):
    get_type = Type.query.filter_by(slug=type_slug).first()
    return Post.query.filter_by(type_id=get_type.id).all()


def get(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        return post
    else:
        abort(404)


def add(title, body, description, status, categories, tags, type_id, model_id, schedule=None):

    data = locals()
    data['permalink'] = slugify(data['title'])

    data = plugins.do_filter("before_post_add", data)

    if not data['title']:
        flash(gettext('This title is empty. Please change title.'), 'warning')
    elif Post.query.filter_by(permalink=data['permalink']).first():
        flash(gettext('This permalink is already in use. Please change title.'), 'warning')
    elif status not in ['draft', 'private', 'publish']:
        flash(gettext('This status is not accepted.'), 'warning')
    else:
        data['schedule'] = get_schedule(data['schedule'], data['status'])

        new_post = Post(permalink=data['permalink'],
                        title=data['title'],
                        body=data['body'],
                        description=data['description'],
                        status=data['status'],
                        type_id=data['type_id'],
                        model_id=data['model_id'],
                        published_at=data['schedule'],
                        author_id=current_user.id
                        )

        # add the new post to the database
        db.session.add(new_post)
        db.session.commit()

        if data['categories'] is not None:
            for category in data['categories']:
                new_term = PostTerm(post_id=new_post.id, term_id=category)
                db.session.add(new_term)

        if data['tags'] is not None:
            for tag in data['tags']:
                new_term = PostTerm(post_id=new_post.id, term_id=tag)
                db.session.add(new_term)

        db.session.commit()
        plugins.do_event("after_post_add", new_post)
        flash(gettext('Your post has been successfully created.'), 'success')
        return new_post
    return False


def edit(post_id, title, body, description, status, categories, tags, type_id, model_id, schedule=None):
    data = locals()
    data['permalink'] = slugify(data['title'])

    data = plugins.do_filter("before_post_edit", data)

    get_post = Post.query.filter_by(permalink=data['permalink']).first()

    if not data['title']:
        flash(gettext('This title is empty. Please change title.'), 'warning')
    elif get_post is not None and str(get_post.id) != data['post_id']:
        flash(gettext('This permalink is already in use. Please change title.'), 'warning')
    else:
        data['schedule'] = get_schedule(data['schedule'], data['status'])
        
        Post.query.filter_by(id=data['post_id']).update(dict(permalink=data['permalink'],
                                                             title=data['title'],
                                                             body=data['body'],
                                                             description=data['description'],
                                                             status=data['status'],
                                                             type_id=data['type_id'],
                                                             model_id=data['model_id'],
                                                             published_at=data['schedule']
                                                             ))

        PostTerm.query.filter_by(post_id=post_id).delete()

        db.session.commit()

        if categories is not None:
            for category in data['categories']:
                new_term = PostTerm(post_id=post_id, term_id=category)
                db.session.add(new_term)

        if tags is not None:
            for tag in data['tags']:
                new_term = PostTerm(post_id=post_id, term_id=tag)
                db.session.add(new_term)

        db.session.commit()
        plugins.do_event("after_post_edit", locals())
        flash(gettext('Your post has been successfully edited.'), 'success')
        return True
    return False


def delete(post_id):
    plugins.do_event("before_post_delete", locals())
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()
    flash(gettext('Your post has been successfully deleted.'), 'success')
    plugins.do_event("after_post_delete", locals())


def count(type=None, status=None):
    if type is None and status is None:
        return Post.query.count()
    elif type is None and status is not None:
        return Post.query.filter_by(status=status).count()
    elif type is not None and status is None:
        return Post.query.filter_by(type=type).count()
    return Post.query.filter(Post.type==type, Post.status==status).count()
