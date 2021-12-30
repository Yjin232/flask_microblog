#Author: Yicheng Jin
#Date: 12/29/2021
from datetime import datetime,timedelta
import unittest
from app import app,db
from app.models import User,Post

class UserModelCase(unittest.TestCase):
    def setUp(self) -> None: #每次执行测试前先执行setUp
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' #创建一个和真实数据库一样的假数据库
        db.create_all()

    def tearDown(self) -> None: #每次测试完后清空session和清空数据库（不删除）
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self): #test password_hashing 固定格式test_xxx
        u = User(username='Jerry')
        u.set_password('cat')
        self.assertFalse(u.check_passwod('dog')) #assertFalse()判断括号内参数是否为False,若是False则通过，反之不通过
        self.assertTrue(u.check_passwod('cat')) #same as assertTrue

    def test_avatar(self): #test avatar
        u = User(username='Mike',email='mike@gamil.com')
        self.assertEqual(u.avatar(128),('https://www.gravatar.com/avatar/c9fe728f2cec4e0950611c886f274463?d=identicon&s=128'))

    def test_follow(self): #test follow and unfollow
        u1 = User(username='Hacker',email='hacker@gmail.com')
        u2 = User(username='Joker',email='joker@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(),[])
        self.assertEqual(u2.followers.all(),[]) #followers这个字段是在model中通过反向引用定义的

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(),1)
        self.assertEqual(u1.followed.first().username,'Joker')
        self.assertEqual(u2.followers.count(),1)
        self.assertEqual(u2.followers.first().username,'Hacker')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        #create four users
        u1 = User(username='john',email='john@gmail.com')
        u2 = User(username='mary',email='mary@gmail.com')
        u3 = User(username='tom',email='wom@gmail.com')
        u4 = User(username='west',email='west@gmail.com')

        #create four posts
        now = datetime.utcnow()
        p1 = Post(body='post form john',author=u1, timestamp=now+timedelta(seconds=1))
        p2 = Post(body='post form mary',author=u2, timestamp=now+timedelta(seconds=4))
        p3 = Post(body='post form tom',author=u3, timestamp=now+timedelta(seconds=3))
        p4 = Post(body='post form west',author=u4, timestamp=now+timedelta(seconds=2))
        db.session.add_all([p1,p2,p3,p4])
        db.session.commit()

        #set up the followers
        u1.follow(u2)#john follow mary
        u1.follow(u4)#john follow west
        u2.follow(u3)#mary follow tom
        u3.follow(u4)#tom follow west
        db.session.commit()

        #check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1,[p2,p4,p1]) #include john himself and mary and west
        self.assertEqual(f2,[p2,p3]) #include mary herself and tom
        self.assertEqual(f3,[p3,p4])
        self.assertEqual(f4,[p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)
