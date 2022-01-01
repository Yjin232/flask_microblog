#Author: Yicheng Jin
#Date: 12/28/2021
from flask import Flask # import Flask lib
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
from flask import request
from flask_babel import lazy_gettext as _l
app = Flask(__name__)
#this command to relaize all the config
app.config.from_object(Config)

#init the database
db = SQLAlchemy(app) # Database object
migrate = Migrate(app,db) # Migrate object

#init the login object
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')

mail = Mail(app)
bootstrap = Bootstrap(app)
momoent = Moment(app)
babel = Babel(app)

#系统语言检测
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

#import routes module from app
from app import routes,models #import routes module from app
