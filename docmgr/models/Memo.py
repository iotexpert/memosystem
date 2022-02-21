
from datetime import datetime
from weakref import ref
from flask import current_app
from docmgr import db
from docmgr.models.User import User
from docmgr.models.MemoState import MemoState
from docmgr.models.MemoFile import MemoFile
from docmgr.models.MemoSignature import MemoSignature
from docmgr.models.MemoReference import MemoReference
import shutil

import re
import os
import json

class Memo(db.Model):
    """[summary]

    Args:
        db ([type]): [description]
    Returns:
        [type]: [description]
    """
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    version = db.Column(db.Integer)
    confidential = db.Column(db.Boolean,default=False)
    distribution = db.Column(db.String(128),default='') 
    keywords = db.Column(db.String(128),default='') 
    title = db.Column(db.String(128), nullable=False,default='')
    num_files = db.Column(db.Integer,default=0)
    memo_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    _signers = db.Column(db.String(128),default='')
    _references = db.Column(db.String(128),default='')
        
    memo_state = db.Column(db.Enum(MemoState))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # do custom initialization here

    def __repr__(self):
        return f"{self.user.username}-{self.number}-{self.version}"



########################################
# Permission Functions 
########################################

    @staticmethod
    def can_create(owner=None,delegate=None):
        if owner==None or delegate==None:
            return False
        
        current_app.logger.info(f"{owner} {delegate}")
        
        return owner.is_delegate(delegate=delegate)

    def can_revise(self,delegate=None):

        if delegate == None:
            return False
        
        if not self.user.is_delegate(delegate):
            return False

        if self.memo_state == MemoState.Active or self.memo_state == MemoState.Obsolete:
            return True

    def can_sign(self,signer=None,delegate=None):

        if signer==None or delegate==None:
            return False
                
        if self.memo_state != MemoState.Signoff:
            return False
        
        if not signer.is_delegate(delegate=delegate):
            return False
       
        status = MemoSignature.is_signer(self.id,signer)
        current_app.logger.info(f"can_sign status = {status}")
        return status['is_signer'] and not status['status'] 
        
    def can_unsign(self,signer=None,delegate=None):
        if signer==None or delegate==None:
            return False
        
        if self.memo_state != MemoState.Signoff:
            return False
        
        if not signer.is_delegate(delegate=delegate):
            return False
        
        current_app.logger.info(f"Signer={signer} delegate={delegate}")
       
        status = MemoSignature.is_signer(self.id,signer)
        current_app.logger.info(f"can_sign status = {status}")
        return status['is_signer'] and status['status'] 

    def can_obsolete(self,delegate=None):
    
        if delegate == None:
            return False
        
        if not self.user.is_delegate(delegate):
            return False
        
        if self.memo_state == MemoState.Active:
            return True 

        return False



    def can_cancel(self,delegate=None):

        if delegate == None:
            return False

        if self.memo_state != MemoState.Draft:
            return False
            
        if not self.user.is_delegate(delegate=delegate):
            return False
        
        return True



    def can_reject(self,signer=None,delegate=None):
        
        if signer==None or delegate == None:
            return False

        if self.memo_state != MemoState.Signoff:
            return False

        if not signer.is_delegate(delegate):
            return False
        
        status = MemoSignature.is_signer(memo_id=self.id,signer=signer)

        # if you are a signer you can reject.. even if you have already signed
        return status['is_signer']

        
    # This function will return True of the "username" has access to self
    def has_access(self,user=None):
        # if it is not confidential than anyone can access
        if self.confidential == False:
            return True

        # at this point we know it is confidential so ... they must provide a username
        if user == None:
            return False


        # you alway have access to your own memo's
        if self.username == user.username:
            return True

        if user.admin:
            return True

        # if the username is in the distribution list then provide access
        if user.username in re.split(r'\s|\,',self.distribution):
            return True

        return False


