
from memos import db
import uuid
import os

class MemoFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _filename = db.Column(db.String(4000))
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

    def __repr__(self):
        return f"File('Document Filename = {self.filename}')"
   
    @staticmethod
    def delete(memo):
        MemoFile.query.filter_by(memo_id=memo.id).delete()
    
    def remove_file(self,memo):
        
        path = memo.get_fullpath()
        try:
            os.remove(os.path.join(path, self.uuid))
        except: # pragma nocover
            pass # ARH... well this can only happen if the file is already gone... which is what we want
        
        db.session.delete(self)
