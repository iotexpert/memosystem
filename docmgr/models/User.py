from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from docmgr import db, login_manager
from flask_login import UserMixin
from docmgr import bcrypt
import re
import numpy
from sqlalchemy.orm import relationship

from docmgr.models.MemoSubscription import MemoSubscription

# This is used by the flask UserMixin
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

        
class Delegate(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=False)   # who is suppsoed to sign
    delegate_id = db.Column(db.String(120), db.ForeignKey('user.username'),nullable=False)  # who is alloed to perform the signature


    @staticmethod
    def is_delegate(owner,delegate):
    #current_app.logger.info(f"Owner={owner} delegate={delegate}")
        if owner is None or delegate is None:
            return False
        if owner.username == delegate.username:
            return True
        
        if delegate.admin == True:
            return True
        
        d = Delegate.query.filter_by(owner_id=owner.username,delegate_id=delegate.username).first()
        if d:
            return True
        else:
            return False
    
    @staticmethod    
    def get_delegates(owner):
        """Lookup delegates owner has defined."""
        delegate_list = Delegate.query.filter_by(owner_id=owner.username).all()
        rval = []
        for delegate_entry in delegate_list:
            user = User.find(username=delegate_entry.delegate_id)
            rval.append(user)
        return rval
    
    @staticmethod    
    def get_delegated_users(delegate):
        """Lookup owners that have added this delegate."""
        delegate_list = Delegate.query.filter_by(delegate_id=delegate.username).all()
        rval = []
        for delegate_entry in delegate_list:
            user = User.find(username=delegate_entry.owner_id)
            rval.append(user)
        return rval
    
    @staticmethod    
    def add(owner, delegate):
        new_delegate = Delegate(owner_id=owner.username,delegate_id=delegate.username)
        
        db.session.add(new_delegate)
        db.session.commit()
        pass
    
    
    @staticmethod
    def delete(owner,delegate=None):
        if delegate == None:
            Delegate.query.filter_by(owner_id=owner.username).delete()
        else:
            Delegate.query.filter_by(owner_id=owner.username,delegate_id=delegate.username).delete()
    

class User(db.Model, UserMixin):
    username = db.Column(db.String(120), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean,default=False)
    readAll = db.Column(db.Boolean,default=False)
    pagesize = db.Column(db.Integer, nullable=False, default = 20)
    _subscriptions = db.Column(db.String(128))
        
    memos = db.relationship('Memo',backref=db.backref('user', lazy=True))
    history = db.relationship('MemoHistory',backref=db.backref('user', lazy=True))

    def get_id(self):
        return self.username

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def check_password(self,check_pw):
        return bcrypt.check_password_hash(self.password, check_pw)

    @property
    def delegate_for(self):
        """owners user is a delegate for"""
        delegate_list = Delegate.get_delegated_users(delegate=self)
        current_app.logger.info(f"Delegate List = {delegate_list}")
        rval = ''
        for delegate in delegate_list:
            rval = rval + delegate.username + ' '
        return {"usernames":rval,"users":delegate_list}

    @property
    def delegates(self):
        """delegates defined for this user"""
        delegate_list = Delegate.get_delegates(owner=self)
        current_app.logger.info(f"Delegate List = {delegate_list}")
        rval = ''
        for delegate in delegate_list:
            rval = rval + delegate.username + ' '
        return {"usernames":rval,"users":delegate_list}
        
    @delegates.setter
    def delegates(self,delegates):

        Delegate.delete(owner=self)
        for delegate_name in re.split(r'\s|\,|\t|\;|\:',delegates):
            delegate = User.find(username=delegate_name)
            if delegate != None:
                Delegate.add(self,delegate)
    
    # is the userid a valid delgate for "self"
    def is_delegate(self,delegate=None):
        return Delegate.is_delegate(self,delegate)
 
    @property
    def subscriptions(self):
        sublist = MemoSubscription.get(self)
        for sub in sublist:
            #current_app.logger.info(f"{sub.subscriber_id} {sub.subscription_id}")
            return self._subscriptions 
        
    @subscriptions.setter
    def subscriptions(self,sub_names):
        self._subscriptions = sub_names
        users = User.valid_usernames(sub_names)
        MemoSubscription.delete(self)
        for user in users['valid_users']:
            #current_app.logger.info(f"adding subscription {self} to {user}")
            ms = MemoSubscription(subscriber_id=self.username,subscription_id=user.username)
            db.session.add(ms)
            db.session.commit()
    
    @staticmethod
    def create_hash_pw(plaintext):
        return bcrypt.generate_password_hash(plaintext).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    @staticmethod
    def find(userid=None,username=None):
        """Find either the userid or the username ... if you sepcify both it will fail if you arent talking about the same user

        Args:
            userid ([int], optional): [The userid you are looking for ]. Defaults to None.
            username ([string], optional): [The username you are looking for]. Defaults to None.

        Returns:
            [User]: The User you are looking for... or None
        """
        #current_app.logger.info(f"User.find username={username} userid={userid}")

        u1 = None
        u2 = None
        if userid != None:
            u1 = User.query.filter_by(id=userid).first()
        if username != None:
            u2 = User.query.filter_by(username=username).first()

        #current_app.logger.info(f"Userfind U1={u1} U2={u2}")
        
        if u1 == None and u2 == None:
            return None
        
        if u1 != None and u2 == None:
            return u1
        
        if u1 == None and u2 != None:
            return u2

        if u1 == u2:
            #current_app.logger.info(f"return user find u1=u2 {u1}")
            return u1       

        raise RuntimeError('Failed impossible condition inside of User.find()')

    # this function takes a string of "users" where they are seperated by , or space and checks if they are valid
    @staticmethod
    def valid_usernames(userlist):
        invalid_usernames = []
        valid_usernames = []
        users = re.split(r'\s|\,',userlist)
        if '' in users: users.remove('')
        #current_app.logger.info(f"User = {users}")
        for username in users:
            user = User.find(username=username)
            if username != "" and  user == None:
                invalid_usernames.append(username)
            else:
                valid_usernames.append(username)

        valid_usernames = numpy.unique(valid_usernames)
        valid_users = []
        for username in valid_usernames:
            valid_users.append(User.find(username=username))

        return {'valid_usernames':valid_usernames,'invalid_usernames':invalid_usernames,'valid_users':valid_users}

    @staticmethod
    def is_admin(username=None):
        user = User.find(username=username)
        if user and user.admin:
            return True
        else:
            return False
        
    @staticmethod
    def is_readAll(username=None):
        user = User.find(username=username)
        if user and user.readAll:
            return True
        else:
            return False
        

    @staticmethod
    def get_pagesize(user):
        
        try:
            return user.pagesize
        except:
            return 10