########################################
# ??? Functions 
########################################

    def get_fullpath(self):
        path = os.path.join(current_app.root_path,"static","memos",f"{self.user_id}",f"{self.number}",f"{self.version}")
        return path

    def get_relpath(self):
        path = os.path.join("/static","memos",f"{self.user_id}",f"{self.number}",f"{self.version}")
        return path

    # return a list of the files attached to this memo
    def get_files(self):
        memo_list = MemoFile.query.filter_by(memo_id=self.id).all()
        return memo_list

    # arh need to add the list of signers and files
    def saveJson(self):
        js = {}
        js['title']=self.title
        js['number']=self.number
        js['version']=self.version
        js['confidential']=self.confidential
        js['distribution']=self.distribution
        js['keywords']=self.keywords
        js['memo_date']=f"{self.memo_date}"
        js['userid']=self.user_id
        js['memo_state']=f"{self.memo_state}"
        js['files']=[]
        for file in self.get_files():
            js['files'].append(file.filename)
    
        path = os.path.join(self.get_fullpath())
        #current_app.logger.info(f"Making Directory {path}")
        os.makedirs(path,exist_ok=True)
        #current_app.logger.info(f"Making Succeeded {path}")

        path = os.path.join(path,f"meta{self.user_id}-{self.number}-{self.version}.json")
        f = open(path,"w")
        json.dump(js,f)
        f.close()


    # get the signers from the singing table and turn it back to a string
    @property 
    def signers(self):
        return self._signers
    
        siglist = MemoSignature.get_signers(self)
        for sig in siglist:
            sig.signer = User.find(userid=sig.signer_id)
            sig.delegate = User.find(userid=sig.delegate_id)
        return siglist
        
    @signers.setter
    def signers(self,signer_names):
        
        self._signers = signer_names
        
        current_app.logger.info(f"Adding signers={signer_names}")
        MemoSignature.delete_signers(self)

        users = User.valid_usernames(signer_names)

        for signer in users['valid_users']:
            MemoSignature.add_signer(memo=self,signer=signer)

######################################################################
# References
######################################################################

    @staticmethod
    def parse_reference(reference):
        parts = re.split(r'-',reference)
        if len(parts) == 2:
            parts.append(None)
        return parts
            
    @staticmethod 
    def valid_references(references):
        current_app.logger.info(f'references ={references}')
        valid_memos = []
        valid_refs = []
        invalid = []
        for memo_ref in re.split(r'\s|\,',references):
            current_app.logger.info(f"Reference = {memo_ref}")
            if memo_ref == '':
                continue
            parts = Memo.parse_reference(memo_ref)
            if len(parts) > 3 or len(parts) < 2:
                invalid.append(memo_ref)
                current_app.logger.info(f"INVALID length append {memo_ref} valid={valid_memos} invalid {invalid}")
                continue
            username = parts[0]
            memo_number = parts[1]
            memo_version = parts[2]
            current_app.logger.info(f"Validating {parts[0]}-{parts[1]}-{parts[2]}")
            memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
            current_app.logger.info(f"Memo = {memo}")
            if memo != None and (memo.memo_state == MemoState.Active or memo.memo_state == MemoState.Obsolete):
                valid_memos.append(memo)
                valid_refs.append(memo_ref)
                current_app.logger.info(f"VALID append {memo_ref} valid={valid_refs} invalid {invalid}")
            else:
                invalid.append(memo_ref)
                current_app.logger.info(f"INVALID append {memo_ref} valid={valid_refs} invalid {invalid}")
        
        rval = {'valid_refs':valid_refs, 'valid_memos' : valid_memos,'invalid':invalid}
        current_app.logger.info(f"Rval - {rval}")
        return rval
            
    @property
    def references(self):
    
        refs = MemoReference.get_refs(self)
        rval = []
        for ref in refs:
            user = User.find(userid=ref[0])
            memo = Memo.find(username=user.username,memo_number=ref[1],memo_version=ref[2])
            if ref[2] == None:
                refstring=f"{user.username}-{ref[1]}"
            else:
                refstring=f"{user.username}-{ref[1]}-{ref[2]}"
            rval.append((refstring,memo))
        return {'reflist':rval,'refs':self._references}
    
    @references.setter
    def references(self,references):
        current_app.logger.info(f"Adding References {references}")
        self._references = references
        
        refs = Memo.valid_references(references)
        for i in range(len(refs['valid_refs'])):
            parsed_ref = Memo.parse_reference(refs['valid_refs'][i])
            user = User.find(username=parsed_ref[0])
            MemoReference.add_ref(self.id,ref_user_id=user.id,ref_memo_number=parsed_ref[1],ref_memo_version=parsed_ref[2])
                

    @property
    def backrefs(self):
        return MemoReference.get_back_refs(self)
        
######################################################################
# 
######################################################################

    def get_next_version(self):
        memo = Memo.query.join(User).filter(Memo.number == self.number)\
            .order_by(Memo.version.desc()).first()

        current_app.logger.info(f"get_next_version {memo.id} {memo.number} {memo.version}")
        if memo:
            return memo.version + 1
        return 1


        
    def save(self):
        db.session.add(self)
        db.session.commit()
        self.saveJson()


