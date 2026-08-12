import pytest

from researchos.infrastructure.bot.telegram_bot import _split_message


@pytest.mark.unit
def test_split_message_under_limit_returns_single_chunk():
    text = "short answer"
    assert _split_message(text, limit=100) == [text]


@pytest.mark.unit
def test_split_message_breaks_on_whitespace():
    text = "aaaa bbbb cccc dddd"
    chunks = _split_message(text, limit=10)

    assert chunks == ["aaaa bbbb", "cccc dddd"]
    assert all(len(chunk) <= 10 for chunk in chunks)


@pytest.mark.unit
def test_split_message_reassembles_to_original():
    text = "word " * 500
    chunks = _split_message(text, limit=4096)

    assert " ".join(chunks) == text
    assert all(len(chunk) <= 4096 for chunk in chunks)


@pytest.mark.unit
def test_split_message_hard_cut_when_no_whitespace():
    text = "a" * 25
    chunks = _split_message(text, limit=10)

    assert chunks == ["a" * 10, "a" * 10, "a" * 5]
