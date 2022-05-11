import os

# LDAP settings
del os.environ["LDAP_HOST"]  # LDAP is too site specific for general automated tests

os.environ['FLASK_ENV'] = 'development'

os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.db'
#os.environ['MEMOS__DATABASE_URI'] = 'mysql+pymysql://user:password@test.local/MEMOS'
#os.environ['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.environ['MEMOS_SECRET_KEY'] = '1E14EDDEF7D41DADBCEA47F14ABEF'

os.environ['MEMOS_EMAIL_SERVER'] = 'smtp.google.com'
os.environ['MEMOS_EMAIL_PORT'] = '587'
os.environ['MEMOS_EMAIL_USER'] = ''
os.environ['MEMOS_EMAIL_PASS'] = ''
