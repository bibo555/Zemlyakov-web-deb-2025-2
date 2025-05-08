import random
import os
from datetime import datetime
import re
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from faker import Faker
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, validators
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

fake = Faker()
app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(50))
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('Role', backref='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Forms
class UserForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message="Поле не может быть пустым"),
        Length(min=5, message="Логин должен содержать минимум 5 символов"),
        Regexp('^[a-zA-Z0-9]+$', message="Логин должен содержать только латинские буквы и цифры")
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Поле не может быть пустым")
    ])
    last_name = StringField('Фамилия')
    first_name = StringField('Имя', validators=[
        DataRequired(message="Поле не может быть пустым")
    ])
    middle_name = StringField('Отчество')
    role_id = SelectField('Роль', coerce=int)

    def validate_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов")
        if len(password) > 128:
            raise ValidationError("Пароль должен содержать максимум 128 символов")
        if not re.search(r'[A-ZА-Я]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r'[a-zа-я]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру")
        if re.search(r'\s', password):
            raise ValidationError("Пароль не должен содержать пробелы")
        if not re.fullmatch(r'[A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\'\.,:;]+', password):
            raise ValidationError("Пароль содержит недопустимые символы")

class EditUserForm(FlaskForm):
    last_name = StringField('Фамилия')
    first_name = StringField('Имя', validators=[
        DataRequired(message="Поле не может быть пустым")
    ])
    middle_name = StringField('Отчество')
    role_id = SelectField('Роль', coerce=int)

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[
        DataRequired(message="Поле не может быть пустым")
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message="Поле не может быть пустым")
    ])
    confirm_password = PasswordField('Повторите новый пароль', validators=[
        DataRequired(message="Поле не может быть пустым")
    ])

    def validate_new_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов")
        if len(password) > 128:
            raise ValidationError("Пароль должен содержать максимум 128 символов")
        if not re.search(r'[A-ZА-Я]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r'[a-zа-я]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру")
        if re.search(r'\s', password):
            raise ValidationError("Пароль не должен содержать пробелы")
        if not re.fullmatch(r'[A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+()\[\]{}><\/\\|"\'\.,:;]+', password):
            raise ValidationError("Пароль содержит недопустимые символы")

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize DB and create admin user
def initialize_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            admin_role = Role(name="admin", description="Администратор")
            polz_role =Role(name="polz", description="Пользователь")
            db.session.add(admin_role)
            db.session.add(polz_role)
            

            admin = User(
                username="admin",
                first_name="Admin",
                role_id=admin_role.id
            )
            admin.set_password("admin123")

            polz = User(
                username="polz",
                first_name="Artem",
                role_id=polz_role.id
            )
           
            polz.set_password("123")  
            db.session.add(admin)
            db.session.add(polz)
            db.session.commit()

initialize_db()

# Маршруты
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html', title='Вход')

@app.route('/users/<int:user_id>')

def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view_user.html', user=user)

@app.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    form = UserForm()
    form.role_id.choices = [(role.id, role.name) for role in Role.query.all()]  # Заполняем выбор ролей

    if request.method == 'POST' and form.validate():
        user = User(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            role_id=form.role_id.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь успешно создан!', 'success')
        return redirect(url_for('index'))

    return render_template('create_edit_user.html', form=form, is_edit=False)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    form.role_id.choices = [(role.id, role.name) for role in Role.query.all()]  # Заполняем выбор ролей

    if request.method == 'POST' and form.validate():
        form.populate_obj(user)  # Обновляем данные пользователя из формы
        db.session.commit()
        flash('Данные пользователя обновлены!', 'success')
        return redirect(url_for('view_user', user_id=user.id))

    return render_template('create_edit_user.html', form=form, is_edit=True)


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удален!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if request.method == 'POST' and form.validate():
        if not current_user.check_password(form.old_password.data):
            flash('Неверный старый пароль', 'danger')
        elif form.new_password.data != form.confirm_password.data:
            flash('Новые пароли не совпадают', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('index'))
    
    return render_template('change_password.html', form=form)

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html', title='Секретная страница')

# Добавьте остальные маршруты (create_user, edit_user, view_user, delete_user) по аналогии

