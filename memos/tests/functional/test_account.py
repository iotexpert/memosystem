import re
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

    # Update page for other account
    with open('tests/resources/JPEG_example_JPG_RIP_001.jpg', 'rb') as fh:
        response = client.post('/account/avgUser',
            data=dict(admin=True,readAll=True,email="avgUser@updated.com",
                delegates="adminUser", subscriptions="adminUser", pagesize=15, picture=(fh, 'JPEG_example_JPG_RIP_001.jpg')),
            follow_redirects=True)
    assert response.status_code == 200
    assert b'avgUser@updated.com' in response.data
    assert b'Account Info' in response.data
    assert b'Your account has been updated!' in response.data

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
    assert b"Invalid users [&#39;reallyBadUser&#39;]" in response.data
    assert b"Invalid users [&#39;badUser&#39;]" in response.data

    # Update page for other account
    with open('tests/resources/JPEG_example_JPG_RIP_001.jpg', 'rb') as fh:
        response = client.post('/account/adminUser',
            data=dict(admin=True,readAll=True,email="avgUser@updated.com",
                delegates="adminUser", subscriptions="adminUser", pagesize=15, picture=(fh, 'JPEG_example_JPG_RIP_001.jpg')),
            follow_redirects=True)
    assert response.status_code == 403
    assert b'403' in response.data
    assert b'Account Info' not in response.data
    assert b'Your account has been updated!' not in response.data

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

    response = client.post('/reset_password', 
        data=dict(email="avgUser2@gmail.com", submit="Request Password Reset"),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Reset Password' in response.data
    assert b'That email is not unique' in response.data

    response = client.post('/login',
                            data=dict(username='avgUser', password='u'),
                            follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: avgUser' in response.data
    
    response = client.get('/reset_password', follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: avgUser' in response.data

    response = client.get('/reset_password/DoNotCare.UserLoggedIn', follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: avgUser' in response.data
    
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

    response = client.get('/reset_password/BadTokenContent', follow_redirects=True)
    assert response.status_code == 200
    assert b'invalid or expired token' in response.data
    assert b'Reset Password' in response.data

    mail = Mail()
    with mail.record_messages() as outbox:
        response = client.post('/reset_password', 
            data=dict(email="adminUser@gmail.com", submit="Request Password Reset"),
            follow_redirects=True)
        assert response.status_code == 200
        assert b'An email has been sent' in response.data

        assert len(outbox) == 1
        assert outbox[0].subject == "Password Reset Request"
        token_grp = re.search('reset_password/(.*?)\n', outbox[0].body)
        assert token_grp
        token = token_grp.group(1)
        assert len(token) > 20

    response = client.get(f'/reset_password/{token}', follow_redirects=True)
    assert response.status_code == 200
    assert not b'invalid or expired token' in response.data
    assert b'Reset Password' in response.data

    response = client.post(f'/reset_password/{token}',
                            data=dict(password='p', confirm_password='p'),
                            follow_redirects=True)
    assert response.status_code == 200
    assert b'Your password has been updated!' in response.data

    response = client.post('/login',
                            data=dict(username='adminUser', password='p'),
                            follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: adminUser' in response.data
    