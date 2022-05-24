from memos.models.MemoState import MemoState

def test_is_valid(db, session):
    assert MemoState.is_valid("MemoState.Draft")
    assert MemoState.is_valid("MemoState.Signoff")
    assert MemoState.is_valid("MemoState.Active")
    assert MemoState.is_valid("MemoState.Obsolete")
    assert not MemoState.is_valid("Draft")