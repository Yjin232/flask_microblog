from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin#在模型中混入类
from app import db,login
from datetime import datetime
from hashlib import md5


#flask_login要求配合代码
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#Flower and Flowed table, 需要在User表中声明多对多的关系
followers = db.Table(
    'followers',# table name
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), # follower column
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')) # followed column
)

#User table
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)

    #ch7 add followers and followed
    followed = db.relationship(
        'User',#自连接
        secondary=followers,#上面定义的粉丝和关注表
        primaryjoin=(followers.c.follower_id==id),
        secondaryjoin=(followers.c.followed_id==id),
        backref=db.backref('followers',lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_passwod(self,password):
        return check_password_hash(self.password_hash,password)

    #avatar function
    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        #外部头像网站
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest,size)

    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self,user):
        return self.followed.filter(followers.c.followed_id==user.id).count()>0

    #查询所有关注用户的所有posts
    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id==Post.user_id)).filter(
            followers.c.follower_id==self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())#union query

#Post table
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)