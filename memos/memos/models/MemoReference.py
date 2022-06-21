from memos import db
from flask import current_app

class MemoReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('memo.id'),nullable=False)
    
    ref_user_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=False)
    ref_memo_number = db.Column(db.Integer,nullable=False)
    ref_memo_version = db.Column(db.String(2))
        
    @staticmethod
    def add_ref(memo_src_id,ref_user_id=None,ref_memo_number=None,ref_memo_version=None):
        new_ref = MemoReference(source_id=memo_src_id,ref_user_id=ref_user_id,ref_memo_number=ref_memo_number,ref_memo_version=ref_memo_version)
        db.session.add(new_ref)


    @staticmethod
    def delete(memo):
        MemoReference.query.filter_by(id=memo.id).delete()
        