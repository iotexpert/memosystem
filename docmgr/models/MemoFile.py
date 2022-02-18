
from sqlalchemy import Column
from docmgr import db
import uuid

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
   