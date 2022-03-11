
from argparse import Action
from datetime import date
from docmgr import db

class MemoHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    memo_id = db.Column(db.Integer, db.ForeignKey('memo.id'))
    memo_ref = db.Column(db.String(48))
    date = db.Column(db.DateTime)
    action = db.Column(db.String(12))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    