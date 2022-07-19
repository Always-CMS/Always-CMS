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
    role_id = db.Column(GUID, db.ForeignKey('role.id'), nullable=False)
    mfa_hash = db.Column(db.String(50))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    meta = db.relationship("UserMeta", backref='user', cascade='all, delete, delete-orphan')
    role = db.relationship("Role", foreign_keys=[role_id])

class UserMeta(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(1000))
    value = db.Column(db.Text())
    

class Media(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(1000), unique=True)
    extension = db.Column(db.String(5))
    alt_text = db.Column(db.Text(), nullable=False, default='')
    description = db.Column(db.Text(), nullable=False, default='')
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


class Notification(db.Model):
    id = db.Column(GUID, primary_key=True, default=uuid.uuid4)
    object_type = db.Column(db.String(50))
    object_comment_id = db.Column(GUID, db.ForeignKey('comment.id'), nullable=True)
    object_user_id = db.Column(GUID, db.ForeignKey('user.id'), nullable=True)
    user_id = db.Column(GUID, db.ForeignKey('user.id'), nullable=True)
    ability_id = db.Column(GUID, db.ForeignKey('ability.id'), nullable=True)
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

    ability = db.relationship("Ability", foreign_keys=[ability_id])


def insert_default_models(*args, **kwargs):
    db.session.merge(Model(id='0267f036497a496db8ea4e048812a619', name='Default', slug='default'))
    db.session.commit()


def insert_default_types(*args, **kwargs):
    db.session.merge(Type(id='0afa7d706c9945299bbe334771924df1', name='Articles', slug='articles', description='Default post type'))
    db.session.commit()


def insert_default_menus(*args, **kwargs):
    db.session.merge(Menu(id='013cba4274c447b6ad7d8e1815b09440', name='Primary', location='primary'))
    db.session.commit()


def insert_default_abilities(*args, **kwargs):
    db.session.merge(Ability(id='e4e7b07446dc4d16b9f2036a4eb966f3', name='comments.edit'))
    db.session.merge(Ability(id='70a5aff1e4ae4844977278e7d4f85ae1', name='comments.list'))
    db.session.merge(Ability(id='1ee1d47275eb4f9f8086de176f6898f9', name='configuration'))
    db.session.merge(Ability(id='34ad1d3d08184085af4cb48b42fd8eb0', name='medias.edit'))
    db.session.merge(Ability(id='7fadeec875974bcdb3f367ae31954a0c', name='medias.list'))
    db.session.merge(Ability(id='969e0c103445471886c15f5eb8f52ea1', name='menus.edit'))
    db.session.merge(Ability(id='969e0c103445471886c15f5eb8f52eac', name='menus.list'))
    db.session.merge(Ability(id='54ad1d3d08184085af4cb48b42fd8eb0', name='pages.edit'))
    db.session.merge(Ability(id='9fadeec875974bcdb3f367ae31954a0c', name='pages.list'))
    db.session.merge(Ability(id='4c1de8a9c4814aedb073690df374f660', name='plugins.disable'))
    db.session.merge(Ability(id='54ad1d3d011840854f4cb48b42fd9eb0', name='plugins.edit'))
    db.session.merge(Ability(id='25514590678647fba8d380dee53b67da', name='plugins.enable'))
    db.session.merge(Ability(id='9fadeec475974bcdb3f362ae31954a1c', name='plugins.list'))
    db.session.merge(Ability(id='54ad1d3d08184085af4cb48b42fd9eb0', name='posts.edit'))
    db.session.merge(Ability(id='9fadeec875974bcdb3f367ae31954a1c', name='posts.list'))
    db.session.merge(Ability(id='c2fd2319e62e46cd98c4fafd912ef5e7', name='roles.edit'))
    db.session.merge(Ability(id='c2952f1411cd44bba128e811b32a2c5c', name='roles.list'))
    db.session.merge(Ability(id='1eb2b17462454d8ca81db454c7ec9a0d', name='terms.edit'))
    db.session.merge(Ability(id='27730be68d8e4632bf0c0e186c2a9bb5', name='terms.list'))
    db.session.merge(Ability(id='c6aa7f12182541d38fba5aee8826d7d7', name='themes.enable'))
    db.session.merge(Ability(id='a0b0040c1bf64d798d8bd4e6b5ad1514', name='themes.list'))
    db.session.merge(Ability(id='2757ff9b06724b78bc7320d3d86a5b75', name='types.edit'))
    db.session.merge(Ability(id='c57d21074ac24c31951312e5ca420a58', name='types.list'))
    db.session.merge(Ability(id='54ad1d3d01184085af4cb48b42fd9eb0', name='users.edit'))
    db.session.merge(Ability(id='9fadeec875974bcdb3f362ae31954a1c', name='users.list'))
    db.session.commit()


def insert_default_roles(*args, **kwargs):
    db.session.merge(Role(id='1ee1d47175eb4f9f8086de176f6898f9', role='Administrator'))
    db.session.commit()


