class Config() :
    #表单需要配置
    WTF_CSRF_ENABLE=True
    SECRET_KEY='iot.embsky.com'

    #邮箱需要的配置
    MAIL_SERVER='smtp.163.com'
    MAIL_PORT='25'
    MAIL_USE_TLS=True
    MAIL_USERNAME='18846681020@163.com'
    #授权码  参考flask基础笔记-->发送基础笔记
    MAIL_PASSWORD='python0722'

    #数据库需要
    SQLALCHEMY_TRACK_MODIFICATIONS=False

class DevelopConfig(Config) :
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@172.25.11.196/develop_db'

class TestConfig(Config):
    TEST = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@172.25.8.12/test_db'

class ProductConfig(Config) :
    SQLALCHEMY_DATABASE_URL = 'mysql://root:123456@172.25.8.12/product_db'


config = {
    'develop':DevelopConfig,
    'test':TestConfig,
    'product':ProductConfig,
    'default':DevelopConfig,
}