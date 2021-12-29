#Author: Yicheng Jin
#Date: 12/28/2021
from flask import Flask # import Flask lib
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
#this command to relaize all the config
app.config.from_object(Config)

#init the database
db = SQLAlchemy(app) # Database object
migrate = Migrate(app,db) # Migrate object

#import routes module from app
from app import routes,models #import routes module from app

