from contextlib import contextmanager
import functools
import threading
from sqlalchemy import *
from sqlalchemy.orm import *

from memos import db

################################################################################

@contextmanager
def transaction():
    try:
        yield
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise
