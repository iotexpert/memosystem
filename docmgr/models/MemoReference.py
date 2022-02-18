
from docmgr import db
from docmgr.models.MemoState import MemoState
from flask import current_app
import re

class MemoReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('memo.id'),nullable=False)
    
    ref_user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    ref_memo_number = db.Column(db.Integer,nullable=False)
    ref_memo_version = db.Column(db.Integer)
    
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
        ref_list = MemoReference.query.filter_by(reference_id=memo.id).all()
        for ref in ref_list:
            rval.append(ref.source_id)
        return rval
    
    
    @staticmethod
    def add_ref(memo_src_id,ref_user_id=None,ref_memo_number=None,ref_memo_version=None):
        new_ref = MemoReference(source_id=memo_src_id,ref_user_id=ref_user_id,ref_memo_number=ref_memo_number,ref_memo_version=ref_memo_version)
        db.session.add(new_ref)
        db.session.commit()
        current_app.logger.info(f"Adding Reference {new_ref}")

