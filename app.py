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
                return redirect(url_for('gerenciar_cursos'))
            except:
                db.session.rollback()
                flash('Falha ao adicionar curso', 'error')
                return redirect(url_for('gerenciar_cursos'))
        
        courses = Course.query.all()

        return render_template('gerenciar_cursos.html', current_user=current_user, form=form, courses=courses)

    @app.route('/editar_cursos/<course_id>', methods=['GET','POST'])
    @roles_required('admin')
    def editar_curso(course_id):
        course = Course.query.filter(Course.id == course_id).first()
        form = CourseForm(name=course.name, description=course.description, type=course.type)
        
        if form.validate_on_submit():
            try: 
                course.name = form.name.data
                course.description = form.description.data
                course.type = form.type.data
                db.session.commit()
                flash('Curso editado com sucesso!', 'success')
                return redirect(url_for('gerenciar_cursos'))
            except:
                db.session.rollback()
                flash('Falha ao editar curso', 'error')
                return redirect(url_for('gerenciar_cursos'))

        return render_template('editar_curso.html', current_user=current_user, form=form, course=course)

    @app.route('/excluir_cursos/<course_id>')
    @roles_required('admin')
    def excluir_curso(course_id):
        course = Course.query.filter(Course.id == course_id).first()
        try: 
            db.session.delete(course)
            db.session.commit()
            flash('Curso removido com sucesso!', 'success')
        except:
            db.session.rollback()
            flash('Falha ao remover curso', 'error')

        return redirect(url_for('gerenciar_cursos'))


    return app

