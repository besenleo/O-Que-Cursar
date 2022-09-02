from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField('email', validators=[
        InputRequired(),
        Email()
    ])
    senha = PasswordField('senha', validators=[
        InputRequired(),
        Length(max=30)
    ])


class RegistroForm(FlaskForm):
    nome = StringField('nome', validators=[
        InputRequired(),
        Length(min=3, max=30)
    ])
    sobrenome = StringField('nome', validators=[
        InputRequired(),
        Length(min=3, max=30)
    ])
    email = StringField('email', validators=[
        InputRequired(),
        Email()
    ])
    senha = PasswordField('senha', validators=[
        InputRequired(),
        Length(min=8, max=30)
    ])


class CursoForm(FlaskForm):
    nome = StringField('nome', validators=[
        InputRequired(),
        Length(min=3, max=50)
    ])
    descricao = StringField('nome', validators=[
        InputRequired(),
        Length(max=300)
    ])
    tipo_curso = SelectField('Programming Language', choices=[
        ('Licenciatura', 'Licenciatura'), 
        ('Graduação', 'Graduação'), 
        ('Pós-Graduação', 'Pós-Graduação')], validators=[InputRequired()])


class PostForm(FlaskForm):
    conteudo = StringField('nome', validators=[
        InputRequired(),
        Length(max=300)
    ])
    #TODO: curso, Provavelmente um SelectField dinamico que passa o objeto do DB?

class ComentarioForm(FlaskForm):
    conteudo = StringField('nome', validators=[
        InputRequired(),
        Length(max=300)
    ])
 