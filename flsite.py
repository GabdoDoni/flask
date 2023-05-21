import sqlite3
import os
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdghj25fghjk78okjhgy66vgbjhbv'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа страницы'


@login_manager.user_loader
def load_user(user_id):
    print('load user')
    return UserLogin().fromDB(user_id, dbase)


# menu = [{'name': 'Установка', 'url': 'install-flask'},
#         {'name': 'Первое приложение', 'url': 'first-app'},
#         {'name': 'Обратная связь', 'url': 'contact'}]


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/add_post', methods=['POST', 'GET'])
def addPost():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка при добавлении статьи')
            else:
                flash('Статья добавлено')
        else:
            flash('Ошибка при добавлении статьи')

    return render_template('add_post.html', title='Создание статьи', menu=dbase.getMenu())


@app.route('/post/<alias>')
@login_required
def showPost(alias):
    title, text = dbase.getPost(alias)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=text)


#
#
# @app.route('/about')
# def about():
#     return render_template('about.html', title='О сайте', menu=menu)
#
#
# @app.route('/contact', methods=['POST', 'GET'])
# def contact():
#     if request.method == 'POST':
#         if len(request.form['username']) > 2:
#             flash('Сообщение отправлено')
#         else:
#             flash('Ошибка отправки')
#
#     return render_template('contact.html', title='Обратная связь', menu=menu)
#
#
@app.route('/login', methods=['POST', 'GET'])
def login():
    # if 'userLogged' in session:
    #     return redirect(url_for('profile', username=session['userLogged']))
    # elif request.method == 'POST' and request.form['username'] == 'doni' and request.form['password'] == '124':
    #     session['userLogged'] = request.form['username']
    #     return redirect(url_for('profile', username=session['userLogged']))
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['password'], request.form['password']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash('Неверно заполнены поля', 'error')

    return render_template('login.html', title='Авторизация', menu=dbase.getMenu())


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if len(request.form['username']) > 4 and len(request.form['email']) > 4  \
                 and len(request.form['password']) > 4 and request.form['password'] == request.form['password2']:
            hash = generate_password_hash(request.form['password'])
            res = dbase.addUser(request.form['username'], request.form['email'], hash)

            if res:
                flash('Новый пользователь успешно создан', 'success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка при добавлении в БД', 'error')
        else:
            flash('Неверно заполнены поля', 'error')

    return render_template('register.html', title='Регистрация', menu=dbase.getMenu())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    # if 'userLogged' not in session or session['userLogged'] != username:
    #     abort(401)
    #
    # return f'Профиль пользователя {username}'
    return f'''<p><a href="{url_for('logout')}">Выйти из профиля</a>
                <p>user info: {current_user.get_id()}'''
#
#
# @app.errorhandler(404)
# def pageerror(error):
#     return render_template('page404.html', title='Страница не найдено', menu=menu), 404


# @app.route('/profile/<path:username>')
# def profile(username):
#     return f'Пользователь: {username}'


# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('about'))
#     print(url_for('profile', username='doni'))

if __name__ == '__main__':
    app.run(debug=True)
