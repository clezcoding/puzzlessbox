import uuid

from formatters import format_confirmation
from schemas import DraftPreview

from tests.conftest import TEST_DRAFT


def _draft(type_: str) -> DraftPreview:
    return DraftPreview(
        id=uuid.UUID(TEST_DRAFT),
        title="Meeting mit Team",
        type=type_,
        category="Inbox",
        summary="Q3 Roadmap besprechen.",
    )


def test_format_confirmation_note():
    text = format_confirmation(_draft("note"))
    assert "Stash-Check" in text
    assert "Eintrag sichern" in text
    assert "Meeting mit Team" in text
    assert "Inbox" in text
    assert "Q3 Roadmap besprechen." in text
    assert "Typ: Notiz" in text


def test_format_confirmation_all_type_labels():
    expected = {
        "note": "Notiz",
        "task": "Task",
        "link": "Link",
        "event": "Termin",
    }
    for type_key, label in expected.items():
        text = format_confirmation(_draft(type_key))
        assert f"Typ: {label}" in text
