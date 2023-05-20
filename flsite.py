import sqlite3
import os
from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
from FDataBase import FDataBase

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdghj25fghjk78okjhgy66vgbjhbv'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

# menu = [{'name': 'Установка', 'url': 'install-flask'},
#         {'name': 'Первое приложение', 'url': 'first-app'},
#         {'name': 'Обратная связь', 'url': 'contact'}]


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


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
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/add_post', methods=['POST', 'GET'])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

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
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)

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
# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if 'userLogged' in session:
#         return redirect(url_for('profile', username=session['userLogged']))
#     elif request.method == 'POST' and request.form['username'] == 'doni' and request.form['password'] == '124':
#         session['userLogged'] = request.form['username']
#         return redirect(url_for('profile', username=session['userLogged']))
#
#     return render_template('login.html', title='Авторизация', menu=menu)
#
#
# @app.route('/profile/<username>')
# def profile(username):
#     if 'userLogged' not in session or session['userLogged'] != username:
#         abort(401)
#
#     return f'Профиль пользователя {username}'
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