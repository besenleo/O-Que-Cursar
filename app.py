from datetime import datetime
from re import T
from flask import Flask, render_template, url_for, redirect, flash
from sqlalchemy import exists
from flask_mail import Mail
from flask_security import login_required, roles_required, current_user, \
                        SQLAlchemyUserDatastore, Security
from model import db, User, Role, Course, Post, Comment
from forms import ExtendedRegisterForm, CourseForm, PostForm, CommentForm
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    """"
    Creates Flask app
    """
    # Creating and configuring Flask app
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')       # Importing app configuration 
    app.config.from_pyfile('mail_config.cfg')  # Importing mail configuration
    
    # Giving app context to Flask-Mail
    mail = Mail()
    mail.init_app(app)

    db.init_app(app)          # Giving app context to SQLAlchemy
    migrate.init_app(app, db) # Giving app context to Flask-Migrate

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
    
    @app.route('/gerenciar_usuarios')
    @roles_required('admin')
    def gerenciar_usuarios():
        users = User.query.all()
        return render_template('gerenciar_usuarios.html', current_user=current_user, users=users)
    
    @app.route('/promover_usuario/<user_id>/<role>')
    @roles_required('admin')
    def promover_usuario(user_id, role):
        user = User.query.filter(User.id == user_id).first()
        db_role = user_datastore.find_role(role)

        if not db_role:
            flash(f'Permissão invalida!', 'error')
            return redirect(url_for('gerenciar_usuarios'))

        if not user.has_role(role):
            try:
                user_datastore.add_role_to_user(user=user, role=db_role)
                db.session.commit()
                flash(f'Usuario {user.email} promovido para {role}', 'success')
            except:
                db.session.rollback()
                flash(f'Não foi possivel adicionar permissão!')

        return redirect(url_for('gerenciar_usuarios'))

    @app.route('/rebaixar_usuario/<user_id>/<role>')
    @roles_required('admin')
    def rebaixar_usuario(user_id, role):
        user = User.query.filter(User.id == user_id).first()
        db_role = user_datastore.find_role(role)

        if not db_role:
            flash(f'Permissão invalida!', 'error')
            return redirect(url_for('gerenciar_usuarios'))

        if user.has_role(role):
            try:
                user_datastore.remove_role_from_user(user=user, role=db_role)
                db.session.commit()
                flash(f'Usuario {user.email} rebaixado de {role}', 'success')
            except:
                db.session.rollback()
                flash(f'Não foi possivel remover permissão!')

        return redirect(url_for('gerenciar_usuarios'))

    @app.route('/cursos')
    def cursos():
        courses = Course.query.all()
        return render_template('cursos.html', current_user=current_user, courses=courses)
    
    @app.route('/cursos/<course_name>', methods=['GET', 'POST'])
    def curso_home(course_name):
        # Instantiating forms 
        form_post = PostForm()
        form_comment = CommentForm()
        # Query objects on database to populate template
        course = Course.query.filter(Course.name == course_name).first()
        posts = Post.query.filter(Post.courses.any(Course.name == course_name))
        # Creating dynamic field for Post Form
        courses = Course.query.all()
        form_post.courses.choices = [(c.name, c.name) for c in courses]
        form_post.courses.data = [course.name] # Default selects course
        # Post form action
        if form_post.validate_on_submit():
            content = form_post.content.data
            courses_form = form_post.courses.data
            
            try: 
                post = Post(content=content, creation_date=datetime.now(), user = current_user)            
                # Adding the courses to post
                for course_form in courses_form:
                    for course in courses:
                        if course.name == course_form:
                            post.courses.append(course)
                db.session.add(post)
                db.session.commit()
                print(post.courses)
                flash('Post criado com sucesso!', 'success')
                return redirect(url_for('curso_home', course_name=course.name))
            except:
                db.session.rollback()
                flash(f'Falha ao criar post!', 'error')
                return redirect(url_for('curso_home', course_name=course.name))
        # Comment Form action
        if form_comment.validate_on_submit():
            content = form_comment.content.data
            post_id_form = form_comment.post_id.data
            
            try:
                # Querying database to check if post exists
                post_id = int(post_id_form)
                if 0 < Post.query.filter(Post.id == post_id).count() < 2:
                    comment = Comment(content=content, creation_date=datetime.now(), id_post=post_id)
                    # Adding author to comment
                    comment.user = current_user
                    db.session.add(comment)
                    db.session.commit()
                    return redirect(url_for('curso_home', course_name=course.name))
                else:
                    db.session.rollback()
                    flash('Falha ao fazer comentario!', 'error')
                    return redirect(url_for('curso_home', course_name=course.name))
            except:
                db.session.rollback()
                flash('Falha ao fazer comentario!', 'error')
                return redirect(url_for('curso_home', course_name=course.name))
        
        return render_template('curso_home.html', current_user=current_user, course=course, 
                                posts=posts, form_post=form_post, form_comment=form_comment)

    return app

