import unittest
from flask import current_app
from app import create_app, db
from app.models import Student, Teacher, User

class TestUser(unittest.TestCase) :
    def test_user_password_set(self):
        u = User()
        u.password = '123'
        self.assertTrue(u.password_hash)
    def test_user_password_get(self):
        u = User()
        u.password = '123'
        self.assertTrue(u.password_hash)
        with self.assertRaises(AttributeError) :
            u.password
    def test_user_check_password(self):
        u = User()
        u.password = '123'
        self.assertTrue(u.check_password('123'))
    def test_user_only_password(self):
        u = User()
        u.password = '123'
        u1 = User()
        u1.password = '123'
        self.assertFalse(u.password_hash == u1.password_hash)

class TestDB(unittest.TestCase) :
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        t = Teacher()
        t.name = 'zhangliu'
        t.age = 35
        db.session.add(t)
        db.session.commit()
        s = Student()
        s.name = 'wangwu'
        s.age = 20
        s.teacher = t
        db.session.add(s)
        db.session.commit()
    def tearDown(self):
        for s,t in Student.query.all(), Teacher.query.all()  :
            db.session.delete(t)
            db.session.delete(s)
        db.session.commit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    def test_db_query(self):
        t = Teacher.query.first()
        self.assertTrue(t.name == 'zhangliu')

#flask的测试框架会自动创建以下类的对象进行测试
#每次测试都先调用setUp函数，然后再调用其它函数，最后调用tearDown函数
class TestClass(unittest.TestCase) :
    def setUp(self):
        print('start test')
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.t = Teacher()
        self.t.name = 'lizhiyong'
        self.t.age = 32
        db.session.add(self.t)
        db.session.commit()
        self.s = Student()
        self.s.name = 'zhangsan'
        self.s.age = 22
        self.s.teacher = self.t
        db.session.add(self.s)
        db.session.commit()

    def tearDown(self):
        print('end test')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #本次目的是测试app是否能在test配置下创建
    def test_app_exists(self):
        #self.assertTru如果参数表达式为真，代表测试成功，否则测试失败
        self.assertTrue(current_app)
    def test_app_is_test(self):
        self.assertTrue(current_app.config['TEST'])

    #本次测试目的是测试Student模型和Teacher模型
    def test_teacher_exists(self):
        self.assertTrue(self.t is not None)
        self.assertTrue(self.t.name == 'lizhiyong')
    def test_student_exists(self):
        self.assertTrue(self.s)
        self.assertFalse(self.s.name == 'lizhiyong')
        self.assertTrue(self.s.teacher.name == 'lizhiyong')