from app import mail
from flask_mail import Message
from threading import Thread
from flask import current_app


#发送同步邮件  调用此函数的时候会阻塞，也就是说会导致页面卡顿
def send_sync_email(subject, recvs, body, html) :
    #html如果为空的话body有效
    msg = Message(subject=subject, recipients=recvs, body=body, html=html)
    msg.sender = current_app.config['MAIL_USERNAME']
    with current_app.app_context() :
        mail.send(msg)

#发送异步邮件
def send_async_email(subject, recvs, body, html) :
    msg = Message(subject=subject, recipients=recvs, body=body, html=html)
    msg.sender = current_app.config['MAIL_USERNAME']
    #获取current_app代理的正真的app
    app = current_app._get_current_object()
    thead = Thread(target=send_email, args=[app, msg])
    thead.start()

def send_email(app, msg) :
    with app.app_context() :
        mail.send(msg)