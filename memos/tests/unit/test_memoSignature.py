from memos.models.Memo import Memo
from memos.models.MemoSignature import MemoSignature
from memos.models.User import User

def test_sign_noSigner(db, session):
    assert not MemoSignature.sign(memo_id=0, signer=None)

def test_sign_noSigReq(db, session):
    user = User.query.get('avgUser')
    assert not MemoSignature.sign(memo_id=0, signer=user)

def test_sign_alreadySigned(db, session):
    memo = Memo.find(username='readAllUser',memo_number=4, memo_version='A')
    user = User.query.get('avgUser')
    assert MemoSignature.sign(memo_id=memo.id, signer=user)

def test_sign_notSigned(db, session):
    memo = Memo.find(username='readAllUser',memo_number=4, memo_version='A')
    user = User.query.get('readAllUser')
    assert MemoSignature.sign(memo_id=memo.id, signer=user)

def test_unsign_noSigner(db, session):
    assert not MemoSignature.unsign(memo_id=0, signer=None)

def test_unsign_noSigReq(db, session):
    user = User.query.get('avgUser')
    assert not MemoSignature.unsign(memo_id=0, signer=user)

def test_unsign_notSigned(db, session):
    memo = Memo.find(username='readAllUser',memo_number=4, memo_version='A')
    user = User.query.get('readAllUser')
    assert not MemoSignature.unsign(memo_id=memo.id, signer=user)

def test_is_signer_noSigner(db, session):
    assert MemoSignature.is_signer(memo_id=0, signer=None) == {'is_signer':False,'status':False,'signature':None}

def test_is_signer_noSigReq(db, session):
    user = User.query.get('avgUser2')
    assert MemoSignature.is_signer(memo_id=0, signer=user) == {'is_signer':False,'status':False,'signature':None}