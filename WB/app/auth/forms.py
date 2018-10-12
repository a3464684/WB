from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from app.models import User
from wtforms.validators import ValidationError

class LoginForm(FlaskForm) :
    email = StringField(label='邮箱', validators=[DataRequired(), Email(), Length(6,128)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 128)])
    remember_me = BooleanField(label='记住我')
    submit = SubmitField(label='登陆')


#只要表单验证失败就会抛出ValidationError异常
#这个异常会被表单夸奖捕获
#我们需要在模板中进行显示异常信息

#比如:
# {{form.email}}
# {% for e in form.email.errors %}
#  {{e}}
# {% endfor %}
# {{form.password}}
# {% for e in form.password.errors %}
#  {{e}}
# {% endfor %}
class RegisterForm(FlaskForm) :
    email = StringField(label='邮箱', validators=[DataRequired(), Email(), Length(6, 128)])
    name = StringField(label='昵称', validators=[DataRequired(), Length(2, 128)])
    password = PasswordField(label='密码', validators=[DataRequired(), Length(1, 128)])
    password_again = PasswordField(label='确认密码', validators=[EqualTo('password', '两侧输入的密码不一样')])
    submit = SubmitField(label='注册')

    #当提交表单的时候验证email要，自动调用，函数正常返回代表验证成功
    #如果你认为验证不成功则抛出异常
    #field是email
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None :
            #说明该邮箱已经被注册了
            raise ValidationError('这个邮箱已经被注册')

