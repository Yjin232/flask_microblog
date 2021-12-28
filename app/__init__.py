from flask import Flask # import Flask lib

app = Flask(__name__)

#import routes module from app
from app import routes #import routes module from app

