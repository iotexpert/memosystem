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

    @staticmethod
    def convert(value):
        if value == MemoActivity.Create:
            return "Create"
        if value == MemoActivity.Signoff:
            return "Signoff"
        if value == MemoActivity.Sign:
            return "Sign"
        if value == MemoActivity.Unsign:
            return "Unsign"
        if value == MemoActivity.Activate:
            return "Activate"
        if value == MemoActivity.Obsolete:
            return "Obsolete"
        if value == MemoActivity.Cancel:
            return "Cancel"
        if value == MemoActivity.Reject:
            return "Reject"
        if value == MemoActivity.IllegalFile:
            return "IllegalFile"
        return "Unknown"
"""
    def __str__(self):
        current_app.logger.info("checking string value")
        if self.value == 1:
            return "Create"
        if self.value == 2:
            return "Signoff"
        if self.value == 3:
            return "Sign"
        if self.value == 4:
            return "Unsign"
        if self.value == 5:
            return "Activate"
        if self.value == 6:
            return "Obsolete"
        if self.value == 7:
            return "Cancel"
        if self.value == 8:
            return "Reject"
"""