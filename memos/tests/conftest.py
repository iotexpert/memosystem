import pytest
from docmgr import db,create_app

from docmgr.models.User import User
from docmgr.models.MemoHistory import MemoHistory
from flask import current_app
from docmgr.models.User import User
from docmgr.models.Memo import Memo
from docmgr.models.MemoState import MemoState

@pytest.fixture(scope='module')
def client():
    app = create_app()
    app.app_context().push()
    db.init_app(app)
    
    # Create a test client using the Flask application configured for testing
    with app.test_client() as client:
        # Establish an application context
        with app.app_context():
            yield client  # this is where the testing happens!


"""
@pytest.fixture()
def app(scope='module'):
    print("App")
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    app.app_context().push()
    db.init_app(app)
    

    # other setup can go here

    yield app

    # clean up / reset resources here

    

    
@pytest.fixture(scope='module')
def client(app):
    print("Client")
    return app.test_client()
"""


@pytest.fixture(scope='module')
def init_database():
    db.create_all()
    admin =  User(username=current_app.config['ADMIN_USER'], password=User.create_hash_pw(current_app.config['ADMIN_PASSWORD']),email=current_app.config['ADMIN_EMAIL'],admin=True)
    db.session.add(admin)
    db.session.commit()
    memo1 = Memo(number=1, version='A',title="Admin1-1",user_id=1,memo_state=MemoState.Active,num_files=0)
    db.session.add(memo1)
    db.session.commit()
    
    yield
    
    db.drop_all()

@pytest.fixture()
def runner(app):
    print("runner")
    return app.test_cli_runner()


from docmgr import db,create_app
from sqlalchemy_utils.functions import database_exists
from docmgr.models.User import User
from docmgr.models.Memo import Memo
from docmgr.models.MemoState import MemoState
from docmgr.models.MemoFile import MemoFile
from docmgr.models.MemoSignature import MemoSignature

app=create_app()
app.app_context().push()
db.init_app(app)

users = [
    User(username='u1', password= User.create_hash_pw('u'),email='u1@t.local',admin=False,delegates='u3'),
    User(username='u2', password= User.create_hash_pw('u'),email='u2@t.local',admin=False,delegates=''),
    User(username='u3', password= User.create_hash_pw('u'),email='u3@t.local',admin=False,delegates=''),

]

for user in users:
    db.session.add(user)
    try:
        db.session.commit()
        print(f"User {user.username} Created")

    except:
        print(f"User {user.username} Already Exists")
        db.session.rollback()


def create_history():
    memos = [
        Memo(number=1, version='A',title="u1 memo1-1",user_id=2,memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='B',title="u1 memo1-2",user_id=2,memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='C',title="u1 memo1-3",user_id=2,memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=2, version='A',title="u1 memo2-1",user_id=2,memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=3, version='A',title="u1 memo3-1",user_id=2,memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='A',title="u2-1-1",user_id=3,memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='B',title="u2-1-2",user_id=3,memo_state=MemoState.Obsolete,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=1, version='C',title="u2-1-3",user_id=3,memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=2, version='A',title="u2-2-1",user_id=3,memo_state=MemoState.Active,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=3, version='A',title="u2-3-1",user_id=3,memo_state=MemoState.Draft,keywords="asdf asdf asdf qwer ",num_files=0),
        Memo(number=4, version='A',title="u2-4-1",user_id=3,memo_state=MemoState.Draft,keywords="asdf asdf asdf qwer ",num_files=0),
    ]
    for memo in memos:
        db.session.add(memo)
        db.session.commit()
        
        memo.process_state()
    db.session.commit()

    #MemoFile()
    #MemoSignature()