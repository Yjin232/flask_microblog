#Author: Yicheng Jin
#Date: 12/28/2021
from datetime import datetime

from flask import request, render_template, redirect, flash, url_for
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPsswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.email import send_password_reset_email

#record the route time
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

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

#user info route
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author':user,'body':'Test post #1'},
        {'author':user,'body':'Test post #2'}
    ]
    return render_template('user.html',user=user,posts=posts)

@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Edited succeed')
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html',title='Edit Profile',form=form)


#follow route
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not exists.'.format(username))
        return redirect(url_for('user',username=username))
    if user == current_user:
        flash('You can not follow yourself!')
        return redirect(url_for('user',username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Following {} succeed!'.format(username))
    return redirect(url_for('user',username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not exists.'.format(username))
        return redirect(url_for('user', username=username))
    if user == current_user:
        flash('You can not unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Unfollowing {} succeed!'.format(username))
    return redirect(url_for('user', username=username))

#reset password request route
@app.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPsswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',title='Reset Password',form=form)

#reset password route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)




#MAIL_PASSWORD='irkq ongd bzge ebeh'
