from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[Email('Некоректный email')])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=4, max=10, message='Количество символов должен быть от 4 до 10')])
    remember = BooleanField('Запомнить', default=False)
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя: ', validators=[Length(min=4, max=10, message='Количество символов должен быть от 4 до 100')])
    email = StringField('Email: ', validators=[Email('Некоректный email')])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=4, max=10,
                                                                            message='Количество символов должен быть от 4 до 10')])
    password2 = PasswordField('Подвердите пароль: ', validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField('Регистрация')
