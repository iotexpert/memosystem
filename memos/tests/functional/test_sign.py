import io
import re

def test_cancel(client, session):
    """
    Flow:
        login
        Use 'New' to create new memo
        Goto 'Drafts' to view memo created
        'Cancel' memo verify cancel message displayed
        Go to 'Drafts' verify memo no longer there
    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data
        
        response = client.get('/cu/memo')
        assert response.status_code == 200
        assert b'New Memo adminUser-1A' in response.data
        
        response = client.get('/drafts')
        assert response.status_code == 200
        assert b'adminUser-1A' in response.data
        assert b'/cancel/memo/adminUser/1/A' in response.data
        
        response = client.get('/cancel/memo/adminUser/1/A', follow_redirects=True)
        assert response.status_code == 200
        assert b'Canceled adminUser-1A' in response.data
        
        response = client.get('/drafts')
        assert response.status_code == 200
        assert b'adminUser-1A' not in response.data
        assert b'/cancel/memmo/adminUser/1/A' not in response.data

def test_cancel2(client, session):
    """
    Flow:
        login
        Use 'New' to create new memo
        'Cancel' memo verify cancel message displayed
        Go to 'Drafts' verify memo no longer there
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data
        
        response = client.get('/cu/memo')
        assert response.status_code == 200
        assert b'New Memo avgUser-4A' in response.data

        response = client.post('/cu/memo/avgUser/4',
                                data=dict(
                                    username='avgUser',
                                    memo_number=4,
                                    memo_version='A',
                                    title='Test of memo for avgUser #4 rev A', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='',
                                    references='',
                                    cancel='Cancel'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Canceled avgUser-4A' in response.data
        
        response = client.get('/drafts')
        assert response.status_code == 200
        assert b'avgUser-4A' not in response.data
        assert b'/cancel/memmo/avgUser/4/A' not in response.data

def test_invalid_dist(client, session):
    """
    Flow:
        login
        Submit a new memo with invalid distribution list
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data

        response = client.post('/cu/memo/avgUser/4',
                                data=dict(
                                    username='avgUser',
                                    memo_number=4,
                                    memo_version='A',
                                    title='Test of memo for avgUser #4 rev A', 
                                    distribution='adminUser badUser',    
                                    keywords='',
                                    signers='',
                                    references='readAllUser-1 badUser-1 badUser-2-s-s',
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    submit='Submit'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid users [&#39;badUser&#39;]' in response.data
        assert b'Invalid memo references = [&#39;badUser-1&#39;, &#39;badUser-2-s-s&#39;]' in response.data

def test_revise(client, session):
    """
    Flow:
        login
        Submit a revision to an existing memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data

        response = client.get('/cu/memo/avgUser/3',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'New Memo avgUser-3B' in response.data
        
        response = client.post('/cu/memo/avgUser/3',
                                data=dict(
                                    username='avgUser',
                                    memo_number=3,
                                    memo_version='B',
                                    title='avgUser memo 3-2', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='',
                                    references='',
                                    confidential=True,
                                    submit='submit'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'avgUser-3B' in response.data
        assert b'Must have at least one file attached to Submit memo' in response.data
        
        response = client.post('/cu/memo/avgUser/3',
                                data=dict(
                                    username='avgUser',
                                    memo_number=3,
                                    memo_version='B',
                                    title='avgUser memo 3-2', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='',
                                    references='',
                                    confidential=True,
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    submit='submit'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'avgUser-3B' in response.data
        assert b'/memo/avgUser/3/B?detail' in response.data
    
def test_publish_2_files(client, session):
    """
    Flow:
        login
        Use 'New' to create new memo
        - Fill in form with three files
        - Save
        Use 'Edit' to reload the form
        - Remove file #2
        Use 'Edit' to reload the form
        - Submit
        Memo listed on result
        Select memo ?detail
        - Link to files present
        Download files to verify
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
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
                                    title='Test of memo for readAllUser #5 rev A', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='',
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
        
        response = client.post('/cu/memo/readAllUser/5',
                                data=dict(
                                    username='readAllUser',
                                    memo_number=5,
                                    memo_version='A',
                                    title='Test of memo for readAllUser #5 rev A', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='',
                                    references='',
                                    confidential=True,
                                    file_1='Remove'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser-5A' in response.data
        assert b'Remove File(&#39;Document Filename = file_two.txt&#39;' in response.data
        
        response = client.post('/cu/memo/readAllUser/5',
                                data=dict(
                                    username='readAllUser',
                                    memo_number=5,
                                    memo_version='A',
                                    title='Test of memo for readAllUser #5 rev A', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='',
                                    references='',
                                    confidential=True,
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    submit='submit'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser-5A' in response.data
        assert b'/memo/readAllUser/5/A?detail' in response.data
        
        response = client.get('/memo/readAllUser/5/A?detail', follow_redirects=True)
        assert response.status_code == 200
        assert b'file_one.txt' in response.data
        assert b'file_three.txt' in response.data

        file_one_url = re.search('href="([^<>"]+?)"[^<>]*>file_one.txt', str(response.data)).group(1)
        file_three_url = re.search('href="([^<>"]+?)"[^<>]*>file_three.txt', str(response.data)).group(1)

        response = client.get(file_one_url, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content one' in response.data
        response = client.get(file_three_url, follow_redirects=True)
        assert response.status_code == 200
        assert b'file content three' in response.data

        # Verify error on bad file name
        response = client.get(file_three_url+'a', follow_redirects=True)
        assert response.status_code == 404

        response = client.get('/logout',
                                follow_redirects=True)
        assert response.status_code == 200

        # Verify error on no access
        response = client.get(file_three_url, follow_redirects=True)
        assert response.status_code == 403


    
def test_create_invalid_user(client, session):
    """
    Flow:
        login
        Use /cu/memo/invalid_user to verify error handling
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data
        
        response = client.get('/cu/memo/invalid_user')
        assert response.status_code == 404

def test_create_for_nondelegated_user(client, session):
    """
    Flow:
        login
        Use /cu/memo/<non delegated user to verify error handling
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data
        
        response = client.get('/cu/memo/avgUser')
        assert response.status_code == 403

def test_create_with_post(client, session):
    """
    Flow:
        login
        Create memo via a post
        Goto 'Drafts' to view memo created
        'Cancel' memo verify cancel message displayed
        Go to 'Drafts' verify memo no longer there
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data
        

        response = client.post('/cu/memo/avgUser/4',
                                data=dict(
                                    username='avgUser',
                                    memo_number=4,
                                    memo_version='A',
                                    title='', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='badSigner',
                                    references=''
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'New Memo avgUser-4A' in response.data
        assert b'This field is required.' in response.data
        assert b'Invalid users [&#39;badSigner&#39;]' in response.data

def test_check_inbox_nologin(client, session):
    """
    Flow:
        View Inbox
    """
    with client:
        response = client.get('/inbox',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in to access this page.' in response.data

def test_check_inbox_self(client, session):
    """
    Flow:
        login
        View Inbox
    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data        

        response = client.get('/inbox',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser memo 4-1' in response.data
        assert b'testFile.txt' not in response.data

def test_check_inbox_other(client, session):
    """
    Flow:
        login
        View Inbox
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data

        response = client.get('/inbox',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'No memos match that criteria' in response.data

        response = client.get('/inbox/adminUser',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser memo 4-1' in response.data

def test_check_inbox_badUser(client, session):
    """
    Flow:
        login
        View Inbox
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data        

        response = client.get('/inbox/badUser',
                                follow_redirects=True)
        assert response.status_code == 404
        assert b'readAllUser memo 4-1' not in response.data

def test_check_inbox_notDelegate(client, session):
    """
    Flow:
        login
        View Inbox
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data        

        response = client.get('/inbox/adminUser',
                                follow_redirects=True)
        assert response.status_code == 403
        assert b'readAllUser memo 4-1' not in response.data

def test_check_drafts_other(client, session):
    """
    Flow:
        login
        View Drafts
    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data        

        response = client.get('/drafts/readAllUser',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser memo 3-1' in response.data

def test_check_drafts_badUser(client, session):
    """
    Flow:
        login
        View Drafts
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data        

        response = client.get('/drafts/badUser',
                                follow_redirects=True)
        assert response.status_code == 404
        assert b'readAllUser memo 4-1' not in response.data

def test_check_drafts_notDelegate(client, session):
    """
    Flow:
        login
        View Drafts
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data        

        response = client.get('/drafts/adminUser',
                                follow_redirects=True)
        assert response.status_code == 403
        assert b'readAllUser memo 4-1' not in response.data

def test_check_sign_unsign(client, session):
    """
    Flow:
        login as admin
        Create memo as readAll with readAll and admin signatures required
        Attempt sign as avg, expect error
        Attempt sign as bad, expect error
        Sign as self(admin), expect success
        Attempt sign as self(admin), expect error
        Attempt sign invalid memo, expect error

        Attempt unsign as avg, expect error
        Attempt unsign as bad, expect error
        Attempt unsign as readAll, expect error
        Unsign as self(admin), expect success
        Attempt unsign invalid memo, expect error

        Sign as self(admin), expect success
        Sign as readAll, expect success, memo published

    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data
        
        response = client.post('/cu/memo/readAllUser/5',
                                data=dict(
                                    username='readAllUser',
                                    memo_number=5,
                                    memo_version='A',
                                    title='Test of memo for readAllUser #5 rev A', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='readAllUser adminUser',
                                    references='',
                                    confidential=False,
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    submit='submit'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser-5A has been created!' in response.data

        response = client.get('/sign/memo/readAllUser/5/A?signer=avgUser',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sign readAllUser-5A Failed' in response.data

        response = client.get('/sign/memo/readAllUser/5/A?signer=badUser',
                                follow_redirects=True)
        assert response.status_code == 404

        response = client.get('/sign/memo/readAllUser/5/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sign readAllUser-5A Success' in response.data

        response = client.get('/sign/memo/readAllUser/5/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sign readAllUser-5A Failed' in response.data

        response = client.get('/sign/memo/readAllUser/5/B',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sign readAllUser-5-B Failed' in response.data

        # Now the unsign tests
        response = client.get('/unsign/memo/readAllUser/5/A?signer=avgUser',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Unsign readAllUser-5A Failed' in response.data

        response = client.get('/unsign/memo/readAllUser/5/A?signer=badUser',
                                follow_redirects=True)
        assert response.status_code == 404

        response = client.get('/unsign/memo/readAllUser/5/A?signer=readAllUser',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Unsign readAllUser-5A Failed' in response.data

        response = client.get('/unsign/memo/readAllUser/5/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Unsign readAllUser-5A success' in response.data     

        response = client.get('/unsign/memo/readAllUser/5/B',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Unsign readAllUser-5-B Failed' in response.data
        
        response = client.get('/sign/memo/readAllUser/5/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sign readAllUser-5A Success' in response.data

        response = client.get('/history',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'adminUser' in response.data
        assert b'readAllUser-5A' in response.data
        assert b'MemoActivity.Create' in response.data
        assert b'MemoActivity.Unsign' in response.data
        assert b'MemoActivity.Sign' in response.data
        assert b'MemoActivity.Signoff' in response.data

def test_check_revise_and_activate(client, session):
    """
    Flow:
        login as admin
        Create memo as a revision with a signature required
        Sign as self, expect success, memo published

    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data
        
        response = client.post('/cu/memo/readAllUser/4',
                                data=dict(
                                    username='readAllUser',
                                    memo_number=4,
                                    memo_version='B',
                                    title='readAllUser memo 4-2', 
                                    distribution='adminUser',    
                                    keywords='',
                                    signers='readAllUser',
                                    references='',
                                    confidential=False,
                                    memodoc1=(io.BytesIO(b"file content one"), 'file_one.txt'),
                                    submit='submit'
                                    ),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser-4B has been created!' in response.data

        response = client.get('/sign/memo/readAllUser/4/B',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Sign readAllUser-4B Success' in response.data
        assert b'href="/memo/readAllUser/4/B?detail">readAllUser-4B' in response.data

def test_obsolete_nologin(client, session):
    """
    Flow:
        Obsolete memo
    """
    with client:
        response = client.get('/obsolete/memo/avgUser/1/Z',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in to access this page.' in response.data

def test_obsolete_badMemo(client, session):
    """
    Flow:
        Login
        Obsolete memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data

        response = client.get('/obsolete/memo/avgUser/1/Z',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Obsolete avgUser-1-Z Failed' in response.data

def test_obsolete_memo_wo_permission(client, session):
    """
    Flow:
        Login
        Obsolete memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data

        response = client.get('/obsolete/memo/avgUser/1/C',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Obsolete avgUser-1C Failed' in response.data

def test_obsolete_memo_w_permission(client, session):
    """
    Flow:
        Login
        Obsolete memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data

        response = client.get('/obsolete/memo/readAllUser/1/C',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Obsolete readAllUser-1C Success' in response.data

def test_cancel_nologin(client, session):
    """
    Flow:
        Cancel memo
    """
    with client:
        response = client.get('/cancel/memo/avgUser/1/Z',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in to access this page.' in response.data

def test_cancel_badMemo(client, session):
    """
    Flow:
        Login
        Cancel memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data

        response = client.get('/cancel/memo/avgUser/1/Z',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Cannot cancel memo avgUser-1-Z' in response.data

def test_cancel_memo_wo_permission(client, session):
    """
    Flow:
        Login
        Cancel memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data

        response = client.get('/cancel/memo/readAllUser/3/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Cancel readAllUser-3A Failed' in response.data

def test_cancel_memo_w_permission(client, session):
    """
    Flow:
        Login
        Cancel memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data

        response = client.get('/cancel/memo/readAllUser/3/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Canceled readAllUser-3A' in response.data

def test_reject_nologin(client, session):
    """
    Flow:
        Reject memo
    """
    with client:
        response = client.get('/reject/memo/avgUser/1/Z',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in to access this page.' in response.data

def test_reject_badUser(client, session):
    """
    Flow:
        Login
        Reject memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data

        response = client.get('/reject/memo/avgUser/1/Z?signer=badUser',
                                follow_redirects=True)
        assert response.status_code == 404

def test_reject_badMemo(client, session):
    """
    Flow:
        Login
        Reject memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data

        response = client.get('/reject/memo/avgUser/1/Z',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Cannot unsign memo avgUser-1-Z' in response.data

def test_reject_memo_wo_permission(client, session):
    """
    Flow:
        Login
        Reject memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser2', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser2' in response.data

        response = client.get('/reject/memo/readAllUser/4/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Reject readAllUser-4-A Failed' in response.data

def test_reject_memo_w_permission(client, session):
    """
    Flow:
        Login
        Reject memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='readAllUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: readAllUser' in response.data

        response = client.get('/reject/memo/readAllUser/4/A',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Rejected readAllUser-4-A' in response.data

def test_search_load(client, session):
    """
    Flow:
        Load search page
    """
    with client:
        response = client.get('/search',
                                follow_redirects=True)
        assert response.status_code == 200
        title_search = re.search('name="title"[^<>]+?value="([^<>"]*)"', str(response.data))
        keywords_search = re.search('name="keywords"[^<>]+?value="([^<>"]*)"', str(response.data))
        memo_ref_search = re.search('name="memo_ref"[^<>]+?value="([^<>"]*)"', str(response.data))
        username_search = re.search('name="username"[^<>]+?value="([^<>"]*)"', str(response.data))
        inbox_search = re.search('name="inbox"[^<>]+?value="([^<>"]*)"', str(response.data))
        assert title_search and title_search.group(1) == ''
        assert keywords_search and keywords_search.group(1) == ''
        assert memo_ref_search and memo_ref_search.group(1) == ''
        assert username_search and username_search.group(1) == ''
        assert inbox_search and inbox_search.group(1) == ''

def test_search_post_load(client, session):
    """
    Flow:
        Load search page
    """
    with client:
        response = client.post('/search',data=dict(),
                                follow_redirects=True)
        assert response.status_code == 200
        title_search = re.search('name="title"[^<>]+?value="([^<>"]*)"', str(response.data))
        keywords_search = re.search('name="keywords"[^<>]+?value="([^<>"]*)"', str(response.data))
        memo_ref_search = re.search('name="memo_ref"[^<>]+?value="([^<>"]*)"', str(response.data))
        username_search = re.search('name="username"[^<>]+?value="([^<>"]*)"', str(response.data))
        inbox_search = re.search('name="inbox"[^<>]+?value="([^<>"]*)"', str(response.data))
        assert title_search and title_search.group(1) == ''
        assert keywords_search and keywords_search.group(1) == ''
        assert memo_ref_search and memo_ref_search.group(1) == ''
        assert username_search and username_search.group(1) == ''
        assert inbox_search and inbox_search.group(1) == ''

def test_search_get_title(client, session):
    """
    Flow:
        Load search page
    """
    with client:
        response = client.get('/search?search=title:avgUser memo',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'href="/memo/avgUser/3/A?detail">avgUser memo 3-1</a>' in response.data
        assert b'href="/memo/avgUser/2/A?detail">avgUser memo 2-1</a>' in response.data
        assert b'href="/memo/avgUser/1/B?detail">avgUser memo 1-2</a>' in response.data
        assert b'href="/memo/avgUser/1/A?detail">avgUser memo 1-1</a>' in response.data
        
        response = client.get('/search?search=title:No+memo+present',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'No memos match that criteria' in response.data

def test_search_get_keyword(client, session):
    """
    Flow:
        Load search page
    """
    with client:
        response = client.get('/search?search=keywords:Outstanding',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'href="/memo/readAllUser/4/A?detail">readAllUser memo 4-1</a>' in response.data
        assert b'href="/memo/readAllUser/3/A?detail">readAllUser memo 3-1</a>' in response.data
        assert b'href="/memo/readAllUser/1/B?detail">readAllUser memo 1-2</a>' in response.data
        assert b'href="/memo/readAllUser/1/A?detail">readAllUser memo 1-1</a>' in response.data
        
        response = client.get('/search?search=keywords:No+memo+present',
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'No memos match that criteria' in response.data


def test_search_post_title(client, session):
    """
    Flow:
        Search by title
    """
    with client:
        response = client.post('/search', data=dict(title='avgUser'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'href="/memo/avgUser/3/A?detail">avgUser memo 3-1</a>' in response.data
        assert b'href="/memo/avgUser/2/A?detail">avgUser memo 2-1</a>' in response.data
        assert b'href="/memo/avgUser/1/B?detail">avgUser memo 1-2</a>' in response.data
        assert b'href="/memo/avgUser/1/A?detail">avgUser memo 1-1</a>' in response.data
        
        response = client.post('/search', data=dict(title='No+memo+present'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'No memos match that criteria' in response.data

def test_search_post_keyword(client, session):
    """
    Flow:
        Search by keyword
    """
    with client:
        response = client.post('/search?detail', data=dict(keywords='Outstanding'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'href="/memo/readAllUser/4/A?detail">readAllUser memo 4-1</a>' in response.data
        assert b'href="/memo/readAllUser/3/A?detail">readAllUser memo 3-1</a>' in response.data
        assert b'href="/memo/readAllUser/1/B?detail">readAllUser memo 1-2</a>' in response.data
        assert b'href="/memo/readAllUser/1/A?detail">readAllUser memo 1-1</a>' in response.data
        
        response = client.post('/search', data=dict(keywords='No+memo+present'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'No memos match that criteria' in response.data

def test_search_post_memo_ref(client, session):
    """
    Flow:
        search by memo number, shows all versions of memo
    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data

        response = client.post('/search?detail', data=dict(memo_ref='avgUser-1'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'href="/memo/avgUser/3/A?detail">avgUser memo 3-1</a>' not in response.data
        assert b'href="/memo/avgUser/2/A?detail">avgUser memo 2-1</a>' not in response.data
        assert b'href="/memo/avgUser/1/C?detail">avgUser memo 1-3</a>' in response.data
        assert b'href="/memo/avgUser/1/B?detail">avgUser memo 1-2</a>' in response.data
        assert b'href="/memo/avgUser/1/A?detail">avgUser memo 1-1</a>' in response.data

def test_search_post_user(client, session):
    """
    Flow:
        Load search by user, loads active memos
    """
    with client:
        response = client.post('/login',
                                data=dict(username='adminUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: adminUser' in response.data

        response = client.post('/search?detail', data=dict(username='avgUser'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'href="/memo/avgUser/3/A?detail">avgUser memo 3-1</a>' in response.data
        assert b'href="/memo/avgUser/2/A?detail">avgUser memo 2-1</a>' in response.data
        assert b'href="/memo/avgUser/1/C?detail">avgUser memo 1-3</a>' in response.data

def test_search_post_inbox(client, session):
    """
    Flow:
        login
        View Inbox
    """
    with client:
        response = client.post('/login',
                                data=dict(username='avgUser', password='u'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'Account: avgUser' in response.data        

        response = client.post('/search?detail', data=dict(inbox='adminUser'),
                                follow_redirects=True)
        assert response.status_code == 200
        assert b'readAllUser memo 4-1' in response.data