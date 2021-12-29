#Author: Yicheng Jin
#Date: 12/28/2021
from flask import request, render_template, redirect, flash, url_for
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
#index routes
@app.route('/')
@app.route('/index')
@login_required # set index page needs login


def index():
    #add user info
    # user = {'username':'Yicheng'}
    #add user post,list type
    posts = [
        {
            'author': {'username': 'Mike'},
            'body': 'Beautiful day in Seattle!'
         },
        {
            'author': {'username': 'Anna'},
            'body': 'Beautiful day in Las Vegas!'
        }
    ]

    return render_template('index.html',title='Home',posts=posts)

#login routes
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():

        user = User.query.filter_by(username=login_form.username.data).first()
        if user is None or not user.check_passwod(login_form.password.data):
            flash('invalid username or password')

        login_user(user,login_form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')#If there is no next page, redirect to index page
        return redirect(next_page)


        return redirect(url_for('index'))



    return render_template('login.html',form=login_form,title='Login')

#logout route
@app.route('/logout')
def logout():
    logout_user()#clean the session
    return redirect(url_for('index'))

#register route
@app.route('/register',methods=['POST','GET'])
def register():
    if current_user.is_authenticated:#if curr already registered, return to index page
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #这里除了会调用表单中DataRequired这些定义的校验函数，也会调用自定义的 validate_字段名() 的校验函数，全部通过返回True
        #add new user into database
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Cong, Registration Succeed!')
        return redirect(url_for('login'))
    return render_template('register.html',title='Registration',form=form)

