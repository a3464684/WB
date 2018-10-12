from flask import render_template,redirect,url_for
from . import main

#能够截获所有蓝本中发生的404错误
#当用户访问的路由不存在或者调用abort(404)都会跳到此处
@main.app_errorhandler(404)
def error_handler_404(e) :
    return render_template('404.html')

#当用户访问的视图函数发生异常或者调用abort(500)都会跳到此处
@main.app_errorhandler(500)
def error_handler_500(e) :
    return render_template('500.html')

#当用户访问的视图没有权限或者调用abort(403)都会跳到此处
@main.app_errorhandler(403)
def error_handler_403(e) :
    return render_template('403.html')