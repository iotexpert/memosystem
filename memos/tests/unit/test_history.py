#from memos import db,create_app
#from sqlalchemy_utils.functions import database_exists
from memos.models.MemoActivity import MemoActivity
from memos.models.User import User
from memos.models.Memo import Memo
#from memos.models.MemoState import MemoState
#from memos.models.MemoFile import MemoFile
#from memos.models.MemoSignature import MemoSignature
from memos.models.MemoHistory import MemoHistory

def test_history(session):
    pass
    u1 = User.find(username="u1")
    print(f"User = {u1}")
    memo = Memo.find(username="u1",memo_number=1,memo_version='A')
    print(f"{memo}")

    MemoHistory.activity(user=u1,activity=MemoActivity.Create,memo=memo)
    MemoHistory.activity(user=u1,activity=MemoActivity.Sign,memo=memo)
    MemoHistory.activity(user=u1,activity=MemoActivity.Sign,memo=memo)
    MemoHistory.activity(user=u1,activity=MemoActivity.Sign,memo=memo)
    #MemoHistory.activity(user=u1,activity=Memoactivity.Cancel,memo=memo)
