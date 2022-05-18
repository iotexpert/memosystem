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
