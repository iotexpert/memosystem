
from docmgr import db
from flask import current_app

class MemoReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('memo.id'),nullable=False)
    
    ref_user_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=False)
    ref_memo_number = db.Column(db.Integer,nullable=False)
    ref_memo_version = db.Column(db.String(10))
    
    @staticmethod
    def get_refs(memo):
        rval=[]
        ref_list = MemoReference.query.filter_by(source_id=memo.id).all()
        for ref in ref_list:
            rval.append([ref.ref_user_id,ref.ref_memo_number,ref.ref_memo_version])
        return rval
    
    @staticmethod
    def get_back_refs(memo):
        rval=[]
        ref_list = MemoReference.query.filter_by(ref_user_id=memo.userid,ref_memo_number=memo.number,ref_memo_version=memo.version).all()
        for ref in ref_list:
            rval.append(ref.source_id)
        return rval
    
    
    @staticmethod
    def add_ref(memo_src_id,ref_user_id=None,ref_memo_number=None,ref_memo_version=None):
        new_ref = MemoReference(source_id=memo_src_id,ref_user_id=ref_user_id,ref_memo_number=ref_memo_number,ref_memo_version=ref_memo_version)
        db.session.add(new_ref)
        db.session.commit()
#        current_app.logger.info(f"Adding Reference {new_ref}")


    @staticmethod
    def delete(memo):
        MemoReference.query.filter_by(id=memo.id).delete()
        