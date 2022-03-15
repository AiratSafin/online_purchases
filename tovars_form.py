from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired


class TovarsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Содержание", validators=[DataRequired()])
    year = StringField('Год выпуска', validators=[DataRequired()])
    submit = SubmitField('Добавить')