################################################################################       
# functions used to process the state   
# these function would classiavally be called private
################################################################################       

    def obsolete_previous(self): # TODO: perhaps this should be in the process_state function?  (probably)
        prev_list = Memo.query.join(User).filter(Memo.number == self.number,Memo.version != self.version).all()
        for memo in prev_list:
            if memo.memo_state == MemoState.Active:
                memo.memo_state = MemoState.Obsolete
                memo.save()
    
    def process_state(self):
        current_app.logger.info(f"Process State MemoState={MemoSignature.status(self.id)}")
        if self.memo_state == MemoState.Draft:
            if MemoSignature.status(self.id) == False:
                self.memo_state = MemoState.Signoff
                self.save()
                user = User.find(userid=self.user_id)
                self.notify_signers(f"memo {user.username}-{self.number}-{self.version} has gone into signoff")
            else:
                self.memo_state = MemoState.Active
                self.save()
                self.obsolete_previous()
                user = User.find(userid=self.user_id)
                self.notify_distribution(f"memo {user.username}-{self.number}-{self.version} has been published")
   
        if self.memo_state == MemoState.Signoff:
            if MemoSignature.status(self.id):
                self.memo_state = MemoState.Active
                self.save()
                user = User.find(userid=self.user_id)
                self.notify_distribution(f"memo {user.username}-{self.number}-{self.version} has been published")
                self.obsolete_previous()
            else:
                current_app.logger.info(f"Signatures Still Required")


    # TODO: ARH
    def notify_distribution(self,message):
        current_app.logger.info(F"Notify Distribution {self.distribution} {message}")

    # TODO: ARH
    def notify_signers(self,message):
        current_app.logger.info(F"Notify signers {message}")

################################################################################
# State machine functions called by the viewcontroller
################################################################################


# Owner Function
    @staticmethod
    def create_revise(owner=None,delegate=None,memo_number=None):
        
        assert owner != None and delegate != None

# TODO: Enforce the security right here

        memo = Memo.query.join(User).filter(User.id==owner.id,Memo.number==memo_number).first()
 
        # create a new memo
        if memo_number == None or memo==None:
            memo_number = Memo.get_next_number(owner)
        
            new_memo = Memo(number = memo_number,\
                            version = 1,\
                            confidential = False,\
                            distribution = '',\
                            keywords = '',\
                            title = '',\
                            num_files = 0,\
                            user_id = owner.id,\
                            memo_state = MemoState.Draft,\
                            signers = '' )
            new_memo.save()
            return new_memo
       
        
        if memo.memo_state == MemoState.Draft:
            return memo
 
    # TODO: ARH the references copy doesnt work...
        # revise an existing memo
        new_memo = Memo(number = memo_number,\
                            version = memo.get_next_version(),\
                            confidential = memo.confidential,\
                            distribution = memo.distribution,\
                            keywords = memo.keywords,\
                            title = memo.title,\
                            num_files = 0,\
                            user_id = memo.user_id,\
                            memo_state = MemoState.Draft,\
                            signers = memo.signers )
        new_memo.save()
        return new_memo
    
# signer function
    def sign(self,signer=None,delegate=None):
        
        current_app.logger.info(f"signer = {signer} delegate={delegate}")
        if not self.can_sign(signer,delegate):
            return False
        
        MemoSignature.sign(self.id,signer,delegate)
        self.process_state()
        self.save()
        return True

# signer function     
    def unsign(self,signer=None,delegate=None):
        current_app.logger.info(f"signer = {signer} delegate={delegate}")
        
        if not self.can_unsign(signer,delegate):
            return False
        
        MemoSignature.unsign(self.id,signer,delegate)
        self.process_state()
        self.save()
        return True
       
# Owner Function       
    def obsolete(self,delegate=None):
        
        current_app.logger.info(f"Obsolete: {self} Delegate={delegate}")
        
        if not self.can_obsolete(delegate=delegate):
            return False
        
        self.memo_state = MemoState.Obsolete
        self.save()
        return True

