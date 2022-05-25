from memos import revletter

def test_valid_rev():
    assert not revletter.valid_rev(None)
    assert not revletter.valid_rev(1)
    assert not revletter.valid_rev("01")
    assert revletter.valid_rev("A")