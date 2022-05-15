"""
The model file for a Memo

"""
import re
import os
import shutil
import json
from datetime import datetime

from flask import current_app

from memos import db
from memos.models.User import User
from memos.models.MemoState import MemoState
from memos.models.MemoFile import MemoFile
from memos.models.MemoSignature import MemoSignature
from memos.models.MemoReference import MemoReference
from memos.models.MemoHistory import MemoHistory
from memos.models.MemoActivity import MemoActivity
from memos.revletter import b10_to_rev, rev_to_b10

class Memo(db.Model):
    """This class is the single interface to a "memo" and all of the "memos"
    """
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)                                      # Memo Number
    version = db.Column(db.String(2))                                   # A,B,..Z,AA,AB,...AZ,BA
    confidential = db.Column(db.Boolean, default=False)                 # if true only author, signer, distribution can read
    distribution = db.Column(db.String(128), default='')                # user names on the distribution
    keywords = db.Column(db.String(128), default='')                    # any keyword
    title = db.Column(db.String(128), nullable=False, default='')       # The title of the memo
    num_files = db.Column(db.Integer, default=0)                        # The number of files attached to the memo

    action_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # The last time anything happened
    create_date = db.Column(db.DateTime)    # when the memo was created
    submit_date = db.Column(db.DateTime)    # when the memo was most recently submitted  (from created)
    active_date = db.Column(db.DateTime)    # when the memo was moved to active state (from submitted)
    obsolete_date = db.Column(db.DateTime)  # when the memo was moved to obsolete state (from active)
    
    user_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=False)        # The key of the user who owns the memo
    _signers = db.Column(db.String(128),default='')                                 # the hidden list of signer usernames
    _references = db.Column(db.String(128),default='')                              # The hidden list of references
    memo_state = db.Column(db.Enum(MemoState))                                      # Draft, Signoff, Active, Obsolete

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # do custom initialization here

    def __repr__(self):
        return f"{self.user.username}-{self.number}{self.version}"

    def __str__(self):
        return f"{self.user.username}-{self.number}{self.version}"

########################################
# Permission Functions
########################################

    @staticmethod
    def can_create(owner=None, delegate=None):
        """Will return true if the delegate can create a memo for the owner"""

        if owner is None:
            return False

        if delegate is None:
            delegate = owner
       
        return owner.is_delegate(delegate=delegate)

    def can_revise(self, delegate=None):
        """Is the delgate allowed to update "this" memo?"""
        
        if delegate is None:
            return False
        
        if not self.user.is_delegate(delegate):
            return False

        if self.memo_state == MemoState.Active or self.memo_state == MemoState.Obsolete:
            return True

    def can_sign(self, signer=None, delegate=None):
        """Can this memo be signed by delegate for the signers"""
        
        if signer is None or delegate is None:
            return False

        if self.memo_state != MemoState.Signoff:
            return False

        if not signer.is_delegate(delegate=delegate):
            return False

        # The list of signers and if they have signed are kept in the MemoSignature table
        status = MemoSignature.is_signer(self.id,signer)
        return status['is_signer'] and not status['status']

    def can_unsign(self, signer=None, delegate=None):
        """Can this memo be unsigned by delegate for the signer """
        if signer is None or delegate is None:
            return False

        if self.memo_state != MemoState.Signoff:
            return False

        if not signer.is_delegate(delegate=delegate):
            return False

        status = MemoSignature.is_signer(self.id,signer)
        return status['is_signer'] and status['status']

    def can_obsolete(self, delegate=None):
        """ Can this memo be obsoleted by the delegate?  Only active memos can be obsoleted """
        if delegate is None:
            return False

        if not self.user.is_delegate(delegate):
            return False

        if self.memo_state == MemoState.Active:
            return True

        return False

    def can_cancel(self, delegate=None):
        """ can this memo be cancled by the delegate.  Only drafts memos can be canceled"""
        if delegate is None:
            return False

        if self.memo_state != MemoState.Draft:
            return False

        if not self.user.is_delegate(delegate=delegate):
            return False

        return True

    def can_reject(self, signer=None, delegate=None):
        """ can this memo be rejected by the delegate.  Only memos in signoff can be rejected"""
        if signer is None or delegate is None:
            return False

        if self.memo_state != MemoState.Signoff:
            return False

        if not signer.is_delegate(delegate):
            return False

        status = MemoSignature.is_signer(memo_id=self.id,signer=signer)

        # if you are a signer you can reject.. even if you have already signed
        return status['is_signer']

    def has_access(self, user=None):
        """This function will return True of the "username" has access to self"""

        # if it is not confidential than anyone can access
        if self.confidential == False:
            return True

        # at this point we know it is confidential so ... they must provide a username
        if user is None:
            return False

        # you alway have access to your own memo's
        if self.user.username == user.username:
            return True

        if user.admin:
            return True
        
        if user.readAll:
            return True

        # if the username is in the distribution list then provide access TODO: ARH do something better
        if user.username in re.split('\s|\,|\t|\;|\:',self.distribution):
            return True

        return False


