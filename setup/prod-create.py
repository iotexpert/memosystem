from docmgr import db,create_app
from docmgr.models.User import User, Role, Authorization

from flask import current_app

app = create_app()
app.app_context().push()
db.init_app(app)
db.create_all()

user =  User(username=current_app.config['ADMIN_USER'], password=User.create_hash_pw(current_app.config['ADMIN_PASSWORD']),email=current_app.config['ADMIN_EMAIL'])
db.session.add(user)
db.session.commit()
Authorization.add(user,None,Role.Admin)

user =  User(username="u1", password=User.create_hash_pw("u1"),email="u1@u1.local")
db.session.add(user)
db.session.commit()
