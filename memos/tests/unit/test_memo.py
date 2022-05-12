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
    memoDraft = Memo.find(username='readAllUser',memo_number=4, memo_version='A')

    readAllUser = User.find(username='readAllUser')
    avgUser = User.find(username='avgUser')

    assert not memoActive.can_revise()
    assert not memoActive.can_revise(avgUser)
    assert memoActive.can_revise(readAllUser)
    assert memoObsolete.can_revise(readAllUser)
    assert not memoDraft.can_revise(readAllUser)
