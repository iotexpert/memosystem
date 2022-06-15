from memos.models.User import Delegate, User, load_user
import time

"""
Verify functions in User.py

Assumes users exist: adminUser, readAllUser, avgUser
"""     
     
def test_delegate_delete_one(db, session):
    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')
    
    Delegate.add(adminUser, readAllUser)
    delegate = adminUser.delegates
    assert "avgUser" in delegate["usernames"]
    assert "readAllUser" in delegate["usernames"]
    assert len(delegate["users"]) == 2

    Delegate.delete(adminUser, readAllUser)

    delegate = adminUser.delegates
    assert "avgUser" in delegate["usernames"]
    assert "readAllUser" not in delegate["usernames"]
    assert len(delegate["users"]) == 1
     
def test_delegate_delete_all(db, session):
    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')
    
    Delegate.add(adminUser, readAllUser)
    delegate = adminUser.delegates
    assert "avgUser" in delegate["usernames"]
    assert "readAllUser" in delegate["usernames"]
    assert len(delegate["users"]) == 2

    Delegate.delete(adminUser)

    delegate = adminUser.delegates
    assert "avgUser" not in delegate["usernames"]
    assert "readAllUser" not in delegate["usernames"]
    assert len(delegate["users"]) == 0

def test_load_user(db, session):
    user = load_user('adminUser')
    assert user.get_id() == 'adminUser'
     
def test_user_get_id(db, session):
    user = User.find(username='adminUser')
    assert user.get_id() == 'adminUser'
     
def test_user_get_reset_token(db, session):
    user = User.find(username='adminUser')
    token1 = user.get_reset_token()
    time.sleep(1)
    token2 = user.get_reset_token()
    assert token1 != token2
    assert User.verify_reset_token(token2).username =='adminUser'
    assert User.verify_reset_token("xx") == None
     
def test_user_check_password(db, session):
    user = User.find(username='adminUser')
    assert user.check_password('x') == False
    assert user.check_password('u') == True
     
def test_user_delegate_for(db, session):
    user = User.find(username='avgUser')
    delegate = user.delegate_for
    assert delegate["usernames"].strip() == "adminUser"
    assert len(delegate["users"]) == 1
    assert delegate["users"][0].username == "adminUser"
     
def test_user_delegates(db, session):
    user = User.find(username='adminUser')
    delegate = user.delegates
    assert delegate["usernames"].strip() == "avgUser"
    assert len(delegate["users"]) == 1
    assert delegate["users"][0].username == "avgUser"
     
def test_user_is_delegate(db, session):
    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')
    
    assert adminUser.is_delegate() == False # delegate is None
    assert readAllUser.is_delegate(readAllUser) == True # Always delegate for self 
    assert readAllUser.is_delegate(adminUser) == True # Admin is always a valid delegate
    assert adminUser.is_delegate(readAllUser) == False # readAllUser is not a delegate or adminUser
    assert adminUser.is_delegate(avgUser) == True # avgUser is a delegate of adminUser

def test_user_subscriptions(db, session):
    adminUser = User.find(username='adminUser')
    
    adminUser.subscriptions = "readAllUser avgUser"
    assert "readAllUser" in adminUser.subscriptions
    assert "avgUser" in adminUser.subscriptions

def test_user_valid_usernames(db, session):
    v = User.valid_usernames("adminUser readAllUser, unknownUser, badUser@nowhere.com avgUser@gmail.com")
    assert "adminUser" in v["valid_usernames"]
    assert "readAllUser" in v["valid_usernames"]
    assert "avgUser" in v["valid_usernames"]
    assert "unknownUser" not in v["valid_usernames"]
    assert "unknownUser" in v["invalid_usernames"]
    assert "badUser" not in v["valid_usernames"]
    assert "badUser" not in v["invalid_usernames"]
    assert v["non_users"]
    assert len(v["valid_users"]) == 3

def test_user_is_admin(db, session):
    assert User.is_admin('adminUser')
    assert not User.is_admin('readAllUser')

def test_user_is_readAll(db, session):
    assert User.is_readAll('readAllUser')
    assert not User.is_readAll('avgUser')

def test_user_find(db, session):
    assert not User.find(None)
    assert not User.find('badUser')
    assert User.find('avgUser')
