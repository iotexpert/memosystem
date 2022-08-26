from datetime import datetime
import pytest
import os
try:
    import settings_local
except ImportError:
    pass
#load overrides of setting_local for testing.
import test_settings_local
from memos import create_app
from memos import db as _db

from flask import current_app
from memos.models.Memo import Memo
from memos.models.MemoFile import MemoFile
from memos.models.MemoReference import MemoReference
from memos.models.MemoSignature import MemoSignature
from memos.models.MemoState import MemoState
from memos.models.User import User




@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app(__name__)
    @app.context_processor
    def inject_pinned():
        return dict(get_pinned=Memo.get_pinned)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    # With CSRF enabled, the test client needs a wrapper to handle the CSRF cookie
    app.config['WTF_CSRF_ENABLED'] = False
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    # This will make the static member function "get_pinned" available in the template
    @app.context_processor
    def inject_pinned():
        return dict(get_pinned=Memo.get_pinned)

    return app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.environ['SQLALCHEMY_DATABASE_URI'].startswith("sqlite:///../"):
        if os.path.exists(os.environ['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///../", "")):
            os.unlink(os.environ['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///../", ""))

    def teardown():
        _db.close_all_sessions()
        os.unlink(os.environ['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///../", ""))

    _db.app = app
    _db.create_all()
    
    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    Memo.query.delete()
    MemoFile.query.delete()
    MemoReference.query.delete()
    MemoSignature.query.delete()
    User.query.delete()

    db.session.add(User(username='avgUser', password= User.create_hash_pw('u'),email='avgUser@gmail.com'))
    db.session.add(User(username='avgUser2', password= User.create_hash_pw('u'),email='avgUser2@gmail.com'))
    db.session.add(User(username='avgUser2b', password= User.create_hash_pw('u'),email='avgUser2@gmail.com'))
    db.session.add(User(username='adminUser', password= User.create_hash_pw('u'),email='adminUser@gmail.com',admin=True,delegates='avgUser'))
    db.session.add(User(username='readAllUser', password= User.create_hash_pw('u'),email='readAllUser@gmail.com',readAll=True))
    db.session.commit()

    memos = [
        Memo(number=1, version='A',title="avgUser memo 1-1",user_id="avgUser",memo_state=MemoState.Obsolete,keywords="Average Joe "),
        Memo(number=1, version='B',title="avgUser memo 1-2",user_id="avgUser",memo_state=MemoState.Obsolete,keywords="Average Joe "),
        Memo(number=1, version='C',title="avgUser memo 1-3",user_id="avgUser",memo_state=MemoState.Active,keywords="Average Joe ",confidential=True),
        Memo(number=2, version='A',title="avgUser memo 2-1",user_id="avgUser",memo_state=MemoState.Active,keywords="Average Joe "),
        Memo(number=3, version='A',title="avgUser memo 3-1",user_id="avgUser",memo_state=MemoState.Active,keywords="Average Joe "),
        Memo(number=1, version='A',title="readAllUser memo 1-1",user_id='readAllUser',memo_state=MemoState.Obsolete,keywords="Outstanding Joe "),
        Memo(number=1, version='B',title="readAllUser memo 1-2",user_id='readAllUser',memo_state=MemoState.Obsolete,keywords="Outstanding Joe "),
        Memo(number=1, version='C',title="readAllUser memo 1-3",user_id='readAllUser',memo_state=MemoState.Active,keywords="Outstanding Joe ",confidential=True,distribution="avgUser"),
        Memo(number=2, version='A',title="readAllUser memo 2-1",user_id='readAllUser',memo_state=MemoState.Active,keywords="Outstanding Joe ",confidential=True),
        Memo(number=3, version='A',title="readAllUser memo 3-1",user_id='readAllUser',memo_state=MemoState.Draft,keywords="Outstanding Joe "),
        Memo(number=4, version='A',title="readAllUser memo 4-1",user_id='readAllUser',memo_state=MemoState.Signoff,keywords="Outstanding Joe "),
    ]
    for memo in memos:
        db.session.add(memo)     
    db.session.commit()
    
    memoSign = Memo.find(username='readAllUser',memo_number=4, memo_version='A')
    db.session.add(MemoSignature(memo_id = memoSign.id, signer_id = "readAllUser" ) )
    db.session.add(MemoSignature(memo_id = memoSign.id, signer_id = "adminUser" ) )     
    db.session.add(MemoSignature(memo_id = memoSign.id, signer_id = "avgUser", delegate_id = "avgUser",
        signed = True, date_signed = datetime.now() ) )     

    db.session.add(MemoFile(memo_id = memoSign.id, filename = "testFile.txt" ) )
    db.session.add(MemoReference(source_id = memoSign.id, ref_user_id = "avgUser", ref_memo_number = 1, ref_memo_version = "B" ) )
    db.session.add(MemoReference(source_id = memoSign.id, ref_user_id = "avgUser", ref_memo_number = 2) )
    
    memoSign = Memo.find(username='readAllUser',memo_number=3, memo_version='A')
    db.session.add(MemoReference(source_id = memoSign.id, ref_user_id = "readAllUser", ref_memo_number = 1) )
    db.session.add(MemoReference(source_id = memoSign.id, ref_user_id = "readAllUser", ref_memo_number = 1, ref_memo_version = "B") )

    db.session.commit()

    return db.session



