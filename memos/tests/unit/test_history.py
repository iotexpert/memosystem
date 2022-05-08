#from docmgr import db,create_app
#from sqlalchemy_utils.functions import database_exists
from docmgr.models.MemoActivity import Memoactivity
from docmgr.models.User import User
from docmgr.models.Memo import Memo
#from docmgr.models.MemoState import MemoState
#from docmgr.models.MemoFile import MemoFile
#from docmgr.models.MemoSignature import MemoSignature
from docmgr.models.MemoHistory import MemoHistory

def test_history():
    pass
    u1 = User.find(username="u1")
    print(f"User = {u1}")
    memo = Memo.find(username="u1",memo_number=1,memo_version='A')
    print(f"{memo}")

    MemoHistory.activity(user=u1,activity=Memoactivity.Create,memo=memo)
    MemoHistory.activity(user=u1,activity=Memoactivity.Sign,memo=memo)
    MemoHistory.activity(user=u1,activity=Memoactivity.Sign,memo=memo)
    MemoHistory.activity(user=u1,activity=Memoactivity.Sign,memo=memo)
    #MemoHistory.activity(user=u1,activity=Memoactivity.Cancel,memo=memo)
