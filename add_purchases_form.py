from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField,IntegerField
from wtforms.validators import DataRequired


class AddPurchasesForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    phone=StringField('Телефон', validators=[DataRequired()])
    count = IntegerField('Количество', validators=[DataRequired()])
    content = TextAreaField('Пожелания', validators=[DataRequired()])
    submit = SubmitField('Добавить')
