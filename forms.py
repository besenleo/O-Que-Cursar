from flask_security import ConfirmRegisterForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, HiddenField, SelectMultipleField
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms.validators import InputRequired, Length


class ExtendedRegisterForm(ConfirmRegisterForm):
    first_name = StringField('Nome', validators=[
        InputRequired(),
        Length(min=3, max=30)
    ])
    last_name = StringField('Sobrenome', validators=[
        InputRequired(),
        Length(min=3, max=30)
    ])

class ProfileForm(FlaskForm):
    first_name = StringField('Nome', validators=[
        InputRequired(),
        Length(min=3, max=30)
    ])
    last_name = StringField('Sobrenome', validators=[
        InputRequired(),
        Length(min=3, max=30)
    ])
    occupation = StringField('Ocupação', validators=[
        InputRequired(),
        Length(min=3, max=50)
    ])
    photo = FileField('Foto', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Imagens são permitidas em formato .jpg, .png e .jpeg'),
        FileSize(max_size=10485760)
    ])

class CourseForm(FlaskForm):
    name = StringField('Nome', validators=[
        InputRequired(),
        Length(min=3, max=50)
    ])
    description = TextAreaField('Descrição', validators=[
        InputRequired(),
        Length(max=1000)
    ])
    type = SelectField('Tipo do Curso', choices=[
        ('Graduação', 'Graduação'),
        ('Licenciatura', 'Licenciatura'),  
        ('Pós-Graduação', 'Pós-Graduação')], validators=[InputRequired()])


class PostForm(FlaskForm):
    content = TextAreaField('Conteudo', validators=[
        InputRequired(),
        Length(max=300)
    ])
    courses = SelectMultipleField('Cursos', validators=[InputRequired()])


class CommentForm(FlaskForm):
    content = TextAreaField('Comentario', validators=[
        InputRequired(),
        Length(max=300)
    ])
    post_id = HiddenField('Post_id', validators=[
        InputRequired()
    ])
 