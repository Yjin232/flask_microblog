#Author: Yicheng Jin
#Date: 12/28/2021
from app import app, db, cli
from app.models import User, Post
#shell上下文：进入flask.shell
@app.shell_context_processor
def make_shell_context():
    return {'db':db,'User':User,'Post':Post}

if __name__ == '__main__':

    app.run(debug=True)