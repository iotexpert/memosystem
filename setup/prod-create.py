from docmgr import db,create_app
from docmgr.models.User import User
from docmgr.models.MemoHistory import MemoHistory
from flask import current_app

app=create_app()
app.app_context().push()
db.init_app(app)
db.create_all()

admin =  User(username=current_app.config['ADMIN_USER'], password=User.create_hash_pw(current_app.config['ADMIN_PASSWORD']),email=current_app.config['ADMIN_EMAIL'],admin=True)

db.session.add(admin)
db.session.commit()

#MemoFile()
#MemoSignature()