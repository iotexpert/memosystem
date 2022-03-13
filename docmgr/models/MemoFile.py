
from sqlalchemy import Column
from docmgr import db
import uuid
import os
from flask import current_app

class MemoFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _filename = db.Column(db.String(48))
    _uuid = db.Column(db.String(48)) 
    memo_id = db.Column(db.Integer, db.ForeignKey('memo.id'),nullable=False)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self,filename):
        self._filename = filename
        self._uuid = str(uuid.uuid4())       
    
    @property
    def uuid(self):
        return self._uuid
      

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"File('Document Filename = {self.filename}')"

    @staticmethod
    def files(memo_id):
        files = MemoFile.query.filter_by(memo_id=memo_id).order_by(MemoFile.id)
        return files
   
    @staticmethod
    def delete(memo):
        MemoFile.query.filter_by(memo_id=memo.id).delete()
    
    def remove_file(self,memo=None):
        
        path = memo.get_fullpath()
        try:
            os.remove(os.path.join(path, self.uuid))
        except:
            pass # ARH... well this can only happen if the file is already gone... which is what we want
        
        memo.num_files = memo.num_files - 1
        memo.save()
        
        db.session.delete(self)
        db.session.commit()  
