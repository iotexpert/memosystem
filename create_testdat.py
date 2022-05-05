try:
    import settings_local
except ImportError:
    pass
from docmgr import db,create_app
from docmgr.models.User import User
from flask import current_app


app = create_app()
app.app_context().push()
db.init_app(app)

user =  User(username=current_app.config['ADMIN_USER'], password=User.create_hash_pw(current_app.config['ADMIN_PASSWORD']),email=current_app.config['ADMIN_EMAIL'], admin=True)
db.session.add(user)
db.session.commit()

user =  User(username="u1", password=User.create_hash_pw("u1"),email="u1@u1.local")
db.session.add(user)
db.session.commit()