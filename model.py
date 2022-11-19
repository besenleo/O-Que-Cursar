from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

roles_users = db.Table('roles_users',
              db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
              db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

posts_courses = db.Table('posts_courses',
                db.Column('post_id', db.Integer(), db.ForeignKey('post.id')),
                db.Column('course_id', db.Integer(), db.ForeignKey('course.id')))

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
    occupation = db.Column(db.String(50))
    name_change_at = db.Column(db.DateTime())
    profile_picture = db.Column(db.String(50))

    roles = db.relationship('Role', secondary=roles_users, 
                            backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', cascade='all, delete-orphan', back_populates='user')
    comments = db.relationship('Comment', cascade='all, delete-orphan', back_populates='user')


class Course(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(15), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    posts = db.relationship('Post', secondary=posts_courses, cascade='all, delete', back_populates='courses')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    content = db.Column(db.String(300), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    image = db.Column(db.String(50))
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    courses = db.relationship('Course', secondary=posts_courses, back_populates='posts')
    comments = db.relationship('Comment', cascade='all, delete-orphan', backref='posts', lazy='dynamic')
    user = db.relationship('User', back_populates='posts')
    


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    content = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    id_post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', back_populates='comments')
