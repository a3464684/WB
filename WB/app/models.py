from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

#写个例子来说明多对多
#多对多需要关系表实现

rel_table = db.Table('rel_table', \
                     db.Column('sid', db.Integer, db.ForeignKey('stus.id')),\
                     db.Column('cid', db.Integer, db.ForeignKey('clas.id')))
class Stu(db.Model) :
    __tablename__ = 'stus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    #多对多的反向关系
    #db.backref('students', lazy='dynamic') 代表添加到目标类中的字段students是一个query
    classes = db.relationship('Cla', secondary=rel_table, \
                              backref=db.backref('students', lazy='dynamic'), \
                              lazy='dynamic')

class Cla(db.Model) :
    __tablename__ = 'clas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

#权限
class Permission(object) :
    FOLLOW = 0x01
    WRITE = 0x02
    COMMENT= 0x04
    MODE_COMMENT= 0x08
    ADMIN = 0x80

class Role(db.Model) :
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False)
    users = db.relationship('User', backref='role')

    @staticmethod
    def create_roles():
        roles = {
            'user':[Permission.FOLLOW | Permission.WRITE | Permission.COMMENT, True],
            'moderator':[Permission.FOLLOW | Permission.WRITE | Permission.COMMENT | Permission.MODE_COMMENT, False],
            'admin':[0xff, False]
        }

        for r in roles :
            role = Role.query.filter_by(name=r).first()
            if role is None :
                role = Role()
                role.name = r
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class Student(db.Model) :
    __tablename__='students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default='zhangsan')
    age = db.Column(db.Integer, default=20)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))

class Teacher(db.Model) :
    __tablename__='teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default='张三')
    age = db.Column(db.Integer, default=30)
    #lazy='dynamic' 代表访问students的时候返回的是一个query，可以进一步过滤
    #如果没有lazy='dynamic'则访问students的时候返回的是一个列表
    students = db.relationship('Student', backref='teacher', lazy='dynamic')

from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

#多对多的时候需要一个关系表
class Follow(db.Model) :
    #关注者的ID
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    #被关注者ID
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    #关注的时间
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin) :
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128))
    name = db.Column(db.String(128), default='张三')
    password_hash = db.Column(db.String(128))

    #外键  角色
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    about_me = db.Column(db.Text)
    location = db.Column(db.String(64))

    #default=datetime.utcnow()----register_time存放的都是修改表（数据库迁移）的时间
    #default=datetime.utcnow------register_time存放的是创建User对象的时间
    register_time = db.Column(db.DateTime, default=datetime.utcnow)
    access_time = db.Column(db.DateTime, default=datetime.utcnow)

    #-------为了做用户邮箱激活-----------------------------------#
    confirmed = db.Column(db.Boolean, default=False)

    def generate_confirmed_token(self):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'], expires_in=120)
        token = s.dumps({'id':self.id})
        return token

    def confirm(self, token):
        s = Serializer(secret_key=current_app.config['SECRET_KEY'])
        try :
            #token如果超时的话会由异常
            d = s.loads(token)
        except :
            return False

        if d.get('id') == self.id :
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True
        return False

    #-------为了做用户邮箱激活-----------------------------------#

    def __str__(self):
        return str(self.id)+":"+self.name

    #构建一个属性
    @property
    def password(self):
        #密码不能读取，如果读取抛出异常
        raise AttributeError('密码不能读取')
    @password.setter
    def password(self, password):
        #利用sha256+杂质串的方式产生hash值
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        #验证密码是否正确
        return check_password_hash(self.password_hash, password)

    #----------------实现权限认证的方法--------------------#
    def has_permission(self, permission):
        return self.role.permissions & permission == permission
    def is_admin(self):
        return self.has_permission(0xff)

    def is_moderator(self):
        return self.has_permission(Permission.FOLLOW | Permission.WRITE | Permission.COMMENT | Permission.MODE_COMMENT)
    #----------------实现权限认证的方法--------------------#

    #这个方法用来更新用户访问时间
    #这个方法应该在用户访问任何页面的时候调用
    def flush_access_time(self):
        self.access_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    commends = db.relationship('Comment', backref='user', lazy='dynamic')

    news = db.relationship('News', backref='user', lazy='dynamic')

    #粉丝们：关注我们的人们  我们的关注者们
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    #大微们：我们关注的人们  被我们关注的人
    followeds = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    #加一个用来关注其他用户的函数
    def follow(self, user):
        if self.if_follower_of(user) == False :
            f = Follow()
            # f.follower_id = self.id
            # f.followed_id = user.id

            #self.followeds.append(user)

            f.followed = user
            f.follower = self

            db.session.add(f)
            db.session.commit()
    #取消关注
    def unfollow(self, user):
        if self.if_follower_of(user) :
            f = self.followeds.filter_by(followed_id=user.id).first()
            db.session.delete(f)
            db.session.commit()

    #判断自己是不是user的粉丝
    def if_follower_of(self, user):
        #Follow.query.filter_by(followed_id=user.id).filter_by(follower_id=self.id).first()
        #self.followeds.filter_by(followed_id=user.id).first()
        #self.followeds.fiter_by(followed=user).first()
        return self.followeds.filter_by(followed_id=user.id).first() is not None

    #判断自己是不是user的大微
    def if_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

#匿名用户类
#当一个没有登陆的用户访问时，那么login_manager会创建一个匿名用户对象
#currrent_user会代理这个匿名用户对象
from flask_login import AnonymousUserMixin
class AnonymousUser(AnonymousUserMixin) :
    name = '游客'
    def has_permission(self, permission):
        return False
    def is_admin(self):
        return False
    def flush_access_time(self):
        pass

#这个函数由flask-login框架调用
#在用户注销的时候调用logout_user
#logout_user中会通过user_load函数获取到用户对象，然后把用户设置为匿名用户
from app import login_manager
@login_manager.user_loader
def user_load(id) :
    return User.query.get(int(id))

class News(db.Model) :
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    private = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref='new', lazy='dynamic')

class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    new_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
