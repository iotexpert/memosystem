from docmgr import db
from flask import current_app

class MemoSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)   # who is suppsoed to sign
    subscription_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=True)  # who actually performed the signature


    @staticmethod
    def delete(user):
        MemoSubscription.query.filter_by(subscriber_id=user.id).delete()


    @staticmethod        
    def get(user):
        sublist = MemoSubscription.query.filter_by(subscriber_id=user.id).all()
        return sublist