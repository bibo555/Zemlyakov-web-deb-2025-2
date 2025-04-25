import random
from flask import Flask, render_template, request, make_response, abort, session, redirect, url_for, flash
from faker import Faker
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

fake = Faker()

app = Flask(__name__)
application = app
app.secret_key = 'os.urandom(24).hex()'  

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>')
def post(index):
    if index < 0 or index >= len(posts_list):
        abort(404)
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.route('/url_param')
def url_param():
    param= request.args
    return render_template('url_param.html', param=param, title='Параметры URL')

@app.route('/headers')
def show_headers():
    headers=dict(request.headers)
    return render_template('headers.html', headers=headers, title= 'Заголовки')

@app.route('/cookies')
def show_cookies():
    cookie_name='visits' 
    cookie_value=request.cookies.get(cookie_name)
    if cookie_value:
        response= make_response(render_template('cookies.html', action='deleted', cookies=request.cookies, title= 'Cookies'))
        response.delete_cookie(cookie_name)
    else:
        response= make_response(render_template('cookies.html', action='set', cookies=request.cookies, title= 'Cookies'))
        response.set_cookie(cookie_name, str(1), max_age=60*60*24*365*2)
    return response

@app.route('/form', methods=['GET', 'POST'])
def show_form():
    if request.method=='POST':
        form_data= request.form 
        return render_template('form.html', form_data=form_data, method= 'POST', title= 'Параметры формы')
    return render_template('/form.html', method='GET', title= 'Параметры формы') 

@app.route('/phone', methods= ['GET', 'POST'])
def show_phone():
    error=None
    phone= None
    formatted_phone= None

    if request.method=='POST':
        phone=request.form.get('phone', '').strip()
        error, formatted_phone=validate_phone(phone)

    return render_template('phone.html', phone=phone or '', error=error, formatted_phone=formatted_phone, title='Проверка телефона')

def validate_phone(phone):
    cleaned= ''.join(a for a in phone if a.isdigit() or a in '+()-.,')

    if any(a not in '+()-.,0123456789' for a in phone):
        return('Недопустимый ввод телефона', None)
    
    digits = ''.join(a for a in phone if a.isdigit())

    if phone.startswith(('+7', '8')):
        expected_lenght=11
    else:
        expected_lenght=10

    if len(digits)!=expected_lenght:
        return('Неверное количество цифр, ожидается {expected_lenght}, цифр', None)
    
    if expected_lenght==11:
        formatted=  f"8-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    else:
        formatted = f"8-{digits[0:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"

    return(None, formatted)

@app.route('/counter')
def counter():
    if 'counter' in session:
        session['counter'] += 1
    else:
        session['counter'] = 1
    
    return render_template('counter.html', visits=session['counter'])


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице"
login_manager.login_message_category = "info"


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id= id
        self.username= username
        self.password_hash= password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
users_db = {
    1: User(1, 'user', generate_password_hash('qwerty'))

}

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(int(user_id))


# Маршрут для входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        # Поиск пользователя
        user = next((u for u in users_db.values() if u.username == username), None)

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html', title='Вход')

# Маршрут для выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return users_db.get(int(user_id))

# Add secret page route
@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html', title='Секретная страница')
