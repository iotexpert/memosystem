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
db.create_all()

