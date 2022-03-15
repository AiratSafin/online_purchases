import cgi
import json
from flask import Flask, redirect, render_template, session, request

from add_purchases_form import AddPurchasesForm
from db import DB
from login_form import LoginForm
from purchases_model import PurchaseModel
from register_form import RegisterModel
from tovar_model import TovarModel
from tovars_content import content
from tovars_form import TovarsForm
from users_model import UsersModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
db_ = DB()
PurchaseModel(db_.get_connection()).init_table()
UsersModel(db_.get_connection()).init_table()

flag_perm = False

admins = json.loads(open('static/admins.txt', 'r', encoding='utf-8').read())

image = []

tovar_model = TovarModel(db_.get_connection())
for info in content:
    if not tovar_model.exists(info["title"], info["name"]):
        tovar_model.insert(info["img"], info["title"],
                           info["content"], info["year"], info["name"])


# http://127.0.0.1:8080/login

def make_session_permanent():
    session.permanent = False


@app.route('/login', methods=['GET', 'POST'])
def login():
    global flag_perm
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        perm = form.remember_me.data
        user_model = UsersModel(db_.get_connection())
        exists = user_model.exists(user_name, password)
        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
            if perm:
                session.permanent = True
                flag_perm = True
            else:
                session.permanent = False
                flag_perm = True
            return redirect("/index")
        else:
            return render_template('login.html', form=form, error=1)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/')
@app.route('/index/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        form = cgi.FieldStorage()
        if 'username' not in session or not flag_perm and not session.permanent:
            if "username" in session:
                return redirect("/logout")
            return redirect('/login')
        purchases = PurchaseModel(db_.get_connection()).get_all(session['user_id'])
        user_model = UsersModel(db_.get_connection())
        all_purchases = PurchaseModel(db_.get_connection()).get_all()
        all_users = user_model.get_all()
        if session['username'] in admins:
            return render_template('index.html', purchases=reversed(all_purchases),
                                   admins=admins, username=session['username'], all_users=all_users,
                                   adm_n=purchases)
        return render_template('index.html', username=session['username'], purchases=reversed(purchases), admins=admins)


@app.route('/site_users')
def site_users():
    if 'username' not in session:
        return redirect('/login')
    if session['username'] not in admins:
        return redirect('/')
    user_model = UsersModel(db_.get_connection())
    num = user_model.get_all()
    all_users = []
    for i in num:
        id = i[0]
        username = i[1]
        password = i[2]
        k = user_model.count(id)
        all_users.append((id, username, password, k))
    return render_template('site_users.html', users=all_users, admins=admins, username=session['username'])


@app.route('/add_purchases/<tovar>', methods=['GET', 'POST'])
def add_purchases(tovar):
    if tovar == "none":
        if 'username' not in session:
            return redirect('/login')
        form = AddPurchasesForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            phone=form.phone.data
            count=form.count.data
            nm = PurchaseModel(db_.get_connection())
            nm.insert("Без имени", title, content, session['user_id'],phone=phone,count=count)
            return redirect("/index")
        return render_template('add_purchases.html', title='Заявка на покупку', form=form,
                               username=session['username'], admins=admins, tovar="")
    else:
        if 'username' not in session:
            return redirect('/login')
        form = AddPurchasesForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            phone = form.phone.data
            count = form.count.data
            nm = PurchaseModel(db_.get_connection())
            nm.insert(tovar, title, content, session['user_id'],phone=phone,count=count)
            return redirect("/index")
        return render_template('add_purchases.html', title='ДЗаявка на покупку', form=form,
                               username=session['username'], admins=admins, tovar=tovar)


@app.route('/delete_purchases/<int:purchases_id>', methods=['GET'])
def delete_purchases(purchases_id):
    if 'username' not in session:
        return redirect('/login')
    nm = PurchaseModel(db_.get_connection())
    nm.delete(purchases_id)
    return redirect("/index")


@app.route('/delete_tovar/<int:tovar_id>', methods=['GET'])
def delete_tovar(tovar_id):
    if 'username' not in session:
        return redirect('/login')
    bm = TovarModel(db_.get_connection())
    bm.delete(tovar_id)
    return redirect("/all_tovars")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return redirect('/')
    form = RegisterModel()
    if form.validate_on_submit():
        user_name = form.user_name.data
        password = form.password.data
        user = UsersModel(db_.get_connection())
        flag = user.is_username_busy(user_name)
        if flag and user_name not in admins:
            user.insert(user_name, password)
            session['username'] = user_name
            exists = user.exists(user_name, password)
            session['user_id'] = exists[1]
            return redirect("/")
        else:
            return render_template('register.html', form=form, error=1)
    return render_template('register.html', form=form)


@app.route('/all_tovars')
def all_tovars():
    if session['username'] in admins:
        tovar_model = TovarModel(db_.get_connection())
        old_tovars = tovar_model.get_all()
        tovars = []
        for i in range(len(old_tovars)):
            if i % 2 == 0:
                if i != len(old_tovars) - 1:
                    tovars.append(old_tovars[i] + old_tovars[i + 1])
        return render_template('all_tovars.html', show=1, tovars=tovars, username=session["username"], admins=admins)
    else:
        tovar_model = TovarModel(db_.get_connection())
        old_tovars = tovar_model.get_all()
        tovars = []
        for i in range(len(old_tovars)):
            if i % 2 == 0:
                if i != len(old_tovars) - 1:
                    tovars.append(old_tovars[i] + old_tovars[i + 1])
        return render_template('all_tovars.html', tovars=tovars, username=session["username"], admins=admins)


@app.route('/upload')
def upload_files():
    if 'username' not in session:
        return redirect('/')
    return render_template('add_tovar_img.html', show=1)


@app.route('/add_tovar', methods=['POST', 'GET'])
def add_tovar():
    if 'username' not in session:
        return redirect('/')
    form = TovarsForm()
    image_name = image[-1]
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        year = form.year.data
        tovar = TovarModel(db_.get_connection())
        flag = tovar.is_title_busy(title)
        if not flag:
            tovar.insert(image_name, title, content, year, title)
            return redirect("/all_tovars")
        else:
            return render_template('add_tovar.html', form=form, error=1)
    return render_template('add_tovar.html', form=form)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        f = request.files['file']
        f.save("static/{}".format(f.filename))
        img_name = "/static/{}".format(f.filename)
        image.append(img_name)
        return redirect('/add_tovar')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
