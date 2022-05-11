from memos import db
from flask import current_app

class MemoSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=False)   # who is watching
    subscription_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=True)  # who is being watched


    @staticmethod
    def delete(user):
        MemoSubscription.query.filter_by(subscriber_id=user.username).delete()


    @staticmethod        
    def get(user):
        sublist = MemoSubscription.query.filter_by(subscriber_id=user.username).all()
        return sublist