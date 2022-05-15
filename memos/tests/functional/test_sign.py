def test_home_page_get(client, session):

    """
    Given:
    When:
    Then:
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Document Manager' in response.data
    
    

def test_valid_login_logout(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    with client:
        response = client.get('/login')
        response = client.post('/login',
                                data=dict(email='adminUser@gmail.com', password='u'),
                                follow_redirects=True)
    assert response.status_code == 200

    print(response.data)
    assert b'Account: admin' in response.data
#    assert b'Flask User Management' in response.data
#    assert b'Logout' in response.data
#    assert b'Login' not in response.data
#    assert b'Register' not in response.data
