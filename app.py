from datetime import datetime
from flask import Flask, render_template, url_for, redirect, flash
from flask_mail import Mail
from flask_security import login_required, roles_required, roles_accepted, \
                        current_user, SQLAlchemyUserDatastore, Security
from model import db, User, Role, Course, Post, Comment
from forms import ExtendedRegisterForm, CourseForm, PostForm, CommentForm, ProfileForm
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES

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

    # Defining a upload set to handle pictures and videos
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    # Defining routes
    @app.route('/')
    def index():
        return render_template('index.html', current_user=current_user)

    #######################
    # User related routes #
    #######################    

    @app.route('/perfil', methods=['GET', 'POST'])
    @login_required
    def perfil():
        form = ProfileForm()

        if form.validate_on_submit():
            first_name = form.first_name.data
            last_name = form.last_name.data
            occupation = form.occupation.data
            profile_picture = form.photo.data
            change_counter = 0
            
            try:
                if profile_picture:
                    # TODO: remove old profile picture
                    image_filename = photos.save(profile_picture)
                    image_url = photos.url(image_filename)
                    current_user.profile_picture = image_url
                    change_counter += 1
                # Check if user changed their name on the form
                if current_user.first_name != first_name or current_user.last_name != last_name:
                    # Check if it is the user first time changing their name
                    if not current_user.name_change_at:
                        current_user.first_name = first_name
                        current_user.last_name = last_name
                        current_user.name_change_at = datetime.now()
                        change_counter += 1  
                    # Check if user changed their name on the last 90 days
                    elif (datetime.now() - current_user.name_change_at).days < 90:
                        flash('Você só pode trocar de nome 1 vez a cada 90 dias', 'info')
                    else:
                        current_user.first_name = first_name
                        current_user.last_name = last_name
                        current_user.name_change_at = datetime.now()
                        change_counter += 1  
                # Check if user changed their occupation on the form
                if current_user.occupation != occupation:
                    current_user.occupation = occupation
                    change_counter += 1
                # Check if any information was changed based on the previous form, then commits
                if change_counter > 0:
                    db.session.commit()
                    flash('Dados editado com sucesso!', 'success')
                else:
                    flash('Nenhum dado alterado', 'info')                                    
            except:
                db.session.rollback()
                flash('Falha ao editar dados', 'error')

        user_comments = Comment.query.filter(Comment.id_user == current_user.id)

        # Filling the form info
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.occupation.data = current_user.occupation
        
        return render_template('perfil.html', current_user=current_user, comments=user_comments, form=form)  

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
    
    @app.route('/deletar_conta/<user_id>')
    @login_required
    def deletar_conta(user_id):
        if current_user.has_role('admin') or current_user.id == user_id:
            try: 
                user = User.query.filter(User.id == user_id).first()
                db.session.delete(user)
                db.session.commit()
                flash('Usuario removido!', 'success')
            except:
                db.session.rollback()
                flash('Falha ao remover usuario', 'error')
        else:
            flash('Voce nao tem permissão para realizar essa operação!', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/desativar_conta/<user_id>')
    @roles_required('admin')
    def desativar_conta(user_id):
        try: 
            # Query and disable user
            user = User.query.filter(User.id == user_id).first()
            user.active = False
            # Query and delete all user's comments
            user_comments = Comment.query.filter(Comment.id_user == user.id).all()
            for comment in user_comments:
                db.session.delete(comment)
            # Query and delete all user's posts
            user_posts = Post.query.filter(Post.id_user == user.id).all()
            for post in user_posts:
                db.session.delete(post)
            # Commit changes to database
            db.session.commit()
            flash('Usuario desativado!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Falha ao desativadar usuario {e}', 'error')
        
        return redirect(url_for('index'))
    
    @app.route('/reativar_conta/<user_id>')
    @roles_required('admin')
    def reativar_conta(user_id):
        try: 
            # Query and disable user
            user = User.query.filter(User.id == user_id).first()
            user.active = True
            db.session.commit()
            flash('Usuario reativado!', 'success')
        except:
            db.session.rollback()
            flash('Falha ao reativar usuario', 'error')
        
        return redirect(url_for('index'))

    #########################
    # Course related routes #
    #########################

    @app.route('/cursos')
    def cursos():
        courses = Course.query.all()
        return render_template('cursos.html', current_user=current_user, courses=courses)
    
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

    #######################
    # Post related routes #
    #######################

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
        # Post form action
        if form_post.validate_on_submit():
            content = form_post.content.data
            courses_form = form_post.courses.data
            post_image = form_post.image.data
            
            try: 
                if post_image:
                    image_filename = photos.save(post_image)
                    image_url = photos.url(image_filename)
                    post = Post(content=content, creation_date=datetime.now(), user=current_user, image=image_url) 
                else:
                    post = Post(content=content, creation_date=datetime.now(), user=current_user)            
                # Adding the courses to post
                for course_form in courses_form:
                    for course in courses:
                        if course.name == course_form:
                            post.courses.append(course)
                db.session.add(post)
                db.session.commit()
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


    @app.route('/criar_post', methods=['GET', 'POST'])
    @roles_required('mentor')
    def criar_post():
        # Instantiating form 
        form = PostForm()
        # Creating dynamic field for Post Form
        courses = Course.query.all()
        form.courses.choices = [(c.name, c.name) for c in courses]
        # Post form action
        if form.validate_on_submit():
            content = form.content.data
            courses_form = form.courses.data
            post_image = form.image.data
            
            try: 
                if post_image:
                    image_filename = photos.save(post_image)
                    image_url = photos.url(image_filename)
                    post = Post(content=content, creation_date=datetime.now(), user=current_user, image=image_url) 
                else:
                    post = Post(content=content, creation_date=datetime.now(), user=current_user)           
                # Adding the courses to post
                for course_form in courses_form:
                    for course in courses:
                        if course.name == course_form:
                            post.courses.append(course)
                db.session.add(post)
                db.session.commit()
                flash('Post criado com sucesso!', 'success')
                return redirect(url_for('criar_post'))
            except:
                db.session.rollback()
                flash(f'Falha ao criar post!', 'error')
                return redirect(url_for('criar_post'))
        return render_template('criar_post.html', current_user=current_user, form=form)

    @app.route('/post/<post_id>', methods=['GET', 'POST'])
    @login_required
    def post(post_id):
        form = CommentForm()

        post_obj = Post.query.filter(Post.id == post_id).first()
        # Comment form action
        if form.validate_on_submit():
            content = form.content.data
            post_id_form = form.post_id.data
            
            try:
                # Querying database to check if post exists
                post_id_int = int(post_id_form)
                if 0 < Post.query.filter(Post.id == post_id_int).count() < 2:
                    comment = Comment(content=content, creation_date=datetime.now(), id_post=post_id_int)
                    # Adding author to comment
                    comment.user = current_user
                    db.session.add(comment)
                    db.session.commit()
                    return redirect(url_for('post', post_id=post_id_int))
                else:
                    db.session.rollback()
                    flash('Falha ao fazer comentario!', 'error')
                    return redirect(url_for('post', post_id=post_id_int))
            except:
                db.session.rollback()
                flash('Falha ao fazer comentario!', 'error')
                return redirect(url_for('post', post_id=post_id_int))
    
        return render_template('post.html', current_user=current_user, form=form, post=post_obj)
    
    @app.route('/meus_posts', methods=['GET', 'POST'])
    @roles_required('mentor')
    def meus_posts():
        form = CommentForm()
        posts = Post.query.filter(Post.user.has(User.id == current_user.id))
        # Comment form action
        if form.validate_on_submit():
            content = form.content.data
            post_id_form = form.post_id.data
            
            try:
                post_id = int(post_id_form)
                # Querying database to check if post exists
                if 0 < Post.query.filter(Post.id == post_id).count() < 2:
                    comment = Comment(content=content, creation_date=datetime.now(), id_post=post_id)
                    # Adding author to comment
                    comment.user = current_user
                    db.session.add(comment)
                    db.session.commit()
                    return redirect(url_for('meus_posts'))
                else:
                    db.session.rollback()
                    flash('Falha ao fazer comentario!', 'error')
                    return redirect(url_for('meus_posts'))
            except:
                db.session.rollback()
                flash('Falha ao fazer comentario!', 'error')
                return redirect(url_for('meus_posts'))

        return render_template('meus_posts.html', current_user=current_user, form=form, posts=posts)

    @app.route('/excluir_post/<post_id>')
    @roles_accepted('admin', 'mentor')
    def excluir_post(post_id):
        post = Post.query.filter(Post.id == post_id).first()

        if current_user.has_role('admin') or current_user.id == post.user.id:
            try: 
                db.session.delete(post)
                db.session.commit()
                flash('Post removido com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Falha ao remover post', 'error')
        else:
            flash('Voce não tem permissão para deletar esse post', 'error')
            
        return redirect(url_for('index'))
    
    @app.route('/excluir_comentario/<comment_id>')
    @roles_accepted('admin', 'mentor')
    def excluir_comentario(comment_id):
        comment = Comment.query.filter(Comment.id == comment_id).first()
        post = Post.query.filter(Post.id == comment.id_post).first()

        # Only the admin and post's creator can remove comments
        if current_user.has_role('admin') or current_user.id == post.user.id:
            try: 
                db.session.delete(comment)
                db.session.commit()
                flash('Comentario removido com sucesso!', 'success')
            except:
                db.session.rollback()
                flash('Falha ao remover comentario', 'error')
        else:
            flash('Voce não tem permissão para deletar esse comentario', 'error')
            
        return redirect(url_for('index'))

    return app
