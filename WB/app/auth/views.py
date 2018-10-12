from . import auth
from flask import render_template
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm, RegisterForm
from flask import abort
from app.models import User
from flask import redirect, flash, url_for
from app import db
from flask import request
from flask_login import current_user
from flask import current_app
from app.models import Role

# @auth.errorhandler
# def error_handler(e) :
#     flash(str(e))
#     return redirect(url_for('.register'))

from app.email import send_async_email

@auth.route('/register', methods=['GET', 'POST'])
def register() :
    form = RegisterForm()
    if form.validate_on_submit() :
        #在这里可以放心使用表单 邮箱一定是唯一的
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.password = form.password.data

        #'user','moderotor','admin'
        #如果用户注册的邮箱和config.py中发送邮件的邮箱一样，那么这个用户分配管理员
        if user.email == current_app.config['MAIL_USERNAME'] :
            user.role = Role.query.filter_by(name='admin').first()
        else :
            user.role = Role.query.filter_by(default=True).first()
        #其他用户都设置为user角色

        db.session.add(user)
        db.session.commit()

        #发送邮件
        token = user.generate_confirmed_token()
        html = render_template('email/register.html', token=token, user_name=user.name)
        send_async_email(subject='阳光社区验证邮件', recvs=[user.email], body=None, html=html)

        flash('恭喜！注册成功！赶紧登陆！')
        return redirect(url_for('.login'))

    return render_template('auth/register.html', form=form)

@auth.route('/resend_email')
def resend_email() :
    # 发送邮件
    token = current_user.generate_confirmed_token()
    html = render_template('email/register.html', token=token, user_name=current_user.name)
    send_async_email(subject='阳光社区验证邮件', recvs=[current_user.email], body=None, html=html)

    return redirect(url_for('main.user_info'))


@auth.route('/confirm')
@login_required
def confirm() :
    token = request.args.get('token')
    if token is None :
        abort(404)
    if current_user.confirm(token) :
        return redirect(url_for('main.user_info'))
    return render_template('auth/resend_email.html')

#钩子函数
#这个函数会截获所有的请求
#也就是用浏览器访问我们的路由的时候要先执行这个函数
@auth.before_app_request
def before_app_request() :
    #什么样的用户我们才截获？
    #1.已经登陆 and 没有认证 and 访问的不是auth.和stastic
    #print(request.endpoint)
    current_user.flush_access_time()
    if current_user.is_authenticated and\
        not current_user.confirmed and \
        request.endpoint[:5] != 'auth.' and \
        request.endpoint != 'static' :
        #注意：访问其他蓝本的时候，比如main蓝本时候，当前蓝本就是main
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed() :
    if not current_user.confirmed :
        return render_template('auth/unconfirmed.html')
    return redirect(url_for('main.user_info'))

@auth.route('/logout')
@login_required
def logout() :
    logout_user()
    return redirect(url_for('.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login() :
    form = LoginForm()
    if form.validate_on_submit() :
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user is None :
            abort(404)
        if user.check_password(password) :
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.user_info', id=user.id))
        else :
            flash('邮箱或者密码错误')
            return redirect(url_for('.login'))
    return render_template('auth/login.html', form=form)

