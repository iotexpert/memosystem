import io
import re

def test_main(client, session):
    # Main form for admins
    with client:
        # login as normal user
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data

        response = client.get('/admin', 
            follow_redirects=True)
        assert response.status_code == 403

        response = client.get('/logout', 
            follow_redirects=True)
        assert response.status_code == 200
        
        # login as admin user
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data

        response = client.get('/admin', 
            follow_redirects=True)
        assert response.status_code == 200
        assert b'name="source"' in response.data
        assert b'name="destination"' in response.data
        assert b'/admin/rename' in response.data
        assert b'name="delete_ref"' in response.data
        assert b'/admin/delete' in response.data

def test_rename(client, session):
    # Test rename function
    with client:
        # login as normal user
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data
        
        #Create a memo with files to be copied
        response = client.get('/cu/memo')
        assert response.status_code == 200
        assert b'New Memo readAllUser-5A' in response.data
        
        response = client.post('/cu/memo/readAllUser/5',
                                data=dict(
                                    username='readAllUser',
                                    memo_number=5,
                                    memo_version='A',
                                    title='Test of memo for readAllUser #5 rev A', 
                                    distribution='adminUser',    
                                    keywords='LiIon',
                                    signers='avgUser',
                                    references='avgUser-1',
                                    confidential=True,
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    memodoc2=(io.BytesIO(b"file content two"), 'file_two.txt'),
                                    memodoc3=(io.BytesIO(b"file content three"), 'file_three.txt'),
                                    save='Save'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser-5A has been saved' in response.data
        
        response = client.get('/memo/readAllUser/5/A?detail', follow_redirects=True)
        assert response.status_code == 200
        assert b'file_one.txt' in response.data
        assert b'file_three.txt' in response.data

        file_one_url_5A = re.search('href="([^<>"]+?)"[^<>]*>file_one.txt', str(response.data)).group(1)
        file_three_url_5A = re.search('href="([^<>"]+?)"[^<>]*>file_three.txt', str(response.data)).group(1)

        response = client.get(file_one_url_5A, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content one' in response.data
        response = client.get(file_three_url_5A, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content three' in response.data

        # Rename as non-admin - Fail
        response = client.post('/admin/rename', 
                                data=dict(source='readAllUser-5A', destination='readAllUser-5A', rename='Rename'),
                                follow_redirects=True)
        assert response.status_code == 403

        response = client.get('/logout', 
            follow_redirects=True)
        assert response.status_code == 200
        
        # login as admin user
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data

        # Submit empty form - Fail
        response = client.post('/admin/rename', 
                                data=dict(source='', destination='', rename='Rename'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Failed to rename source=&#34;&#34; destination=&#34;&#34;' in response.data

        # Bad Source - Fail
        response = client.post('/admin/rename', 
                                data=dict(source='readAllUser-5B', destination='readAllUser-5B', rename='Rename'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Failed to rename source=&#34;readAllUser-5B&#34; destination=&#34;readAllUser-5B&#34;' in response.data

        # Used destination - Fail
        response = client.post('/admin/rename', 
                                data=dict(source='readAllUser-5A', destination='readAllUser-5A', rename='Rename'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Failed to rename source=&#34;readAllUser-5A&#34; destination=&#34;readAllUser-5A&#34;' in response.data

        # Rename from 5A to 5B - Success
        response = client.post('/admin/rename', 
                                data=dict(source='readAllUser-5A', destination='readAllUser-5B', rename='Rename'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sucessful rename src = readAllUser-5A dst = readAllUser-5B' in response.data
        
        # Verify 5A is gone
        response = client.get('/memo/readAllUser/5/A?detail', follow_redirects=True)
        assert response.status_code == 200
        assert b'No memos match that criteria' in response.data

        # Verify the old files are not present
        response = client.get(file_one_url_5A, follow_redirects=True)
        assert response.status_code == 404
        response = client.get(file_three_url_5A, follow_redirects=True)
        assert response.status_code == 404
        
        # Verify 5B exists
        response = client.get('/memo/readAllUser/5/B?detail', follow_redirects=True)
        assert response.status_code == 200
        assert b'file_one.txt' in response.data
        assert b'file_three.txt' in response.data

        # Verify the files on 5B exist
        file_one_url_5B = re.search('href="([^<>"]+?)"[^<>]*>file_one.txt', str(response.data)).group(1)
        file_three_url_5B = re.search('href="([^<>"]+?)"[^<>]*>file_three.txt', str(response.data)).group(1)

        response = client.get(file_one_url_5B, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content one' in response.data
        response = client.get(file_three_url_5B, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content three' in response.data

def test_delete(client, session):
    # Test delete function
    with client:
        # login as normal user
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data
        
        #Create a memo with files to be deleted
        response = client.get('/cu/memo')
        assert response.status_code == 200
        assert b'New Memo readAllUser-5A' in response.data
        
        response = client.post('/cu/memo/readAllUser/5',
                                data=dict(
                                    username='readAllUser',
                                    memo_number=5,
                                    memo_version='A',
                                    title='Test of memo for readAllUser #5 rev A', 
                                    distribution='adminUser',    
                                    keywords='LiIon',
                                    signers='avgUser',
                                    references='avgUser-1',
                                    confidential=True,
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    memodoc2=(io.BytesIO(b"file content two"), 'file_two.txt'),
                                    memodoc3=(io.BytesIO(b"file content three"), 'file_three.txt'),
                                    save='Save'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser-5A has been saved' in response.data
        
        response = client.get('/memo/readAllUser/5/A?detail', follow_redirects=True)
        assert response.status_code == 200
        assert b'file_one.txt' in response.data
        assert b'file_three.txt' in response.data

        file_one_url_5A = re.search('href="([^<>"]+?)"[^<>]*>file_one.txt', str(response.data)).group(1)
        file_three_url_5A = re.search('href="([^<>"]+?)"[^<>]*>file_three.txt', str(response.data)).group(1)

        response = client.get(file_one_url_5A, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content one' in response.data
        response = client.get(file_three_url_5A, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content three' in response.data

        # Delete as non-admin - Fail
        response = client.post('/admin/delete', 
                                data=dict(delete_ref='readAllUser-5A', delete='Delete'),
                                follow_redirects=True)
        assert response.status_code == 403

        response = client.get('/logout', 
            follow_redirects=True)
        assert response.status_code == 200
        
        # login as admin user
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data

        # Submit empty form - Fail
        response = client.post('/admin/delete', 
                                data=dict(delete_ref='', delete='Delete'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Failed to delete &#34;&#34; invalid reference' in response.data

        # Bad memo name - Fail
        response = client.post('/admin/delete', 
                                data=dict(delete_ref='readAllUser-5B', delete='Delete'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Failed to delete &#34;readAllUser-5B&#34; invalid reference' in response.data

        # Delete 5A - Success
        response = client.post('/admin/delete', 
                                data=dict(delete_ref='readAllUser-5A', delete='Delete'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sucessful delete readAllUser-5A' in response.data
        
        # Verify 5A is gone
        response = client.get('/memo/readAllUser/5/A?detail', follow_redirects=True)
        assert response.status_code == 200
        assert b'No memos match that criteria' in response.data

        # Verify the old files are not present
        response = client.get(file_one_url_5A, follow_redirects=True)
        assert response.status_code == 404
        response = client.get(file_three_url_5A, follow_redirects=True)
        assert response.status_code == 404