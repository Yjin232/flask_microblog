#Author: Yicheng Jin
#Date: 12/28/2021
from datetime import datetime

from flask import request, render_template, redirect, flash, url_for, jsonify
from guess_language import guess_language
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPsswordRequestForm, ResetPasswordForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from app.email import send_password_reset_email
from flask_babel import _

#record the route time
from app.translate import translate


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#index routes
@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
@login_required # set index page needs login
def index():
    form = PostForm()
    if form.validate_on_submit():
        #新增检测语言功能
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) >5:
            language = ''
        post = Post(body=form.post.data,author=current_user,language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    #改成分页形式
    page = request.args.get('page',1,type=int)
    posts = current_user.followed_posts().paginate(page,app.config['POSTS_PER_PAGE'], False)
    #上一页和下一页
    next_url = url_for('index',page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index',page=posts.prev_num) if posts.has_prev else None

    # posts = current_user.followed_posts().all()

    return render_template('index.html',title='Home',posts=posts.items,form=form, next_url=next_url,prev_url=prev_url)

#login routes
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    login_form = LoginForm()

    if login_form.validate_on_submit():

        user = User.query.filter_by(username=login_form.username.data).first()
        if user is None or not user.check_passwod(login_form.password.data):
            flash(_('invalid username or password'))

        login_user(user,login_form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')#If there is no next page, redirect to index page
        return redirect(next_page)


        return redirect(url_for('index'))



    return render_template('login.html',form=login_form,title='Login')

#logout route
@app.route('/logout')
def logout():
    logout_user()#clean the session
    return redirect(url_for('index'))

#register route
@app.route('/register',methods=['POST','GET'])
def register():
    if current_user.is_authenticated:#if curr already registered, return to index page
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #这里除了会调用表单中DataRequired这些定义的校验函数，也会调用自定义的 validate_字段名() 的校验函数，全部通过返回True
        #add new user into database
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Cong, Registration Succeed!'))
        return redirect(url_for('login'))
    return render_template('register.html',title='Registration',form=form)

#user info route
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user',username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user',username=user.username, page=posts.prev_num) if posts.has_prev else None

    # posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts.items,next_url=next_url,prev_url=prev_url)

@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash(_('Edited succeed'))
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html',title='Edit Profile',form=form)


#follow route
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not exists.'.format(username))
        return redirect(url_for('user',username=username))
    if user == current_user:
        flash(_('You can not follow yourself!'))
        return redirect(url_for('user',username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Following {} succeed!'.format(username))
    return redirect(url_for('user',username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not exists.'.format(username))
        return redirect(url_for('user', username=username))
    if user == current_user:
        flash(_('You can not unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Unfollowing {} succeed!'.format(username))
    return redirect(url_for('user', username=username))

#reset password request route
@app.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPsswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',title='Reset Password',form=form)

#reset password route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)



#explore route
@app.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',title='Explore',posts=posts.items,next_url=next_url,prev_url=prev_url)


@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],request.form['source_language'],request.form['dest_language'])})
