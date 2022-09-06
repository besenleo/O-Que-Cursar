from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

roles_users = db.Table('roles_users',
              db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
              db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    roles = db.relationship('Role', secondary=roles_users, 
                            backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='users', lazy='dynamic')
    comentarios = db.relationship('Comment', backref='users', lazy='dynamic')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    type = db.Column(db.String(15), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    posts = db.relationship('Post', backref='courses', lazy='dynamic')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    content = db.Column(db.String(300), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    id_course = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    id_mentor = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    comentarios = db.relationship('Comment', backref='posts', lazy='dynamic')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    content = db.Column(db.String(280), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    id_post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
