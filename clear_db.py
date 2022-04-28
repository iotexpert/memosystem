try:
    import settings_local
except ImportError:
    pass
from docmgr import db,create_app
import shutil
from docmgr.models.User import User
from docmgr.models.Memo import Memo
from docmgr.models.MemoFile import MemoFile
from docmgr.models.MemoSignature import MemoSignature


app=create_app()
app.app_context().push()
db.init_app(app)

try:
    shutil.rmtree("docmgr/static/memos/*")
except:
    print("Already removed files")
    
try:
    MemoSignature.__table__.drop(db.engine)
    MemoFile.__table__.drop(db.engine)
    Memo.__table__.drop(db.engine)
    User.__table__.drop(db.engine)

except:
    print("Tables already removed")
