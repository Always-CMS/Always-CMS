# -*- coding: utf-8 -*-

import uuid
from flask_login import UserMixin
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from always_cms.app import db


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)

        if not isinstance(value, uuid.UUID):
            return "%.32x" % uuid.UUID(value).int
        # hexstring
        return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)


class Configuration(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(1000))
    value = db.Column(db.Text())


class Role(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    role = db.Column(db.String(50), unique=True)


class Ability(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(50), unique=True)


class RoleAbility(db.Model):
    __tablename__ = 'role_ability'
    role_id = db.Column(GUID, db.ForeignKey('role.id'),
                        primary_key=True, nullable=False)
    ability_id = db.Column(GUID, db.ForeignKey(
        'ability.id'), primary_key=True, nullable=False)

    role = db.relationship("Role", foreign_keys=[role_id])
    ability = db.relationship("Ability", foreign_keys=[ability_id])


class User(UserMixin, db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    role = db.Column(db.String(50))
    mfa_hash = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    meta = db.relationship("UserMeta", backref='user', cascade='all, delete, delete-orphan')


class UserMeta(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(1000))
    value = db.Column(db.Text())
    

class Media(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(1000), unique=True)
    extension = db.Column(db.String(5))
    alt_text = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    meta = db.relationship("MediaMeta", back_populates='media', cascade='delete, merge, save-update')


class MediaMeta(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    media_id = db.Column(GUID, db.ForeignKey('media.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(1000))
    value = db.Column(db.Text())
    media = db.relationship("Media", back_populates="meta")


class Post(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    permalink = db.Column(db.String(2000), unique=True)
    type_id = db.Column(GUID, db.ForeignKey('type.id'), nullable=False)
    model_id = db.Column(GUID, db.ForeignKey('model.id'), nullable=False)
    title = db.Column(db.String(1000))
    body = db.Column(db.Text())
    description = db.Column(db.Text())
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    published_at = db.Column(db.DateTime(timezone=True))
    author_id = db.Column(GUID, db.ForeignKey('user.id'), nullable=False)

    term = db.relationship("PostTerm", back_populates='post')
    type = db.relationship("Type", foreign_keys=[type_id])
    model = db.relationship("Model", foreign_keys=[model_id])
    author = db.relationship("User", foreign_keys=[author_id])


class Page(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    permalink = db.Column(db.String(2000), unique=True)
    title = db.Column(db.String(1000))
    body = db.Column(db.Text())
    description = db.Column(db.Text())
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    published_at = db.Column(db.DateTime(timezone=True))
    author_id = db.Column(GUID, db.ForeignKey('user.id'), nullable=False)

    author = db.relationship("User", foreign_keys=[author_id])


class Type(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200))
    slug = db.Column(db.String(200))
    description = db.Column(db.Text())


class Term(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    classification = db.Column(db.String(50))
    name = db.Column(db.String(200))
    slug = db.Column(db.String(200))
    description = db.Column(db.Text())

    post = db.relationship("PostTerm", back_populates='term')


class PostTerm(db.Model):
    __tablename__ = 'post_term'
    post_id = db.Column(GUID, db.ForeignKey('post.id'),
                        primary_key=True, nullable=False)
    term_id = db.Column(GUID, db.ForeignKey('term.id'),
                        primary_key=True, nullable=False)

    post = db.relationship("Post", foreign_keys=[post_id])
    term = db.relationship("Term", foreign_keys=[term_id])


class Model(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200))
    slug = db.Column(db.String(200))


class Comment(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    post_id = db.Column(GUID, db.ForeignKey('post.id'), nullable=False)
    status = db.Column(db.String(200))
    content = db.Column(db.Text())
    user_id = db.Column(GUID, db.ForeignKey('user.id'), nullable=True)
    author = db.Column(db.String(200))
    author_email = db.Column(db.String(200))
    author_ip = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    parent_id = db.Column(GUID, db.ForeignKey('comment.id'), nullable=True)

    post = db.relationship("Post", foreign_keys=[post_id])
    user = db.relationship("User", foreign_keys=[user_id])
    parent = db.relationship("Comment", foreign_keys=[parent_id])


class Menu(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200))
    location = db.Column(db.String(200))


class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(200))
    link = db.Column(db.String(255))
    target = db.Column(db.String(200))
    menu_id = db.Column(GUID, db.ForeignKey('menu.id'), nullable=True)
    parent_id = db.Column(GUID, db.ForeignKey('menu_item.id'), nullable=True)
    
    menu = db.relationship("Menu", foreign_keys=[menu_id])
    child = db.relationship("MenuItem", foreign_keys=[parent_id], cascade='all, delete')
