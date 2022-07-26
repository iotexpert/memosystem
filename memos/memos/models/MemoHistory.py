from datetime import datetime

from memos import db
from memos.models.User import User
from memos.models.MemoActivity import MemoActivity
from flask import current_app

class MemoHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    memo_id = db.Column(db.Integer, db.ForeignKey('memo.id'))
    memo_ref = db.Column(db.String(48))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    memo_activity = db.Column(db.Enum(MemoActivity))      # For some reason the attribute names "activity" and "action" are illegal
    ref_user_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=False)

    @staticmethod
    def activity(memo=None,memo_activity=None,user=None):
        if user==None:
            userid =  '0'
        else:
            userid = user.username
        current_app.logger.info(f"activity={memo_activity} memo={memo} memoid={memo.id} user={user}")
   
        if memo_activity != MemoActivity.Cancel:
            mh = MemoHistory(memo_id=memo.id,memo_ref=f"{memo}",memo_activity=memo_activity,ref_user_id=userid)
        else:
            # Update all of the memo_id's of this one to NULL
            MemoHistory.query.filter_by(memo_id=memo.id).update(dict(memo_id=None))
            mh = MemoHistory(memo_id=None,memo_ref=f"{memo}",memo_activity=memo_activity,ref_user_id=userid)
            
        
        db.session.add(mh)

            
    @staticmethod
    def get_history(memo_ref=None,memo=None,page=1,pagesize=None):
        return MemoHistory.query.order_by(MemoHistory.id.desc()).paginate(page = page,per_page=pagesize)

