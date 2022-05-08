"""
This file creates some test users
"""

try:
    import settings_local
except ImportError:
    pass

from memos import db,create_app
from memos.models.User import User


app = create_app()
app.app_context().push()
db.init_app(app)

u1 =  User(username="u1", password=User.create_hash_pw("u1"),email="u1@u1.local")
db.session.add(u1)
db.session.commit()

u2 =  User(username="u2", password=User.create_hash_pw("u2"),email="u2@u2.local")
db.session.add(u2)
db.session.commit()

# delegate to u1 to u2
u1.delegates = "u2"

# a plain user with no delgation authority
u3 =  User(username="u3", password=User.create_hash_pw("u3"),email="u3@u3.local")
db.session.add(u3)
db.session.commit()

# a readall user
u4 =  User(username="u4", password=User.create_hash_pw("u4"),email="u4@u4.local",readAll=True)
db.session.add(u4)
db.session.commit()
