from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_security import login_required, current_user, SQLAlchemyUserDatastore, Security
from models.model import db, User, Role, Course, Post, Comment
from forms import ExtendedRegisterForm

def create_app():
    """"
    Creates Flask app
    """
    # Creating and configuring Flask app
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')       # Importing app configuration 
    app.config.from_pyfile('mail_config.cfg')  # Importing mail configuration
    
    # # Giving app context to Flask-Mail
    mail = Mail()
    mail.init_app(app)

    db.init_app(app) # Giving app context to SQLAlchemy

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)        # Registring o User e Role model
    security = Security(app, user_datastore, 
                        confirm_register_form=ExtendedRegisterForm) # Instancing Flask-Security

    # Defining routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/perfil')
    @login_required
    def perfil():
        return f'<h1> Olá, {current_user.first_name} {current_user.last_name}</h1>' 

    return app