########################################
# ??? Functions
########################################

    def get_fullpath(self):
        """ This function gives the os path to a file """    
        path = os.path.join(current_app.root_path,"static","memos",f"{self.user_id}",f"{self.number}",f"{self.version}")
        return path

    def get_relpath(self):
        """ Return the relative path of this memo """
        path = os.path.join("/static","memos",f"{self.user_id}",f"{self.number}",f"{self.version}")
        return path

    def get_files(self):
        """ Return a list of the files attached to this memo"""
        memo_list = MemoFile.query.filter_by(memo_id=self.id).all()
        return memo_list

    def saveJson(self):
        """ Create the JSON file which is a copy of all of the meta data """
        js = {}
        js['title']=self.title
        js['number']=self.number
        js['version']=self.version
        js['confidential']=self.confidential
        js['distribution']=self.distribution
        js['keywords']=self.keywords
        js['userid']=self.user_id
        js['memo_state']=f"{self.memo_state}"
        js['keywords']= self.keywords
        js['signers']=self.signers['signers']
        js['references']= self.references['ref_string']
        js['files']=[]
        for file in self.get_files():
            js['files'].append(file.filename)

        path = os.path.join(self.get_fullpath())
        #current_app.logger.info(f"Making Directory {path}")
        os.makedirs(path,exist_ok=True)
        #current_app.logger.info(f"Making Succeeded {path}")

        path = os.path.join(path,f"meta-{self.user_id}-{self.number}-{self.version}.json")
        f = open(path,"w")
        json.dump(js,f)
        f.close()

    @property
    def signers(self):
        # get the signers from the signing table and turn it back to a string and a list
        siglist = MemoSignature.get_signers(self)
        for sig in siglist:
            sig.signer = User.find(username=sig.signer_id)
            sig.delegate = User.find(username=sig.delegate_id)
        return {'signers':self._signers,'siglist':siglist}

    @signers.setter
    def signers(self,signer_names):
        self._signers = signer_names
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
        for memo_ref in re.split(r'\s|\,|\t|\;|\:',references):
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
            memo = Memo.find(username=username,memo_number=memo_number,memo_version=memo_version)
            current_app.logger.info(f"Memo = {memo}")
            if memo != None and (memo.memo_state == MemoState.Active or memo.memo_state == MemoState.Obsolete):
                valid_memos.append(memo)
                valid_refs.append(memo_ref)
            else:
                invalid.append(memo_ref)
        
        rval = {'valid_refs':valid_refs, 'valid_memos' : valid_memos,'invalid':invalid}
        return rval
            
    @property
    def references(self):
        # this function will return a list of refeference objects + a string of the references
        refs = MemoReference.get_refs(self)
        rval = []
        for ref in refs:
            userid=ref[0]
            memo = Memo.find(username=userid,memo_number=ref[1],memo_version=ref[2])
            if ref[2] == None:
                refstring=f"{userid}-{ref[1]}"
            else:
                refstring=f"{userid}-{ref[1]}-{ref[2]}"
            rval.append((refstring,memo))
        return {'reflist':rval,'ref_string':self._references}
    
    @references.setter
    def references(self,references):
        self._references = references

        refs = Memo.valid_references(references)
        for i in range(len(refs['valid_refs'])):
            parsed_ref = Memo.parse_reference(refs['valid_refs'][i])
            user = User.find(username=parsed_ref[0])
            MemoReference.add_ref(self.id,ref_user_id=user.username,ref_memo_number=parsed_ref[1],ref_memo_version=parsed_ref[2])

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
            return b10_to_rev(rev_to_b10(memo.version)+1)

        return b10_to_rev(1) # also known as 'A'

    def save(self):
        db.session.add(self)
        db.session.commit()
        self.saveJson()


