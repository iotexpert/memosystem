from datetime import datetime
from docmgr import db
from docmgr.models.User import User
from flask import current_app

class MemoSignature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    memo_id = db.Column(db.Integer, db.ForeignKey('memo.id'),nullable=False)
    signer_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)   # who is suppsoed to sign
    delegate_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=True)  # who actually performed the signature
    signed = db.Column(db.Boolean,default=False)
    date_signed = db.Column(db.DateTime, nullable=True)
    

    @staticmethod
    def get_signers(memo):
        signlist =  MemoSignature.query.filter_by(memo_id=memo.id).all()
        return signlist
    
    @staticmethod
    def sign(memo_id=memo_id,signer=None,delegate=None):
     
        #assert signer!=None and type(signer)==type(User)    

        
        current_app.logger.info(f"memo_id ={memo_id} signer={signer} delegate={delegate}")

        memosig = MemoSignature.query.filter_by(memo_id=memo_id,signer_id=signer.id).first()
        
        if memosig == None:
            return False
        
        # if the memo is already signed... ok sure.
        if memosig.signed:
            return True
               
        memosig.signed = True
        memosig.date_signed = datetime.utcnow()
        if delegate != None:
            memosig.delegate_id = delegate.id
        else:
            memosig.delegate_id = None
            
        current_app.logger.info(f"MemoSignature id={memosig.id} memo_id={memosig.memo_id} user_id={memosig.signer_id} signed ={memosig.signed} date signed ={memosig.date_signed}")
        
        db.session.add(memosig)
        db.session.commit()
        return True

    @staticmethod
    def unsign(memo_id=memo_id,signer=None,delegate=None):
        #assert signer!=None and type(signer)==type(User)    
        
        current_app.logger.info(f"Type for user = {type(signer)}")      
     
        memosig = MemoSignature.query.filter_by(memo_id=memo_id,signer_id=signer.id).first()
        
        if memosig == None:
            return False

        # if the memo is already signed... ok sure.
        if memosig.signed != True:
            return False
        
        memosig.signed = False
        memosig.date_signed = None
        memosig.acting_id = None
        current_app.logger.info(f"MemoSignature Unsigned id={memosig.id} memo_id={memosig.memo_id} signer_id={memosig.signer_id} acting_id={memosig.acting_id} signed ={memosig.signed} date signed ={memosig.date_signed}")
        
        db.session.add(memosig)
        db.session.commit()
        return True

    @staticmethod
    def unsign_all(memo=None):
        assert memo != None
        
        memo_sigs = MemoSignature.query.filter_by(memo_id=memo.id).all()
        for sig in memo_sigs:
            sig.delegate_id = None
            sig.signed = False
            sig.date_signed = None
            db.session.add(sig)
            db.session.commit()

    @staticmethod
    def add_signer(memo=None,signer=None):
        
        current_app.logger.info(f"signing memo={memo}")
        
        current_app.logger.info(f"Adding Signer {signer} to {memo.user.username}/{memo.number}/{memo.version}")
         
        sig = MemoSignature(memo_id=memo.id,signed=False,signer_id=signer.id)
        db.session.add(sig)
        db.session.commit()

    # look at all of the signatures.. return True if everyone has signed
    @staticmethod
    def status(memo_id):
        memosig = MemoSignature.query.filter_by(memo_id=memo_id,signed=False).all()
        current_app.logger.info(f"signature status = {memosig}")
        if memosig:
            return False
        return True

    @staticmethod
    def delete_signers(memo):
        MemoSignature.query.filter_by(memo_id=memo.id).delete()
    
    # returns a tuple
    # True or False if you are a signer
    # True of False if you have signed
    # The actual signer object
    @staticmethod
    def is_signer(memo_id=None,signer=None):
        
        current_app.logger.info(f"memo={memo_id} signer={signer}")
       
        if memo_id == None:
            return {'is_signer':False,'status':False,'signature':None}
       
        if signer == None:
            return {'is_signer':False,'status':False,'signature':None}
    
        msig = MemoSignature.query.filter_by(memo_id=memo_id,signer_id=signer.id).first()
        if msig != None:
            return {'is_signer':True,'status':msig.signed,'signature':msig}
        else:
            return {'is_signer':False,'status':False,'signature':None}

    @staticmethod
    def get_signatures(signer=None,signed=True):
        """
        This function creates a list of signatures needed to be signed by "signer"
        This function is used by the inbox to figure out what the person needs to sign
        """
        assert signer != None,"Signer must have some value"
        rval = []

        memosig = MemoSignature.query.filter_by(signer_id=signer.id,signed=signed).order_by(MemoSignature.signed).all()

        for sig in memosig:
            rval.append(sig.memo_id)
        current_app.logger.info(f"User={signer.username} Signatures = {memosig} Rval={rval}")
        return rval
    