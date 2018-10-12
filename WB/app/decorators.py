from functools import wraps
from app.models import Permission
from app.models import User
from flask_login import current_user
from flask import abort

def decorator_permission(permission) :
    def permission_fun(fun) :
        @wraps(fun)
        def p_fun() :
            if current_user.has_permission(permission) :
                ret = fun()
                return ret
            abort(403)
        return p_fun
    return permission_fun

def decorator_admin(fun) :
    return decorator_permission(0xff)(fun)


