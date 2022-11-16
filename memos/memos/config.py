import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }

#    'pool_size': 10,
#    'pool_recycle': 60,
#    'pool_pre_ping': True

    if os.environ.get('SQLALCHEMY_ECHO') == 'True': # pragma nocover
        SQLALCHEMY_ECHO=True
    else:
        SQLALCHEMY_ECHO=False



    SECRET_KEY = os.environ.get('MEMOS_SECRET_KEY')
    
    MAIL_SERVER = os.environ.get('MEMOS_EMAIL_SERVER')
    MAIL_PORT = os.environ.get('MEMOS_EMAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MEMOS_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('MEMOS_EMAIL_PASS')
 
    ADMIN_USER = os.environ.get('MEMOS_ADMIN_USER')
    ADMIN_PASSWORD = os.environ.get('MEMOS_ADMIN_PASSWORD')
    ADMIN_EMAIL = os.environ.get('MEMOS_ADMIN_EMAIL')
    
    MEMO_ROOT = os.environ.get('MEMOS_MEMO_ROOT')
    
    LDAP_SCHEMA = os.getenv('LDAP_SCHEMA')
    LDAP_PORT = os.getenv('LDAP_PORT')
    LDAP_HOST = os.getenv('LDAP_HOST')
    LDAP_BASE_DN = os.getenv('LDAP_BASE_DN')
    LDAP_USERNAME = os.getenv('LDAP_USERNAME')
    LDAP_PASSWORD = os.getenv('LDAP_PASSWORD')
    LDAP_USER_OBJECT_FILTER = os.getenv('LDAP_USER_OBJECT_FILTER')
    LDAP_GROUP_OBJECT_FILTER = os.getenv('LDAP_GROUP_OBJECT_FILTER')
    LDAP_USE_SSL = LDAP_SCHEMA == 'ldaps'

    TESTING = True if os.getenv('TESTING') else False
 
    ENABLE_REGISTER = True if os.getenv('ENABLE_REGISTER') else False