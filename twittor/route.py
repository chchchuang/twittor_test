from flask import render_template, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from twittor.forms import LoginForm, RegisterForm, EditProfileForm
from twittor.models import User, Tweet #要讓 flask知道 model存在
from twittor import db

@login_required
def index():
    posts = [
        {
            'author': {'username': 'root'},
            'body': "hi I'm root!"
        },
        {
            'author': {'username': 'test'},
            'body': "hi I'm test!"
        }
    ]
    return render_template("index.html", posts=posts)


def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first() #取第一個
        if u is None or not u.check_password(form.password.data):
            print("invalid username or password")
            return redirect(url_for('login'))
        login_user(u, remember=form.remember_me.data) #記錄登入用戶資訊
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template("login.html", title="Sign In", form=form)

def logout():
    logout_user()
    return redirect(url_for('login'))

def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html", title="Registeration", form=form)

@login_required
def user(username): #參數來自網址
    u = User.query.filter_by(username=username).first()
    if u is None:
        abort(404)
    posts = [
        {
            'author': {'username': u.username},
            'body': "hi I'm {}!".format(u.username)
        },
        {
            'author': {'username': u.username},
            'body': "hi I'm {}!".format(u.username)
        }
    ]
    if request.method == 'POST':
        # print(request.form.to_dict()) #key: submit.name, value: submit.value
        if request.form['request_button'] == 'Follow':
            current_user.follow(u)
            db.session.commit()
        else:
            current_user.unfollow(u)
            db.session.commit()
    return render_template("user.html", title="Profile", user=u, posts=posts)

def page_not_found(e):
    return render_template("404.html"), 404

@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.about_me.data = current_user.about_me
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username)) #url_for('endpoint')
    return render_template("edit_profile.html", form=form)
