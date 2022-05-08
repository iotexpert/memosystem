try:
    import settings_local
except ImportError:
    pass
from memos import db,create_app
import shutil
from memos.models.User import User
from memos.models.Memo import Memo
from memos.models.MemoFile import MemoFile
from memos.models.MemoSignature import MemoSignature


app=create_app()
app.app_context().push()
db.init_app(app)

try:
    shutil.rmtree("memos/static/memos/*")
except:
    print("Already removed files")
    
try:
    MemoSignature.__table__.drop(db.engine)
    MemoFile.__table__.drop(db.engine)
    Memo.__table__.drop(db.engine)
    User.__table__.drop(db.engine)

except:
    print("Tables already removed")
