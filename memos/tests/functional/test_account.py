def test_register(client, session):
    """
    Test base / url
    """
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

    response = client.post('/login', 
        data=dict(email='john.doe@gmail.com',password='pass', submit='Login'),
        follow_redirects=True)
    assert response.status_code == 200
    assert b'Account: jdoe' in response.data
    assert b'Logout' in response.data