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

from memos.models.User import User
from memos.models.MemoHistory import MemoHistory
from flask import current_app
from memos.models.User import User
from memos.models.Memo import Memo
from memos.models.MemoState import MemoState
from memos.models.MemoSignature import MemoSignature




@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app(__name__)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    # With CSRF enabled, the test client needs a wrapper to handle the CSRF cookie
    app.config['WTF_CSRF_ENABLED'] = False
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
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
        _db.drop_all()
        os.unlink(os.environ['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///../", ""))

    _db.app = app
    _db.create_all()

    _db.session.add(User(username='avgUser', password= User.create_hash_pw('u'),email='avgUser@gmail.com'))
    _db.session.add(User(username='adminUser', password= User.create_hash_pw('u'),email='adminUser@gmail.com',admin=True,delegates='avgUser'))
    _db.session.add(User(username='readAllUser', password= User.create_hash_pw('u'),email='readAllUser@gmail.com',readAll=True))
    _db.session.commit()

    memos = [
        Memo(number=1, version='A',title="avgUser memo1-1",user_id="avgUser",memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='B',title="avgUser memo1-2",user_id="avgUser",memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='C',title="avgUser memo1-3",user_id="avgUser",memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0,confidential=True),
        Memo(number=2, version='A',title="avgUser memo2-1",user_id="avgUser",memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=3, version='A',title="avgUser memo3-1",user_id="avgUser",memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='A',title="readAllUser-1-1",user_id='readAllUser',memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='B',title="readAllUser-1-2",user_id='readAllUser',memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='C',title="readAllUser-1-3",user_id='readAllUser',memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0,confidential=True,distribution="avgUser"),
        Memo(number=2, version='A',title="readAllUser-2-1",user_id='readAllUser',memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0,confidential=True),
        Memo(number=3, version='A',title="readAllUser-3-1",user_id='readAllUser',memo_state=MemoState.Draft,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=4, version='A',title="readAllUser-4-1",user_id='readAllUser',memo_state=MemoState.Signoff,keywords="asdf asdf asdf qwer ",num_files=0),
    ]
    for memo in memos:
        _db.session.add(memo)     
    _db.session.commit()
    
    memoSign = Memo.find(username='readAllUser',memo_number=4, memo_version='A')
    _db.session.add(MemoSignature(memo_id = memoSign.id, signer_id = "readAllUser" ) )
    _db.session.add(MemoSignature(memo_id = memoSign.id, signer_id = "adminUser" ) )     
    _db.session.add(MemoSignature(memo_id = memoSign.id, signer_id = "avgUser", delegate_id = "avgUser",
        signed = True, date_signed = datetime.now() ) )     
    _db.session.commit()
    
    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session



