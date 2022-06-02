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

    @staticmethod
    def get_state(state):
        if state == "MemoState.Draft":
            return MemoState.Draft
        elif state == "MemoState.Signoff":
            return MemoState.Signoff
        elif state == "MemoState.Active":
             return MemoState.Active   
        elif state == "MemoState.Obsolete":
            return MemoState.Obsolete
        else:
            return None

    def compare_short_name(self,name):
        return self.name == name

    def short_name(self):
        return self.name

