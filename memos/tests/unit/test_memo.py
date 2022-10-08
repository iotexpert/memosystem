from memos.models.User import User
from memos.models.Memo import Memo


def test___repr__(db, session):
    memoObsolete = Memo.find(username='readAllUser',memo_number=1, memo_version='A')
    assert memoObsolete.__repr__() == 'readAllUser-1A'

def test___str__(db, session):
    memoObsolete = Memo.find(username='readAllUser',memo_number=1, memo_version='A')
    assert memoObsolete.__str__() == 'readAllUser-1A'

def test_can_create(db, session):
    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')

    assert not Memo.can_create()
    assert Memo.can_create(readAllUser)
    assert not Memo.can_create(adminUser, readAllUser)

def test_can_revise(db, session):
    memoObsolete = Memo.find(username='readAllUser',memo_number=1, memo_version='A')
    memoActive = Memo.find(username='readAllUser',memo_number=1, memo_version='C')
    memoDraft = Memo.find(username='readAllUser',memo_number=3, memo_version='A')

    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not memoActive.can_revise()
    assert not memoActive.can_revise(avgUser)
    assert memoActive.can_revise(readAllUser)
    assert memoObsolete.can_revise(readAllUser)
    assert not memoDraft.can_revise(readAllUser)

def test_can_sign(db, session):
    memoDraft = Memo.find(username='readAllUser',memo_number=3, memo_version='A')
    memoSign = Memo.find(username='readAllUser',memo_number=4, memo_version='A')

    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not memoSign.can_sign(avgUser, None)  # Must supply delegate
    assert not memoSign.can_sign(None, avgUser)  # Must supply signer
    assert not memoSign.can_sign(readAllUser, avgUser) # avgUser not a delegate for readAllUser
    assert memoSign.can_sign(readAllUser, readAllUser) # Can sign for self
    assert memoSign.can_sign(adminUser, avgUser)  # avgUser is a delgate for adminUser
    assert not memoSign.can_sign(avgUser, avgUser) # avgUser already signed on this memo
    assert not memoDraft.can_sign(readAllUser, readAllUser) #memo not in signoff state

def test_can_unsign(db, session):
    memoDraft = Memo.find(username='readAllUser',memo_number=3, memo_version='A')
    memoSign = Memo.find(username='readAllUser',memo_number=4, memo_version='A')

    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not memoSign.can_unsign(avgUser, None)  # Must supply delegate
    assert not memoSign.can_unsign(None, avgUser)  # Must supply signer
    assert not memoSign.can_unsign(readAllUser, avgUser) # avgUser not a delegate for readAllUser
    assert not memoSign.can_unsign(readAllUser, readAllUser) # Not yet signed.
    assert memoSign.can_unsign(avgUser, avgUser) # avgUser has signed on this memo
    assert memoSign.can_unsign(avgUser, adminUser)  # adminUser is a delgate for everyone
    assert not memoDraft.can_unsign(readAllUser, readAllUser) #memo not in signoff state

def test_can_obsolete(db, session):
    memoDraft = Memo.find(username='readAllUser',memo_number=3, memo_version='A')
    memoActive = Memo.find(username='readAllUser',memo_number=1, memo_version='C')

    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not memoActive.can_obsolete(None)  # Must supply delegate
    assert not memoActive.can_obsolete(avgUser) # avgUser not a delegate for readAllUser
    assert memoActive.can_obsolete(adminUser)  # adminUser is a delgate for everyone
    assert not memoDraft.can_obsolete(readAllUser) #memo not in signoff state

def test_can_cancel(db, session):
    memoDraft = Memo.find(username='readAllUser',memo_number=3, memo_version='A')
    memoActive = Memo.find(username='readAllUser',memo_number=1, memo_version='C')

    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not memoDraft.can_cancel(None)  # Must supply delegate
    assert not memoDraft.can_cancel(avgUser) # avgUser not a delegate for readAllUser
    assert memoDraft.can_cancel(adminUser)  # adminUser is a delgate for everyone
    assert not memoActive.can_cancel(readAllUser) #memo not in signoff state

def test_can_reject(db, session):
    memoDraft = Memo.find(username='readAllUser',memo_number=3, memo_version='A')
    memoSign = Memo.find(username='readAllUser',memo_number=4, memo_version='A')

    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not memoSign.can_reject(avgUser, None)  # Must supply delegate
    assert not memoSign.can_reject(None, avgUser)  # Must supply signer
    assert not memoSign.can_reject(readAllUser, avgUser) # avgUser not a delegate for readAllUser
    assert memoSign.can_reject(readAllUser, readAllUser) # Not yet signed
    assert memoSign.can_reject(avgUser, avgUser) # avgUser has signed on this memo
    assert memoSign.can_reject(avgUser, adminUser)  # adminUser is a delgate for everyone
    assert not memoDraft.can_reject(readAllUser, readAllUser) #memo not in signoff state

def test_can_access(db, session):
    AvgConf = Memo.find(username='avgUser',memo_number=1, memo_version='C')
    ReadNotConf = Memo.find(username='readAllUser',memo_number=1, memo_version='B')
    ReadConfWithAvg = Memo.find(username='readAllUser',memo_number=1, memo_version='C')
    ReadConfWOAvg = Memo.find(username='readAllUser',memo_number=2, memo_version='A')

    adminUser = User.find(username='adminUser')
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert ReadNotConf.can_access(None,None)  # Not confidential, memo access without user
    assert not AvgConf.can_access(None,None)  # Confidential memo not access without user
    assert AvgConf.can_access(avgUser,avgUser)  # Access to self
    assert AvgConf.can_access(readAllUser,readAllUser)  # Access to read all permission
    assert AvgConf.can_access(adminUser,adminUser)  # Access to admin

    assert ReadConfWithAvg.can_access(avgUser,avgUser)  # Access to with distribution
    assert not ReadConfWOAvg.can_access(avgUser,avgUser)  # No access with out distribution

def test_create_revise(db, session):
    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not Memo.create_revise(readAllUser, avgUser) # avgUser not a delegate for readAllUser

def test_get_inbox(db, session):
    assert not Memo.get_inbox(user=None)

def test_get_drafts(db, session):
    assert not Memo.get_drafts(user=None)

def test_parse_reference(db, session):
    # Test with number a version smashed together
    ref = Memo.parse_reference('avgUser-2a')
    assert ref['memo'] is not None
    assert ref['valid']
    assert ref['user'].username == 'avgUser'
    assert ref['memo_number'] == 2
    assert ref['memo_version'] == 'A'
    
    # Test with no numeric memo number
    ref = Memo.parse_reference('avgUser-aa')
    assert ref['memo'] is None
    assert not ref['valid']
    assert ref['memo_number'] is None
    
    # Test with non alpha version
    ref = Memo.parse_reference('avgUser-2_')
    assert ref['memo'] is None
    assert not ref['valid']
    assert ref['memo_number'] is None
    
    # Test with non alpha version
    ref = Memo.parse_reference('avgUser-2-_')
    assert ref['memo'] is None
    assert not ref['valid']
    assert ref['memo_number'] is None

def test_valid_references(db, session):
    # Test with number a version smashed together
    ref = Memo.valid_references('readAllUser-1a;readAllUser-2a\treadAllUser-3a,readAllUser-4a: ; badMemo')
    assert 'readAllUser-1a' in ref['valid_refs']
    assert 'readAllUser-2a' in ref['valid_refs']
    assert 'readAllUser-3a' in ref['invalid']
    assert 'readAllUser-4a' in ref['invalid']
    assert 'badMemo' in ref['invalid']