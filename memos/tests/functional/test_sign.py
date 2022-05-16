import io
import re

def test_cancel(client, session):
    """
    Flow:
        login
        Use 'New' to create new memo
        Goto 'Drafts' to view memo created
        'Cancel' memo verify cancel message displayed
        Got to 'Drafts' verify memo no longer there
    """
    with client:
        response = client.post('/login',
                                data=dict(email='avgUser@gmail.com', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data
        
        response = client.get('/cu/memo')
        assert response.status_code == 200
        assert b'New Memo avgUser-4A' in response.data
        
        response = client.get('/drafts')
        assert response.status_code == 200
        assert b'avgUser-4A' in response.data
        assert b'/cancel/memo/avgUser/4/A' in response.data
        
        response = client.get('/cancel/memo/avgUser/4/A', follow_redirects=True)
        assert response.status_code == 200
        assert b'Canceled avgUser-4A' in response.data
        
        response = client.get('/drafts')
        assert response.status_code == 200
        assert b'avgUser-4A' not in response.data
        assert b'/cancel/memmo/avgUser/4/A' not in response.data
    
def test_publish_2_files(client, session):
    """
    Flow:
        login
        Use 'New' to create new memo
        - Fill in form with two files
        - Submit
        Memo listed on result
        Select memo ?detail
        - Link to files present
        Download files to verify
    """
    with client:
        response = client.post('/login',
                                data=dict(email='readAllUser@gmail.com', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data
        
        response = client.get('/cu/memo')
        assert response.status_code == 200
        assert b'New Memo readAllUser-5A' in response.data
        
        response = client.post('/cu/memo/readAllUser/5',
                                data=dict(
                                    username='readAllUser',
                                    memo_number=5,
                                    memo_version='A',
                                    title='Test of memo for readAllUser #4 rev A', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='',
                                    references='',
                                    confidential=True,
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    memodoc2=(io.BytesIO(b"file content two"), 'file_two.txt'),
                                    submit='submit'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser-5A' in response.data
        assert b'/memo/readAllUser/5/A?detail' in response.data
        
        response = client.get('/memo/readAllUser/5/A?detail', follow_redirects=True)
        assert response.status_code == 200
        assert b'file_one.txt' in response.data
        assert b'file_two.txt' in response.data

        file_one_url = re.search('href="([^<>]+?)">file_one.txt', str(response.data)).group(1)
        file_two_url = re.search('href="([^<>]+?)">file_two.txt', str(response.data)).group(1)

        response = client.get(file_one_url, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content one' in response.data
        response = client.get(file_two_url, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content two' in response.data

        # Verify error on bad file name
        response = client.get(file_two_url+'a', follow_redirects=True)
        assert response.status_code == 404

        response = client.get('/logout',
                                follow_redirects=True)
        assert response.status_code == 200

        # Verify error on no access
        response = client.get(file_two_url, follow_redirects=True)
        assert response.status_code == 403

