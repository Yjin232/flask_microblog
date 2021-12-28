#Author: Yicheng Jin
#Date: 12/28/2021
from flask import request,render_template,redirect
from app import app

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