################################################################################       
# functions used to process the state   
# these function would classiavally be called private
################################################################################       

    def obsolete_previous(self,acting=None):
        prev_list = Memo.query.join(User).filter(Memo.number == self.number,Memo.version != self.version).all()
        for memo in prev_list:
            if memo.memo_state == MemoState.Active:
                memo.memo_state = MemoState.Obsolete
                MemoHistory.activity(memo=memo,memo_activity=MemoActivity.Obsolete,user=acting)
                memo.save()

    # This function is called when:
    # 1- a valid draft is created
    # 2- a signature happens
    # 3- an unsign happens
    def process_state(self,acting=None):
        if self.memo_state == MemoState.Draft:
            if MemoSignature.status(self.id) == False:
                self.memo_state = MemoState.Signoff
                self.submit_date = datetime.utcnow()
                MemoHistory.activity(memo=self,memo_activity=MemoActivity.Signoff,user=acting)
                self.notify_signers(f"memo {self.user.username}-{self.number}-{self.version} has gone into signoff")
            else:
                self.memo_state = MemoState.Active
                self.active_date = datetime.utcnow()
                MemoHistory.activity(memo=self,memo_activity=MemoActivity.Activate,user=acting)
                self.obsolete_previous(acting=acting)
                self.notify_distribution(f"memo {self.user.username}-{self.number}-{self.version} has been published")
   
        if self.memo_state == MemoState.Signoff:
            if MemoSignature.status(self.id):
                self.memo_state = MemoState.Active
                self.active_date = datetime.utcnow()
                self.notify_distribution(f"memo {self.user.username}-{self.number}-{self.version} has been published")
                MemoHistory.activity(memo=self,memo_activity=MemoActivity.Activate,user=acting)

                self.obsolete_previous(acting=acting)
            else:
                current_app.logger.info(f"Signatures Still Required")
        
        self.action_date = datetime.utcnow()
        self.save()


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
        """ This function will return None or a new Memo if the owner/delgate and revise this memo """        
        assert owner != None and delegate != None
        if owner == None or delegate == None:
            return None
        
        if owner.is_delegate(delegate) != True:
            return None

        memo = Memo.query.join(User).filter(User.username==owner.username,Memo.number==memo_number).order_by(Memo.version.desc()).first()
 
        # create a new memo (i.e. not a new version of an existing memo)
        if memo_number == None or memo==None:
            memo_number = Memo.get_next_number(owner)
        
            new_memo = Memo(number = memo_number,\
                            version = 'A',\
                            confidential = False,\
                            distribution = '',\
                            keywords = '',\
                            title = '',\
                            num_files = 0,\
                            user_id = owner.username,\
                            memo_state = MemoState.Draft,\
                            action_date = datetime.utcnow(),\
                            create_date = datetime.utcnow(),\
                            signers = '' )
            
            new_memo.save()
            MemoHistory.activity(memo=new_memo,memo_activity=MemoActivity.Create,user=delegate)
            
            current_app.logger.info(f"Creating new memo {new_memo}")
            return new_memo
       
        
        if memo.memo_state == MemoState.Draft:
            current_app.logger.info(f"Found a draft memo {memo}")
            return memo
 
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
                            action_date = datetime.utcnow(),\
                            create_date = datetime.utcnow(),\
                             )
        new_memo.save()
        new_memo.references = memo.references['ref_string']  # cannot be done until there is an id assigned by the save
        new_memo.signers = memo._signers                     # cannot be done until there is an id assigned by the save
        new_memo.save()
        MemoHistory.activity(memo=new_memo,memo_activity=MemoActivity.Create,user=delegate)
        return new_memo

# signer function
    def sign(self,signer=None,delegate=None):

        current_app.logger.info(f"signer = {signer} delegate={delegate}")
        if not self.can_sign(signer,delegate):
            current_app.logger.info("NOT!!@ allowed to sign")
            return False
        
        current_app.logger.info("allowed to sign")
        MemoSignature.sign(self.id,signer,delegate)
        MemoHistory.activity(memo=self,user=delegate,memo_activity=MemoActivity.Sign)
        self.process_state(acting=delegate)
        return True

# signer function     
    def unsign(self,signer=None,delegate=None):
        
        if not self.can_unsign(signer,delegate):
            return False
        
        MemoSignature.unsign(self.id,signer,delegate)
        MemoHistory.activity(memo=self,user=delegate,memo_activity=MemoActivity.Unsign)
        self.process_state(acting=delegate)
        return True
       
# Owner Function       
    def obsolete(self,delegate=None):
        
        current_app.logger.info(f"Obsolete: {self} Delegate={delegate}")
        
        if not self.can_obsolete(delegate=delegate):
            return False
        
        self.memo_state = MemoState.Obsolete
        self.action_date = datetime.utcnow()
        self.obsolete_date = datetime.utcnow()
        MemoHistory.activity(memo=self,user=delegate,memo_activity=MemoActivity.Obsolete)
        self.save()
        return True

