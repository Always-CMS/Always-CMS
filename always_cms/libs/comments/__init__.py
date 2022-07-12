# -*- coding: utf-8 -*-

from flask import flash

from always_cms.libs import configurations, plugins
from always_cms.app import db
from always_cms.models import Comment


def get_all():
    return Comment.query.all()


def get(comment_id):
    return Comment.query.filter_by(id=comment_id).first()


def get_by_post(post_id, status='approved'):
    if status.lower() == 'all':
        return Comment.query.filter_by(post_id=post_id).all()
    else:
        return Comment.query.filter_by(post_id=post_id, status=status).all()


def add(content, post_id, parent_id=None, user_id=None, author=None, author_email=None, author_ip=None):

    data = plugins.do_filter("before_comment_add", locals())

    if configurations.get('comments_enabled') == "False":
        flash('You cannot post comments because they are disabled.', 'warning')
        return False
    if not content:
        flash('This comment is invalid. Please modify the content.', 'warning')
        return False
    if not post_id:
        flash('A comment must be linked to a post. Please define a post.', 'warning')
        return False
    if not user_id or (not author or not author_email):
        flash('You cannot post a comment without an author.', 'warning')
        return False

    if configurations.get('comments_moderation') == "True":
        status = "pending"
    else:
        status = "approved"

    new_comment = Comment(post_id=data['post_id'],
                          status=data['status'],
                          user_id=data['user_id'],
                          author=data['author'],
                          author_email=data['author_email'],
                          author_ip=data['author_ip'],
                          parent_id=data['parent_id'])

    db.session.add(new_comment)
    db.session.commit()

    plugins.do_event("after_comment_add", new_comment)

    return new_comment


def change_user_id(comment_id = None, source_user_id = None, destination_user_id = db.null() ):
    if comment_id is None:
        Comment.query.filter_by(
            user_id=source_user_id).update(dict(user_id=destination_user_id))
    else:
        if source_user_id is None:
            Comment.query.filter_by(
                id=comment_id).update(dict(user_id=destination_user_id))
        else:
            Comment.query.filter(
                Comment.id==comment_id, Comment.user_id==source_user_id).update(dict(user_id=destination_user_id))
        
    db.session.commit()
    


def delete(comment_id):
    plugins.do_event("before_comment_delete", locals())
    Comment.query.filter_by(id=comment_id).delete()
    db.session.commit()
    plugins.do_event("after_comment_delete", locals())
    return True


def approval(comment_id):
    plugins.do_event("before_comment_approval", locals())
    Comment.query.filter_by(
        id=comment_id).update(dict(status="approved"))
    db.session.commit()
    flash('The comment has been approved.', 'success')
    plugins.do_event("after_comment_approval", locals())
    return True


def rejected(comment_id):
    plugins.do_event("before_comment_rejected", locals())
    Comment.query.filter_by(
        id=comment_id).update(dict(status="rejected"))
    db.session.commit()
    flash('The comment has been rejected.', 'success')
    plugins.do_event("after_comment_rejected", locals())
    return True


def count(status=None):
    if status is None:
        return Comment.query.count()
    return Comment.query.filter_by(status=status).count()