def insert_default_roles_abilities(*args, **kwargs):
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='1eb2b17462454d8ca81db454c7ec9a0d'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='1ee1d47275eb4f9f8086de176f6898f9'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='25514590678647fba8d380dee53b67da'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='2757ff9b06724b78bc7320d3d86a5b75'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='27730be68d8e4632bf0c0e186c2a9bb5'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='34ad1d3d08184085af4cb48b42fd8eb0'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='4c1de8a9c4814aedb073690df374f660'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='54ad1d3d011840854f4cb48b42fd9eb0'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='54ad1d3d01184085af4cb48b42fd9eb0'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='54ad1d3d08184085af4cb48b42fd8eb0'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='54ad1d3d08184085af4cb48b42fd9eb0'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='70a5aff1e4ae4844977278e7d4f85ae1'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='7fadeec875974bcdb3f367ae31954a0c'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='969e0c103445471886c15f5eb8f52ea1'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='969e0c103445471886c15f5eb8f52eac'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='9fadeec475974bcdb3f362ae31954a1c'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='9fadeec875974bcdb3f362ae31954a1c'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='9fadeec875974bcdb3f367ae31954a0c'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='9fadeec875974bcdb3f367ae31954a1c'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='a0b0040c1bf64d798d8bd4e6b5ad1514'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='c2952f1411cd44bba128e811b32a2c5c'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='c2fd2319e62e46cd98c4fafd912ef5e7'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='c57d21074ac24c31951312e5ca420a58'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='c6aa7f12182541d38fba5aee8826d7d7'))
    db.session.merge(RoleAbility(role_id='1ee1d47175eb4f9f8086de176f6898f9', ability_id='e4e7b07446dc4d16b9f2036a4eb966f3'))
    db.session.commit()


def insert_default_configurations(*args, **kwargs):
    db.session.merge(Configuration(id='053a22b203b34dd8a91b8a8b60b95cc3', name='robots_txt', value='User-agent: *\r\nDisallow: /admin/'))
    db.session.merge(Configuration(id='071c34d70ffc414d9dbc525cf2a318ef', name='force_redirect_to_https', value='False'))
    db.session.merge(Configuration(id='29e429f577ce4251a88c6f839fae640f', name='default_users_role', value='1ee1d471-75eb-4f9f-8086-de176f6898f9'))
    db.session.merge(Configuration(id='2de0d0671bce46e3a5bf842a68a95b98', name='s3_bucket_name', value=''))
    db.session.merge(Configuration(id='4275cccd2ebf4ddaa70825a85b1f431d', name='mail_secure', value='False'))
    db.session.merge(Configuration(id='50da7778a1b448398912a5fdb4b4e7b2', name='comments_enabled', value='True'))
    db.session.merge(Configuration(id='61fd39464e1e4c0e98b76be07c1ab762', name='default_language', value='English'))
    db.session.merge(Configuration(id='7335f06b06f84c6093cfb04e7797d7e8', name='s3_endpoint_url', value=''))
    db.session.merge(Configuration(id='76c38a787bf6466ea054a2ebca658659', name='registration_confirmation', value='False'))
    db.session.merge(Configuration(id='8205ea04e09544ae8c3970957f2cf07d', name='s3_use_ssl', value='True'))
    db.session.merge(Configuration(id='98a9ef32cd01412b844117966b425f08', name='default_upload_location', value='local'))
    db.session.merge(Configuration(id='9ad94429cf234ee89ec2c4ab267866a8', name='translation', value='False'))
    db.session.merge(Configuration(id='a8bda406cf3b46dd8fb2effb342a0b61', name='comments_moderation', value='True'))
    db.session.merge(Configuration(id='d0bc53e05c194e54b6c6e180753ae705', name='s3_access_key_id', value=''))
    db.session.merge(Configuration(id='e4a93be83f87465f9b6f01740f1145a7', name='date_format', value='%B% %D%, %Y%'))
    db.session.merge(Configuration(id='ecaeae624c7f4683a142f5a0f99259d3', name='s3_secret_access_key', value=''))
    db.session.merge(Configuration(id='f57aca01100c49baa489e7d7f560ea07', name='mail_host', value='localhost'))
    db.session.merge(Configuration(id='f57aca01800c41baa489e7d7f560ea07', name='users_can_register', value='True'))
    db.session.merge(Configuration(id='f57aca01800c49baa482e7d7f560ea07', name='mail_port', value='25'))
    db.session.merge(Configuration(id='f57aca01800c49baa489e7d7f150ea07', name='mail_password', value=''))
    db.session.merge(Configuration(id='f57aca01800c49baa489e7d7f160ea07', name='mail_username', value=' '))
    db.session.merge(Configuration(id='f57aca01800c49baa489e7d7f560ea07', name='sitename', value='Always CMS'))
    db.session.merge(Configuration(id='f57aca01800c49baa489e7d7f560ea08', name='template', value='classic'))
    db.session.merge(Configuration(id='f57aca11800c41baa489e7d7f560ea07', name='minify_template', value='False'))
    db.session.merge(Configuration(id='f57acb01800c49baa489e7d7f560ea08', name='short_description', value='Powered with love by Always CMS.'))
    db.session.merge(Configuration(id='f7edf48800a2436089747b0b26b430f7', name='s3_region_name', value=''))
    db.session.commit()

def create_tables():
    """Create Tables and populate certain ones"""
    db.create_all()
    insert_default_models()
    insert_default_types()
    insert_default_menus()
    insert_default_abilities()
    insert_default_roles()
    insert_default_roles_abilities()
    insert_default_configurations()