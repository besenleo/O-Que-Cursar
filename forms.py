from flask_security import ConfirmRegisterForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
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

class CourseForm(FlaskForm):
    name = StringField('Nome', validators=[
        InputRequired(),
        Length(min=3, max=50)
    ])
    description = StringField('Descrição', validators=[
        InputRequired(),
        Length(max=300)
    ])
    type = SelectField('Tipo do Curso', choices=[
        ('Licenciatura', 'Licenciatura'), 
        ('Graduação', 'Graduação'), 
        ('Pós-Graduação', 'Pós-Graduação')], validators=[InputRequired()])


class PostForm(FlaskForm):
    content = StringField('Conteudo', validators=[
        InputRequired(),
        Length(max=300)
    ])
    #TODO: curso, Provavelmente um SelectField dinamico que passa o objeto do DB?

class CommentForm(FlaskForm):
    content = StringField('Conteudo', validators=[
        InputRequired(),
        Length(max=300)
    ])
 