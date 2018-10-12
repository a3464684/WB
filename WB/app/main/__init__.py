#导入蓝本类
from flask import Blueprint

main = Blueprint('main', __name__)

#导入views和errors模块，不然其中的视图不能使用
from . import views,errors