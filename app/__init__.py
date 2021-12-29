#Author: Yicheng Jin
#Date: 12/28/2021
from flask import Flask # import Flask lib
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
# print(app.config['SECRET_KEY'])

#import routes module from app
from app import routes #import routes module from app

