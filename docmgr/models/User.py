from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from docmgr import db, login_manager
from flask_login import UserMixin
from docmgr import bcrypt
import re
import numpy
from sqlalchemy.orm import relationship

# TODO: ARH Why is this here
@login_manager.user_loader
def load_user(user_id):
    current_app.logger.info("calling the load user function")
    return User.query.get(int(user_id))

        
class Delegate(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)   # who is suppsoed to sign
    delegate_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=True)  # who actually performed the signature


    @staticmethod
    def is_delegate(owner,delegate):
        current_app.logger.info(f"Owner={owner} delegate={delegate}")
        if owner.id == delegate.id:
            return True
        
        d = Delegate.query.filter_by(owner_id=owner.id,delegate_id=delegate.id).first()
        if d:
            return True
        else:
            return False
    
    @staticmethod    
    def get_who_delegated(owner=None):
        delegate_list = Delegate.query.filter_by(owner_id=owner.id).all()
        current_app.logger.info(f"Delegate_list = {delegate_list}")
        rval = []
        for delegate_entry in delegate_list:
            user = User.find(userid=delegate_entry.delegate_id)
            rval.append(user)
        return rval
    
    @staticmethod    
    def add(owner=None,delegate=None):
        new_delegate = Delegate(owner_id=owner.id,delegate_id=delegate.id)
        
        db.session.add(new_delegate)
        db.session.commit()
        pass
    
    
    @staticmethod
    def delete(owner=None,delegate=None):
        if delegate == None:
            Delegate.query.filter_by(owner_id=owner.id).delete()
        else:
            Delegate.query.filter_by(owner_id=owner.id,delegate_id=delegate.id).delete()
    

# TODO: ARH consider userid and _id
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean,default=False)
        
    memos = db.relationship('Memo',backref=db.backref('user', lazy=True))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def check_password(self,check_pw):
        return bcrypt.check_password_hash(self.password, check_pw)


    @property
    def delegates(self):
        delegate_list = Delegate.get_who_delegated(owner=self)
        rval = ''
        for delegate in delegate_list:
            rval = rval + delegate.username + ' '
        return rval
        
    @delegates.setter
    def delegates(self,delegates):

        Delegate.delete(owner=self)
        for delegate_name in re.split(r'\s|\,',delegates):
            delegate = User.find(username=delegate_name)
            current_app.logger.info(f"Delegate = {delegate}")
            if delegate != None:
                Delegate.add(self,delegate)
    
    def get_who_delegated(self):
        return Delegate.get_who_delegated(self)
        
    
    # is the userid a valid delgate for "self"
    def is_delegate(self,delegate=None):
        return Delegate.is_delegate(self,delegate)
 
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
        invalid_users = []
        valid_users = []
        users = re.split(r'\s|\,',userlist)
        if '' in users: users.remove('')
        #current_app.logger.info(f"User = {users}")
        for username in users:
            if username != "" and User.find(username=username) == None:
                invalid_users.append(username)
            else:
                valid_users.append(username)

        valid_users = numpy.unique(valid_users)

        return {'valid_users':valid_users,'invalid_users':invalid_users}

    @staticmethod
    def is_admin(username=None):
        user = User.find(username=username)
        if user and user.admin:
            return True
        else:
            return False
        
