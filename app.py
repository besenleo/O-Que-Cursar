from email import message
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_security import login_required, roles_required, current_user, \
                        SQLAlchemyUserDatastore, Security
from models.model import db, User, Role, Course, Post, Comment
from forms import ExtendedRegisterForm, CourseForm

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
        return render_template('index.html', current_user=current_user)
    
    @app.route('/perfil')
    @login_required
    def perfil():
        return render_template('perfil.html', current_user=current_user) 

    @app.route('/gerenciar_cursos', methods=['GET', 'POST'])
    @roles_required('admin')
    def gerenciar_cursos():
        form = CourseForm()
        
        if form.validate_on_submit():
            nome = form.name.data
            descricao = form.description.data
            tipo = form.type.data

            course = Course(name=nome, description=descricao, type=tipo)

            try: 
                db.session.add(course)
                db.session.commit()
                flash('Curso adicionado com sucesso!', 'success')
            except:
                flash('Não foi possivel adicionado com sucesso!', 'error')\
        
        courses = Course.query.all()

        return render_template('gerenciar_cursos.html', current_user=current_user, form=form, courses=courses)

    return app

