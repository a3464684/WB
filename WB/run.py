#python虚拟环境
#意义：不怕被损坏    每个项目一个虚拟环境，这样每个项目之间不会受到影响
#做法：
#1.制作python虚拟环境
#    a.创建一个文件夹  vevn
#    b.python -m venv venv
#2.每次装包的时候要装到虚拟环境中
#    venv\Scripts\pip.exe install flask-wtf .....
#3.每次装包完成后都要生成需求文件
#    venv\Scripts\pip.exe freeze > requirements.txt

#如果不小心损坏了venv中的虚拟环境怎么办？
#1.删掉venv中的所有文件
#2.重新创建python虚拟环境
#   python -m venv venv
#3.安装原来项目需要的包
#   venv\Scripts\pip.exe install -r requirements.txt
#4.到此已经恢复了python虚拟环境

#蓝本？蓝本就是一个包，通常一个app包中包含多个蓝本
#意义：可以把不同功能的代码分别写到不同的蓝本中，可以减少代码耦合性，便于团队合作


from app import create_app
from app import db
from flask_script import Manager, Shell
from app.models import Student, Teacher, User
import pymysql
from flask_migrate import Migrate, MigrateCommand
from app.models import Cla, Stu

pymysql.install_as_MySQLdb()

app = create_app('develop')

manager = Manager(app)

#创建一个数据库迁移对象（修改表）
migrate = Migrate(app, db)

#增加一条命令叫做db经常
manager.add_command('db', MigrateCommand)

#输入库迁移具体步骤
#1.创建数据库迁移需要的目录和脚本文件
# venv\Scripts\python.exe run.py db init
#2.统计数据模型和表之前的区别
# venv\Scripts\python.exe run.py db migrate -m 'add age in student'
#3.第二部统计到的区别更新到数据库（修改表）
# venv\Scripts\python.exe run.py db upgrade

def make_context() :
    return dict(Student=Student,Teacher=Teacher,db=db,User=User, Cla=Cla, Stu=Stu)

manager.add_command('shell', Shell(make_context=make_context))

@manager.command
def test() :
    import unittest
    t = unittest.TestLoader()
    t = t.discover('tests')
    unittest.TextTestRunner().run(t)

from app.models import Role
@manager.command
def init() :
    Role.create_roles()


#app.run(debug=True, host='0.0.0.0')

#20180927 遇到了一个问题：数据库迁移的时候无法检测到改变
#分析原因：在数据库develop_db中有一个表用来记录版本，因为对数据库的不正常修改（注释1）导致了数据库中版本出问题
#解决办法：
#   方法一：
#       1.删除数据库中保存版本的表
#       2.删除项目中的migration文件夹
#       3.venv\Scripts\python.exe run.py db init
#       4.venv\Scripts\python.exe run.py db migrate
#       5.venv\Scripts\python.exe run.py db upgrade

#   方法二：
#       1.到项目中的migration文件夹中找到最新版本号
#       2.把版本号更新到数据库中保存版本的表
#           use develop_db
#           update alembic_version set version_num='b4f7dfc0e8f6';
#       3.venv\Scripts\python.exe run.py db migrate
#       4.venv\Scripts\python.exe run.py db upgrade
#注释1：不正常访问-不适用数据模型和数据库迁移对的方法去创建删除表

#在给用户发送邮件的时候发送一个链接
#http://iot.embsky.com/auth/check_token?token=字符串
#字符串应该满足两个条件：
#1.字符串必须无规律可循
#2.字符串必须能够唯一标识一个用户

#装饰器复习
#装饰器的本质是一个函数，这个函数的参数是个函数，返回值也是个函数


'''
def add(a, b) :
    return a + b

def hello(aa) :
    def zsq(fun) :
        def abc(a, b) :
            if a > 100 :
                if aa > 20:
                    a = 500
                else :
                    a = 50
            if b > 100 :
                b = 50
            ret = fun(a, b)
            return ret
        return abc
    return zsq

bb = hello(1)
hhh = bb(add)
hhh(1, 2)

from functools import wraps

def hello(aa) :
    def zsq(fun) :
        @wraps(fun)
        def abc(a, b) :
            if a > 100 :
                a = 50
            if b > 100 :
                b = 50
            ret = fun(a, b)
            return ret
        return abc
    return zsq
    
@hello(22)
def add(a, b) :
    return a + b

add(1, 3)
'''



manager.run()