# Owner Function
    def cancel(self,delegate=None):
        current_app.logger.info(f"Cancel: {self} Delegate={delegate}")
        
        if not self.can_cancel(delegate=delegate):
            return False
        
        current_app.logger.info(f"Canceling: {self} Delegate={delegate}")
        
        MemoFile.delete(self)
        # delete all of the files in that directory & the directory
        
        shutil.rmtree(self.get_fullpath())
        
        MemoReference.delete(self)
        MemoSignature.delete_signers(self)
        db.session.delete(self)
        db.session.commit()       
        current_app.logger.info(f"Canceled: {self} ")
        
        return True

# signer function
    def reject(self,signer=None,delegate=None):

        current_app.logger.info(f"signer = {signer} delegate={delegate}")
        if not self.can_reject(signer,delegate):
            return False
        
        
        self.memo_state = MemoState.Draft
        MemoSignature.unsign_all(self)
        self.save()
        self.notify_signers(f"Memo {self.user.username}-{self.number}-{self.version} has been rejected for {signer.username} by {delegate.username}")
        return True
    

################################################################################       
# End of State machine functions
################################################################################       

    @staticmethod
    def find(memo_id=None,username=None,memo_number=None,memo_version=0):
        
        if memo_id != None:
            return Memo.query.filter_by(id=memo_id).first()
            
             
        if memo_version == None:
            memo_version = 0

        current_app.logger.info(f"FIND: Looking for {username}/{memo_number}/{memo_version}")
        
        user = User.find(username=username)
        current_app.logger.info(f"Found user {user}")
        if user == None:
            return None

        if memo_version != 0:
            memo = Memo.query.join(User).filter(User.id==user.id,Memo.number==memo_number,Memo.version==memo_version).first()
            current_app.logger.info(f"Memo Status = {memo}")
        else:
            memo = Memo.query.join(User).filter(User.id==user.id,Memo.number==memo_number).order_by(Memo.version.desc()).first()
        
        
        current_app.logger.info(f"Found Memo id={memo}")
                                
        return memo

    @staticmethod
    def get_memo_list(username=None,memo_number=None,memo_version=None,pagesize=0,page=1):

        
        if memo_version:
            memo_list = Memo.query.join(User).filter(User.username==username,\
                                                Memo.number==memo_number,\
                                                Memo.version==memo_version)\
                                                    .paginate(page = page,per_page=pagesize)
        elif memo_number:
            memo_list = Memo.query.join(User).filter(User.username==username,Memo.number==memo_number)\
            .order_by(Memo.memo_date.desc()).paginate(page = page,per_page=pagesize)

        elif username:
            memo_list = Memo.query.join(User).filter(User.username==username,Memo.memo_state == MemoState.Active)\
            .order_by(Memo.memo_date.desc()).paginate(page = page,per_page=pagesize)
        else:
            memo_list = Memo.query.join(User).filter(Memo.memo_state == MemoState.Active)\
            .order_by(Memo.memo_date.desc()).paginate(page = page,per_page=pagesize)
    
        return memo_list

    @staticmethod
    def get_next_number(user=None):
        assert user!=None
        
        if user.next_memo == None:
            next_memo = 1
        else:
            next_memo = user.next_memo
        
        current_app.logger.info(f"Next Memo # = {next_memo}")
        memo_list = Memo.query.join(User).filter(User.username==user.username, Memo.number >= next_memo-1)\
            .order_by(Memo.number).all()
        
        current_app.logger.info(f"MemoList = {memo_list}")
        
        for memo in memo_list:
            if memo.number == next_memo:
                next_memo = next_memo + 1
                continue
            else:
                break
            
        current_app.logger.info(f"Next Memo Number = {next_memo}")
        
        return next_memo
    

    @staticmethod
    def get_inbox(user=None):
        
        if user == None:
            return None  # TODO: ARH... not really what you want to return
        
        page=1
        pagesize=10
        msigs = MemoSignature.get_signatures(user,signed=False)
        
        memolist = Memo.query.join(User).filter(Memo.memo_state==MemoState.Signoff,Memo.id.in_(msigs)).paginate(page = page,per_page=pagesize)      
        current_app.logger.info(f"Inbox for {user.username} = Items={len(memolist.items)} {memolist}")
        return memolist
    
    @staticmethod
    def get_drafts(user=None):
    
        if user == None:
            return None  # TODO: ARH... not really what you want to return
        
        page=1
        pagesize=10
        
        memolist = Memo.query.join(User).filter(Memo.memo_state==MemoState.Draft,User.id==user.id).paginate(page = page,per_page=pagesize)      
        current_app.logger.info(f"Drafts for {user.username} = Items={len(memolist.items)} {memolist}")
        return memolist