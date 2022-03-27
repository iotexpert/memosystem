"""_summary_

Raises:
    RuntimeError: _description_

Returns:
    _type_: _description_
    
"""
import enum
import re
import numpy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin

from docmgr import db, login_manager
from docmgr import bcrypt
from docmgr.models.MemoSubscription import MemoSubscription

# This is used by the flask UserMixin
@login_manager.user_loader
def load_user(user_id):
    """This function is called by the flask UserMixin

    Args:
        user_id (int): The userid of the User object you are looking

    Returns:
        User: The User who's userid = user_id 
    """
    return User.query.get(int(user_id))

class Role(enum.Enum):
    """The Role enumeration is used to identify the legal roles in the system adminitrator, 
    delegate, read etc for the authorizaitons table

    Args:
        enum (Int)
    """
    ADMIN    = 1
    DELEGATE = 2


class Authorization(db.Model):
    """_summary_

    Args:
        db (_type_): _description_

    Returns:
        _type_: _description_
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)   # who is suppsoed to sign
    role = db.Column(db.Enum(Role))      # For some reason the attribute names "activity" and "action" are illegal
    for_userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # who actually performed the signature
   
    
    @staticmethod
    def has_role(user, for_user, role):
        """This function looks up the "user" to see if they have the "role" optionally
        for the "delegate"

        Args:
            user (User): The user you are looking for
            for_user (User): The user you are looking for
            role (Role): The specific role

        Returns:
            Boolean: True if the user has the role, False if Not
        """
        if role is None:
            return False
        
        if for_user is None:
            role = Authorization.query.filter_by(user_id=user.id, role=role).first()
        else:
            role = Authorization.query.filter_by(user_id=user.id, 
                                                 for_userid=for_user.id, role=role).first()

        
        return True
        
    @staticmethod
    def add(user, for_user, role):
        """Add a new role for the "user" as applies to "for_user"
        For example for user1 to delegate to user2  call
        add(user2, user1, Role.DELEGATE)

        Args:
            user (User): The user you want to create a role for
            for_user (User): The user you want the new rule to apply to
            role (Role): The specific role
        """
        if for_user is None:
            for_userid = None
        else:
            for_userid = for_user.id

        new_auth = Authorization(user_id=user.id, for_userid=for_userid, role=role)
        db.session.add(new_auth)
        db.session.commit()

    @staticmethod
    def delete(user=None, for_user=None, role=None):
        
        if user is None and for_user is None:  # probably should assert
            return
        
        if user is None and for_user is not None:
            Authorization.query.filter_by(for_userid=for_user.id, role=role).delete()
            return
        
        if user is not None and for_user is None:
            Authorization.query.filter_by(user_id=user.id, role=role).delete()
            return
        
        if user is not None and for_user is not None:
            Authorization.query.filter_by(user_id=user.id, for_userid=for_user.id, role=role).delete()
            return
 
    @staticmethod
    def get_authorized_users(user, role):
        auth_list = Authorization.query.filter_by(user_id=user.id, role=role).all()
        rval = []
        for auth in auth_list:
            user = User.find(userid=auth.for_userid)
            rval.append(user)
        return rval

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    pagesize = db.Column(db.Integer, nullable=False, default = 20)
    _subscriptions = db.Column(db.String(128))
        
    memos = db.relationship('Memo',backref=db.backref('user', lazy=True))
    history = db.relationship('MemoHistory',backref=db.backref('user', lazy=True))


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def check_password(self,check_pw):
        return bcrypt.check_password_hash(self.password, check_pw)


    @property
    def delegates(self):
        delegate_list = Authorization.get_authorized_users(self, Role.DELEGATE)
        current_app.logger.info(f"Delegate List = {delegate_list}")
        rval = ''
        for delegate in delegate_list:
            rval = rval + delegate.username + ' '
        return {"usernames":rval, "users":delegate_list}
        
    @delegates.setter
    def delegates(self, delegates):
        current_app.logger.info("In setter")
        Authorization.delete(None, self, Role.DELEGATE)
        for delegate_name in re.split(r'\s|\,|\t|\;|\:',delegates):
            delegate = User.find(username=delegate_name)
            if delegate is not None:
                Authorization.add(delegate, self, Role.DELEGATE)
       
    # is the userid a valid delgate for "self"
    def is_delegate(self, delegate=None):
        current_app.logger.info(f"is delegate self={self.id} delegate={delegate.id}")
        if delegate is not None and self.id == delegate.id:
            return True
        
        return Authorization.has_role(delegate, self, Role.DELEGATE)
 
    @property
    def subscriptions(self):
        sublist = MemoSubscription.get(self)
        for sub in sublist:
            #current_app.logger.info(f"{sub.subscriber_id} {sub.subscription_id}")
            return self._subscriptions 
        
    @subscriptions.setter
    def subscriptions(self, sub_names):
        self._subscriptions = sub_names
        users = User.valid_usernames(sub_names)
        MemoSubscription.delete(self)
        for user in users['valid_users']:
            #current_app.logger.info(f"adding subscription {self} to {user}")
            ms = MemoSubscription(subscriber_id=self.id,subscription_id=user.id)
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
        if userid is not None:
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

    def is_admin(self):
        return Authorization.has_role(self, None, Role.ADMIN)


    @staticmethod
    def get_pagesize(user):
        """

        Args:
            user (_type_): _description_

        Returns:
            _type_: _description_
        """
        if user is None or user.is_anonymous or user.pagesize is None:
            return 10
        return user.pagesize
