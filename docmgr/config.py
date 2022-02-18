import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=False
    

    SECRET_KEY = os.environ.get('DOCMGR_SECRET_KEY')
    
    MAIL_SERVER = os.environ.get('DOCMGR_EMAIL_SERVER')
    MAIL_PORT = os.environ.get('DOCMGR_EMAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('DOCMGR_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('DOCMGR_EMAIL_PASS')
 
    ADMIN_USER = os.environ.get('DOCMGR_ADMIN_USER')
    ADMIN_PASSWORD = os.environ.get('DOCMGR_ADMIN_PASSWORD')
    ADMIN_EMAIL = os.environ.get('DOCMGR_ADMIN_EMAIL')
    
    MEMO_ROOT = os.environ.get('DOCMGR_MEMO_ROOT')
 