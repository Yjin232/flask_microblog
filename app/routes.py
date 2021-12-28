#Author: Yicheng Jin
#Date: 12/28/2021

from app import app

@app.route('/')
@app.route('/index')

def index():
    return 'Hello, World!'