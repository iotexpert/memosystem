from memos.models.Memo import Memo
from memos.models.MemoState import MemoState

def test_is_valid(db, session):
    assert MemoState.is_valid("MemoState.Draft")
    assert MemoState.is_valid("MemoState.Signoff")
    assert MemoState.is_valid("MemoState.Active")
    assert MemoState.is_valid("MemoState.Obsolete")
    assert not MemoState.is_valid("Draft")

def test_get_state(db, session):
    assert MemoState.get_state("MemoState.Draft") == MemoState.Draft
    assert MemoState.get_state("MemoState.Signoff") == MemoState.Signoff
    assert MemoState.get_state("MemoState.Active") == MemoState.Active
    assert MemoState.get_state("MemoState.Obsolete") == MemoState.Obsolete
    assert MemoState.get_state("Draft") == None

def test_short_name(db, session):
    assert MemoState.short_name(MemoState.Draft) == "Draft"
    assert MemoState.short_name(MemoState.Signoff) == "Signoff"
    assert MemoState.short_name(MemoState.Active) == "Active"
    assert MemoState.short_name(MemoState.Obsolete) == "Obsolete"

def test_compare_short_name(db, session):
    assert MemoState.compare_short_name(MemoState.Draft, "Draft")
    assert MemoState.compare_short_name(MemoState.Signoff, "Signoff")
    assert MemoState.compare_short_name(MemoState.Active, "Active")
    assert MemoState.compare_short_name(MemoState.Obsolete, "Obsolete")
    assert not MemoState.compare_short_name(MemoState.Obsolete, "Draft")