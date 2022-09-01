from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from DB.model import db, Usuario, Curso, Post, Comentario

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('DB\config.cfg')
    db.init_app(app)

    @app.route('/')
    def index():
        t = Usuario.query.filter(Usuario.nome == 'admin').first()
        return f"<h1>Funcionou: {t.nome} <h1>"

    return app

