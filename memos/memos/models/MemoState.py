import enum

class MemoState(enum.Enum):
    Draft = 1
    Signoff = 2
    Active = 3
    Obsolete = 4
    
    @staticmethod
    def is_valid(state):
        if state == "MemoState.Draft" or \
            state == "MemoState.Signoff" or \
            state == "MemoState.Active" or \
            state == "MemoState.Obsolete":
            return True
        else:
            return False
            

    def compare_short_name(self,name):
        if self.value == 1 and name=="Draft":
            return True
        elif self.value == 2 and name == "Signoff":
            return True
        elif self.value == 3 and name == "Active":
            return True
        elif self.value == 4 and name == "Obsolete":
            return True
        return False

    def short_name(self):
        if self.value == 1:
            return "Draft"
        if self.value == 2:
            return "Signoff"
        if self.value == 3:
            return "Active"
        if self.value == 4:
            return "Obsolete"

