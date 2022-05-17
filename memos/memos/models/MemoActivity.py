import enum
from flask import current_app

class MemoActivity(enum.Enum):
    Create = 1             # Memo has been created and put into draft
    Signoff = 2            # Memo has been submitted to signoff
    Sign = 3               # A signature has been added
    Unsign = 4             # A signature has been removed
    Activate = 5           # Memo moved from signoff to active
    Obsolete = 6           # Memo has been obsoleted
    Cancel = 7             # Memo has been canceled and deleted from the system
    Reject = 8             # Memo has been rejected and put back into draft
    IllegalFile = 9        # User tried to access a file that was not authorized