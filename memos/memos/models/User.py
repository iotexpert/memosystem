import datetime
import email
import jwt
import numpy
import os
import re
from flask import current_app
from flask_login import UserMixin
from memos import bcrypt, db, login_manager
from memos.extensions import ldap

from memos.models.MemoSubscription import MemoSubscription

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
        pass
    
    
    @staticmethod
    def delete(owner,delegate=None):
        if delegate == None:
            Delegate.query.filter_by(owner_id=owner.username).delete()
        else:
            Delegate.query.filter_by(owner_id=owner.username,delegate_id=delegate.username).delete()
    

class User(db.Model, UserMixin):
    username = db.Column(db.String(120), primary_key=True)
    email = db.Column(db.String(120))
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean,default=False)
    readAll = db.Column(db.Boolean,default=False)
    pagesize = db.Column(db.Integer, nullable=False, default = 10)
        
    memos = db.relationship('Memo',backref=db.backref('user', lazy=True))
    history = db.relationship('MemoHistory',backref=db.backref('user', lazy=True))

    def get_id(self):
        return self.username

    def get_reset_token(self, expires_sec=1800):
        reset_token = jwt.encode(
            {
                "confirm": self.username,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                       + datetime.timedelta(seconds=expires_sec)
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return reset_token

    def check_password(self,check_pw):
        if ldap: #pragma nocover  -- testing ldap is very environment centric.
            try:
                ldap_user = ldap.get_object_details(self.username)
            except:
                return False

            self.admin = False
            self.readAll = False
            admin_groups = os.environ["LDAP_ADMIN_GRP"].split(";")
            readAll_groups = os.environ["LDAP_READ_GRP"].split(";")
            if 'memberOf' in ldap_user and isinstance(ldap_user['memberOf'], list):
                for grp in ldap_user['memberOf']:
                    grp = str(grp, 'utf-8')
                    for aGrp in admin_groups:
                        if grp.startswith(aGrp) : self.admin = True
                    for rGrp in readAll_groups:
                        if grp.startswith(rGrp) : self.readAll = True   
            return ldap.bind_user(self.username, check_pw)

        try:
            return bcrypt.check_password_hash(self.password, check_pw)
        except:  # pragma nocover - blanked password from ldap creation has a 'bad salt'
            return False
        

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
        l = []
        for sub in sublist:
            l.append( sub.subscription_id)
        return ' '.join(l)
        
    @subscriptions.setter
    def subscriptions(self,sub_names):
        self._subscriptions = sub_names
        users = User.valid_usernames(sub_names)
        MemoSubscription.delete(self)
        for user in users['valid_users']:
            ms = MemoSubscription(subscriber_id=self.username,subscription_id=user.username)
            db.session.add(ms)
    
    @staticmethod
    def create_hash_pw(plaintext):
        return bcrypt.generate_password_hash(plaintext).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):        
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                leeway=datetime.timedelta(seconds=10),
                algorithms=["HS256"]
            )
        except:
            return None

        return User.query.get(data.get('confirm'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    @staticmethod
    def find(username):
        """Lookup user by username

        Returns:
            [User]: The User you are looking for... or None
        """
        if username is None:
            return None
        user = User.query.filter_by(username=username).first()
        if user is None and ldap: #pragma nocover  -- testing ldap is very environment centric.
            try:
                ldap_user = ldap.get_object_details(username)
                if ldap_user is None:
                    return None
                user = User(username=ldap_user[os.environ["LDAP_USER_NAME"]][0].decode('ASCII'), 
                email=ldap_user[os.environ["LDAP_EMAIL"]][0].decode('ASCII'), password='xx')
                db.session.add(user)
                
            except:
                return None
                


            # If we validated a user with ldap, Update their permissions from LDAP groups.
            if ldap_user: #pragma nocover  -- testing ldap is very environment centric.
                user.admin = False
                user.readAll = False
                admin_groups = os.environ["LDAP_ADMIN_GRP"].split(";")
                readAll_groups = os.environ["LDAP_READ_GRP"].split(";")
                if 'memberOf' in ldap_user and isinstance(ldap_user['memberOf'], list):
                    for grp in ldap_user['memberOf']:
                        grp = str(grp, 'utf-8')
                        for aGrp in admin_groups:
                            if grp.startswith(aGrp) : user.admin = True
                        for rGrp in readAll_groups:
                            if grp.startswith(rGrp) : user.readAll = True
                        
        return user

    # this function takes a string of "users" where they are seperated by , or space and checks if they are valid
    @staticmethod
    def valid_usernames(userlist):
        invalid_usernames = []
        valid_usernames = []
        email_addrs = []
        has_non_users = False
        users = re.split('\s|\,|\t|\;|\:',userlist)
        while '' in users: users.remove('')

        for username in users:            
            # See if an email is listed.
            email_match = re.fullmatch('^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$', username)
            if email_match:
                email_addrs.append(str(email_match[0]))
                user = User.query.filter_by(email=email_match[0]).first()
                if user == None:
                    has_non_users = True
                else:
                    valid_usernames.append(user.username)
            else:
                user = User.find(username=username)
                if user == None:
                    invalid_usernames.append(username)
                    has_non_users = True
                else:
                    valid_usernames.append(user.username)
                    email_addrs.append(str(user.email))

        email_addrs = numpy.unique(email_addrs)
        valid_usernames = numpy.unique(valid_usernames)
        valid_users = []
        for username in valid_usernames:
            valid_users.append(User.find(username=username))

        return {
            'valid_usernames':valid_usernames,
            'invalid_usernames':invalid_usernames,
            'valid_users':valid_users,
            'email_addrs':email_addrs,
            'non_users':has_non_users
            }

    @staticmethod
    def is_admin(username):
        user = User.find(username=username)
        if user and user.admin:
            return True
        else:
            return False
        
    @staticmethod
    def is_readAll(username):
        user = User.find(username=username)
        if user and user.readAll:
            return True
        else:
            return False        

    @staticmethod
    def get_pagesize(user):    
        if hasattr(user, 'pagesize'):    
            return user.pagesize
        else:
            return 20