# Owner Function
    def cancel(self,delegate=None):
        current_app.logger.info(f"Cancel: {self} Delegate={delegate}")
    
        memostring = f"{self}"
        
        if not self.can_cancel(delegate=delegate):
            return False
        
        
        MemoFile.delete(self)
        # delete all of the files in that directory & the directory
        
        shutil.rmtree(self.get_fullpath())
        
        MemoReference.delete(self)
        MemoSignature.delete_signers(self)
        MemoHistory.activity(memo=self,user=delegate,memo_activity=MemoActivity.Cancel)

        db.session.delete(self)
        db.session.commit()       
        current_app.logger.info(f"Canceling")
        
        return True

# signer function
    def reject(self,signer=None,delegate=None):

        current_app.logger.info(f"signer = {signer} delegate={delegate}")
        if not self.can_reject(signer,delegate):
            return False
        
        
        self.memo_state = MemoState.Draft
        self.action_date = datetime.utcnow()
        self.submit_date = None
        self.active_date = None
        self.obsolete_date = None
        MemoHistory.activity(memo=self,memo_activity=MemoActivity.Reject,user=delegate)
        MemoSignature.unsign_all(self)
        self.save()
        self.notify_signers(f"Memo {self.user.username}-{self.number}-{self.version} has been rejected for {signer.username} by {delegate.username}")
        return True
    

################################################################################       
# End of State machine functions
################################################################################       

    @staticmethod
    def find(memo_id=None,username=None,memo_number=None,memo_version=None):
        
        if memo_id != None:
            return Memo.query.filter_by(id=memo_id).first()

        current_app.logger.info(f"FIND: Looking for {username}/{memo_number}/{memo_version}")
        
        user = User.find(username=username)
        current_app.logger.info(f"Found user {user}")
        if user == None:
            return None

        if memo_version != None:
            memo = Memo.query.join(User).filter(User.username==user.username,Memo.number==memo_number,Memo.version==memo_version).first()
            current_app.logger.info(f"Memo Status = {memo}")
        else:
            memo = Memo.query.join(User).filter(User.username==user.username,Memo.number==memo_number).order_by(Memo.version.desc()).first()
        
        
        current_app.logger.info(f"Found Memo id={memo}")
                                
        return memo

    @staticmethod
    def get_memo_list(username=None,memo_number=None,memo_version=None,page=1,pagesize=None):

        if memo_version:
            memo_list = Memo.query.join(User).filter(User.username==username,\
                                                Memo.number==memo_number,\
                                                Memo.version==memo_version)\
                                                    .paginate(page = page,per_page=pagesize)
        elif memo_number:
            memo_list = Memo.query.join(User).filter(User.username==username,Memo.number==memo_number)\
            .order_by(Memo.action_date.desc()).paginate(page = page,per_page=pagesize)

        elif username:
            memo_list = Memo.query.join(User).filter(User.username==username,Memo.memo_state == MemoState.Active)\
            .order_by(Memo.action_date.desc()).paginate(page = page,per_page=pagesize)
        else:
            memo_list = Memo.query.join(User).filter(Memo.memo_state == MemoState.Active)\
            .order_by(Memo.action_date.desc()).paginate(page = page,per_page=pagesize)
    
        return memo_list
    
    @staticmethod 
    def search(title=None,keywords=None,page=1,pagesize=None):
        current_app.logger.info(f"Search title={title}")
        if title != None:
            memo_list = Memo.query.filter(Memo.title.like(f"%{title}%")).order_by(Memo.action_date.desc()).paginate(page = page,per_page=pagesize)
        
        if keywords != None:
            memo_list = Memo.query.filter(Memo.keywords.like(f"%{keywords}%")).order_by(Memo.action_date.desc()).paginate(page = page,per_page=pagesize)
            
        return memo_list

    @staticmethod   
    def get_next_number(user=None):
        assert user!=None
                
        memo_list = Memo.query.join(User).filter(User.username==user.username)\
            .order_by(Memo.number.desc()).first()
        
        if memo_list == None:
            return 1
        return memo_list.number+1
        

    @staticmethod
    def get_inbox(user=None,page=1,pagesize=None):
        
        assert user!=None,"User must not be none"
        if user == None:
            return None
        
        msigs = MemoSignature.get_signatures(user,signed=False)
        
        memolist = Memo.query.join(User).filter(Memo.memo_state==MemoState.Signoff,Memo.id.in_(msigs)).order_by(Memo.action_date.desc()).paginate(page = page,per_page=pagesize)      
        current_app.logger.info(f"Inbox for {user.username} = Items={len(memolist.items)} {memolist}")
        return memolist
    
    @staticmethod
    def get_drafts(user=None,page=1,pagesize=None):
    
        assert user!=None,"User must not be none"
        if user == None:
            return None
        
        memolist = Memo.query.join(User).filter(Memo.memo_state==MemoState.Draft,User.username==user.username).order_by(Memo.action_date.desc()).paginate(page = page,per_page=pagesize)      
        return memolist