from contextlib import contextmanager
import functools
import threading
from sqlalchemy import *
from sqlalchemy.orm import *

from memos import db

################################################################################

def scopefunc():
    return "{}.{}".format(is_inside_txn(), threading.current_thread().ident)

txn_context = threading.local()

context_name = "db_or_conection_instance_id"

def push_txn_context():
    if not hasattr(txn_context, context_name):
        setattr(txn_context, context_name, [])
    getattr(txn_context, context_name).append(True)


def pop_txn_context():
    getattr(txn_context, context_name).pop(-1)


def is_inside_txn():
    return len(getattr(txn_context, context_name, [])) > 0

@contextmanager
def transaction():
    outer_transaction = False #not is_inside_txn()
    push_txn_context()
    if db.session.autocommit:
        db.session.begin()
    else:
        db.session.begin(nested=True)
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
        if outer_transaction:
            db.session.close()
        pop_txn_context()
    

def transactional(func):
    @functools.wraps(func)
    def wrapper(**kwargs):
        with transaction():
            return func(**kwargs)
    return wrapper