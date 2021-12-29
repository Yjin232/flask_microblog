#Author: Yicheng Jin
#Date: 12/28/2021
from flask import request, render_template, redirect, flash, url_for
from app import app
from app.forms import LoginForm

#index routes
@app.route('/')
@app.route('/index')

def index():
    #add user info
    user = {'username':'Yicheng'}
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

    return render_template('index.html',title='Home',user=user,posts=posts)

#login routes
@app.route('/login',methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash('Login requestd for user {}, remember_me={}'.format(login_form.username.data,login_form.remember_me.data))
        return redirect(url_for('index'))


    return render_template('login.html',form=login_form,title='Login')