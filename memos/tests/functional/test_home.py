def test_home_page_get(client, session):
    """
    Test base / url
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'readAllUser memo 2-1' not in response.data
    assert b'readAllUser memo 1-3' not in response.data
    assert b'avgUser memo 3-1' in response.data
    assert b'avgUser memo 2-1' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo(client, session):
    """
    Test base /memo url
    """
    response = client.get('/memo')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'readAllUser memo 2-1' not in response.data
    assert b'readAllUser memo 1-3' not in response.data
    assert b'avgUser memo 3-1' in response.data
    assert b'avgUser memo 2-1' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo_avgUser(client, session):
    """
    Test /memo/<user> url
    """
    response = client.get('/memo/avgUser')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'avgUser memo 3-1' in response.data
    assert b'avgUser memo 2-1' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo_avgUser_1(client, session):
    """
    Test /memo/<user>/<memo#> url
    """
    response = client.get('/memo/avgUser/1')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'avgUser-1A' in response.data
    assert b'avgUser memo 1-1' in response.data
    assert b'avgUser-1B' in response.data
    assert b'avgUser memo 1-2' in response.data
    assert b'avgUser-1C' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo_avgUser_1_b(client, session):
    """
    Test /memo/<user>/<memo#> url
    """
    response = client.get('/memo/avgUser-1')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'avgUser-1A' in response.data
    assert b'avgUser memo 1-1' in response.data
    assert b'avgUser-1B' in response.data
    assert b'avgUser memo 1-2' in response.data
    assert b'avgUser-1C' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo_avgUser_1_3(client, session):
    """
    Test /memo/<user>/<memo#>/<version> url
    """
    response = client.get('/memo/avgUser/1/C')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'avgUser-1A' not in response.data
    assert b'avgUser memo 1-1' not in response.data
    assert b'avgUser-1B' not in response.data
    assert b'avgUser memo 1-2' not in response.data
    assert b'avgUser-1C' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo_avgUser_1_3b(client, session):
    """
    Test /memo/<user>-<memo#>-<version> url
    """
    response = client.get('/memo/avgUser-1-C')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'avgUser-1A' not in response.data
    assert b'avgUser memo 1-1' not in response.data
    assert b'avgUser-1B' not in response.data
    assert b'avgUser memo 1-2' not in response.data
    assert b'avgUser-1C' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo_avgUser_1_3c(client, session):
    """
    Test /memo/<user>/<memo#><version> url
    """
    response = client.get('/memo/avgUser/1C')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'avgUser-1A' not in response.data
    assert b'avgUser memo 1-1' not in response.data
    assert b'avgUser-1B' not in response.data
    assert b'avgUser memo 1-2' not in response.data
    assert b'avgUser-1C' in response.data
    assert b'avgUser memo 1-3' not in response.data

def test_home_page_get_memo_avgUser_1_4(client, session):
    """
    Test missing /memo/<user>/<memo#>/<version> url
    """
    response = client.get('/memo/avgUser/1/4')
    assert response.status_code == 200
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' in response.data
    assert b'avgUser-1A' not in response.data
    assert b'avgUser memo 1-1' not in response.data
    assert b'avgUser-1B' not in response.data
    assert b'avgUser memo 1-2' not in response.data
    assert b'avgUser-1C' not in response.data
    assert b'avgUser memo 1-3' not in response.data
    assert b'No memos match' in response.data

def test_valid_login_adminUser(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
    assert response.status_code == 200

    print(response.data)
    assert b'Account: adminUser' in response.data
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' not in response.data
    assert b'Register' not in response.data
    assert b'Logout' in response.data
    assert b'readAllUser memo 2-1' in response.data
    assert b'readAllUser memo 1-3' in response.data
    assert b'avgUser memo 3-1' in response.data
    assert b'avgUser memo 2-1' in response.data
    assert b'avgUser memo 1-3' in response.data

def test_valid_login_readAllUser(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
    assert response.status_code == 200

    print(response.data)
    assert b'Account: readAllUser' in response.data
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' not in response.data
    assert b'Register' not in response.data
    assert b'Logout' in response.data
    assert b'readAllUser memo 2-1' in response.data
    assert b'readAllUser memo 1-3' in response.data
    assert b'avgUser memo 3-1' in response.data
    assert b'avgUser memo 2-1' in response.data
    assert b'avgUser memo 1-3' in response.data

def test_valid_login_avgUser(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        
    assert response.status_code == 200

    print(response.data)
    assert b'Account: avgUser' in response.data
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' not in response.data
    assert b'Register' not in response.data
    assert b'Logout' in response.data
    assert b'readAllUser memo 2-1' not in response.data
    assert b'readAllUser memo 1-3' in response.data
    assert b'avgUser memo 3-1' in response.data
    assert b'avgUser memo 2-1' in response.data
    assert b'avgUser memo 1-3' in response.data

def test__for_avgUser(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        
    assert response.status_code == 200

    assert b'Account: avgUser' in response.data
    assert b'Memo System' in response.data
    assert b'Home' in response.data
    assert b'Search' in response.data
    assert b'Login' not in response.data
    assert b'Register' not in response.data
    assert b'Logout' in response.data
    assert b'readAllUser memo 2-1' not in response.data
    assert b'readAllUser memo 1-3' in response.data
    assert b'avgUser memo 3-1' in response.data
    assert b'avgUser memo 2-1' in response.data
    assert b'avgUser memo 1-3' in response.data

def test_help(client, session):
    """
    Test help link
    """
    with client:
        response = client.get('/help', follow_redirects=True)
        assert response.status_code == 200

        assert b'What is a Memo?' in response.data


def test_template(client, session):
    """
    Test base / url
    """
    response = client.get('/template')
    assert response.status_code == 200
    
    response = client.get('/template/asdf')
    assert response.status_code == 404
    
    response = client.get('/template/avgUser-1c')
    assert response.status_code == 403
    
    
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)

        response = client.get('/template/avgUser-1c?set',follow_redirects=True)
        assert response.status_code == 200
        
        response = client.get('/template')
        assert b"avgUser memo 1-3" in response.data
        
        response = client.get('/template/avgUser-1c?unset',follow_redirects=True)
        assert response.status_code == 200

        response = client.get('/template')
        assert b"avgUser memo 1-3" not in response.data
        

def test_pinned(client, session):
    """
    Test base / url
    """
    response = client.get('/pinned/')
    assert response.status_code == 404
    
    response = client.get('/pinned/asdf')
    assert response.status_code == 404
    
    response = client.get('/pinned/avgUser-1c')
    assert response.status_code == 403
    
    
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)

        response = client.get('/pinned/avgUser-1c?set',follow_redirects=True)
        assert response.status_code == 200
        
        response = client.get('/')
        assert b"bg-warning" in response.data
        
        response = client.get('/pinned/avgUser-1c?unset',follow_redirects=True)
        assert response.status_code == 200

        response = client.get('/')
        assert b"bg-warning" not in response.data
        
