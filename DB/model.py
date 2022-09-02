from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

login_manager = LoginManager()
db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key= True)
    nome = db.Column(db.String(30), nullable=False)
    sobrenome = db.Column(db.String(30), nullable= False)
    email = db.Column(db.String, nullable=False, unique=True)
    senha = db.Column(db.String(30), nullable=False)
    status_perfil = db.Column(db.Boolean, nullable=False, default=True)
    administrador = db.Column(db.Boolean, nullable=False, default=False)
    professor = db.Column(db.Boolean, nullable=False, default=False)
    token_sessao = db.Column(db.String(100), unique=True)

    posts = db.relationship('Post', backref='usuario', lazy='dynamic')
    comentarios = db.relationship('Comentario', backref='usuario', lazy='dynamic')

    def get_id(self):
        return self.token_sessao


class Curso(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(300), nullable=False)
    tipo_curso = db.Column(db.String(15), nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)

    posts = db.relationship('Post', backref='curso', lazy='dynamic')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    conteudo = db.Column(db.String(300), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False)
    id_curso = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    id_prof = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    comentarios = db.relationship('Comentario', backref='post', lazy='dynamic')


class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    conteudo = db.Column(db.String(280), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False)
    id_post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)



