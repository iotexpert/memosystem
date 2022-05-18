
from flask_mail import Mail

def test_register(client, session):
    # Register new user
    response = client.post('/register', 
        data=dict(username='jdoe',email='john.doe@gmail.com',password='pass', confirm_password='pass', submit='Sign Up'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Your account has been created!' in response.data
    assert b'Log In' in response.data

    # Error on duplicate account or email
    response = client.post('/register', 
        data=dict(username='jdoe',email='john.doe@gmail.com',password='pass', confirm_password='pass', submit='Sign Up'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'That username is taken. Please choose a different one' in response.data
    assert b'That email is taken. Please choose a different one.' in response.data

    # attempt login with bad password
    response = client.post('/login', 
        data=dict(username='jdoe',password='bad pass', submit='Login'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Login Unsuccessful' in response.data

    # successful login
    response = client.post('/login', 
        data=dict(username='jdoe',password='pass', submit='Login'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: jdoe' in response.data
    assert b'Logout' in response.data

    # When logged in, /register redirects to home page
    response = client.get('/register',
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: jdoe' in response.data
    assert b'Logout' in response.data

    # When logged in, /login redirects to home page
    response = client.get('/login',
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: jdoe' in response.data
    assert b'Logout' in response.data

def test_account_access_admin(client, session):
    # login as admin
    response = client.post('/login',
                            data=dict(username='adminUser', password='u'),
                            follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: adminUser' in response.data

    # View page for self
    response = client.get('/account', follow_redirects=True)
    assert response.status_code == 200
    assert b'adminUser@gmail.com' in response.data
    assert b'Account Info' in response.data

    # View page for invalid account
    response = client.get('/account/badUser', follow_redirects=True)
    assert response.status_code == 404
    assert b'Account Info' not in response.data

    # View page for other account
    response = client.get('/account/avgUser', follow_redirects=True)
    assert response.status_code == 200
    assert b'avgUser@gmail.com' in response.data
    assert b'Account Info' in response.data

def test_account_access_nonadmin(client, session):
    # login as normal user
    response = client.post('/login',
                            data=dict(username='avgUser', password='u'),
                            follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: avgUser' in response.data

    # View page for self
    response = client.get('/account', follow_redirects=True)
    assert response.status_code == 200
    assert b'avgUser@gmail.com' in response.data
    assert b'Account Info' in response.data

    # View page for other account
    response = client.get('/account/adminUser', follow_redirects=True)
    assert response.status_code == 200
    assert b'adminUser@gmail.com' in response.data
    assert b'Account Info' in response.data

    # Send invalid update
    response = client.post('/account',
        data=dict(username="avgUser", email="adminUser@gmail.com", delegates="adminUser reallyBadUser", subscriptions="adminUser badUser"),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'avgUser@gmail.com' in response.data
    assert b'That email is taken.' in response.data
    assert b"Invalid users [&#39;reallyBadUser&#39;]" in response.data
    assert b"Invalid users [&#39;badUser&#39;]" in response.data

def test_reset(client, session):
    response = client.get('/reset_password', follow_redirects=True)
    assert response.status_code == 200
    assert b'Reset Password' in response.data

    response = client.get('/reset_password/BadTokenContent', follow_redirects=True)
    assert response.status_code == 200
    assert b'That is an invalid or expired token' in response.data
    assert b'Reset Password' in response.data

    response = client.post('/reset_password', 
        data=dict(email="badUser@gmail.com", submit="Request Password Reset"),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Reset Password' in response.data
    assert b'There is no account with that email. You must register first.' in response.data

    # mail = Mail()
    # with mail.record_messages() as outbox:

    #     response = client.post('/reset_password', 
    #         data=dict(email="adminUser@gmail.com", submit="Request Password Reset"),
    #         follow_redirects=True)
    #     assert response.status_code == 200
    #     assert b'Reset Password' in response.data

    #     assert len(outbox) == 1
    #     assert outbox[0].subject == "testing"
    
    response = client.post('/login',
                            data=dict(username='avgUser', password='u'),
                            follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: avgUser' in response.data
    
    response = client.get('/reset_password', follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: avgUser' in response.data

    response = client.get('/reset_password/BadTokenContent', follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: avgUser' in response.data