from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, current_user, logout_user, fresh_login_required
from forms import LoginForm, RegistroForm, PostForm, ComentarioForm
from DB.model import db, login_manager, Usuario, Curso, Post, Comentario
from urllib.parse import urlparse, urljoin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

def is_safe_url(target):
    """
    Função para validar se URL que vai redicionar pós-login.
    Garante que a URL é segura.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and  ref_url.netloc == test_url.netloc

def create_app():
    # Criando e configurando Flask app
    app = Flask(__name__)
    app.config.from_pyfile('DB\config.cfg')
    
    # Passando o contexto do app para o LoginManager, SQLAlchemy e URLSafe
    login_manager.init_app(app)
    db.init_app(app)
    serializer = URLSafeTimedSerializer(app.secret_key)
   
    # Conectado User model e LoginManager
    @login_manager.user_loader
    def carregar_usuario(token_sessao):
        # coleta informação do usuario
        usuario = Usuario.query.filter_by(token_sessao=token_sessao).first()

        if usuario:
            try: 
                serializer.loads(token_sessao, max_age=app.config['TIME_TO_EXPIRE'])
            except:
                usuario.token_sessao = None
                db.session.commit()
                return None
        
        return usuario

    # Redirect para logins e fresh_logins
    login_manager.login_view = 'login'
    login_manager.login_message = 'Para acessar a página entre com seu usuario e senha'
    login_manager.refresh_view = 'login'
    login_manager.needs_refresh_message = 'Você precisa Entrar novamente para acessar a página'

    # Definindo routes do site
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/perfil')
    @login_required
    def perfil():
        return f'<h1> Olá, {current_user.nome} {current_user.sobrenome}</h1>' 

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
            lembre = request.form.get('lembre_de_mim')

            usuario = Usuario.query.filter(Usuario.email == email).first()
            
            if not usuario:
                return '<h1>Usuario não esta cadastrado<\h1>'

            if senha != usuario.senha:
                return '<h1>Senha ou usuario errado!<\h1>'
            
            # Muda o token da sessao toda vez que o usuario loga
            token_sessao = serializer.dumps([usuario.email, usuario.senha])
            usuario.token_sessao = token_sessao
            db.session.commit()

            login_user(usuario, remember=lembre)

            if 'next' in session and session['next']:
                if is_safe_url(session['next']): 
                    return redirect(session['next'])
            
            return redirect(url_for('index'))

        session['next'] = request.args.get('next')
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/registrar')
    def registrar():
        # TODO: Adicionar form e lembrar de criar uma token_sessao 
        usuario = Usuario(nome='Teste', sobrenome='teste', email='teste@email.com', senha='senha', 
                          token_sessao=serializer.dumps(['teste@email.com', 'senha']))
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('index'))
    
    @app.route('/trocar_senha')
    @fresh_login_required
    def trocar_senha():
        # TODO: Adicionar form e lembrar de criar uma nova token_sessao todo vez que trocar a senha
        return '<h1> So um exemplo de pagina que precisa de fresh login </h1>'

    return app

