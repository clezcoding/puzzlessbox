"""CAP-04 channel-neutral payload verification across mock Hermes adapters."""

import re
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

import dialog
from tests.conftest import (
    TEST_DRAFT,
    MockSession,
    active_draft_state,
    mock_categories,
)

CAPTURE_TEXT = "Notiz: Q3 Roadmap"
MARKDOWN_TOKENS = ("**", "#", "__")
HTML_CHARS = ("<", ">")
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def _capture_create_result() -> dict:
    return {
        "id": TEST_DRAFT,
        "status": "draft",
        "title": CAPTURE_TEXT,
        "type": "note",
        "summary": CAPTURE_TEXT,
    }


@contextmanager
def capture_patches(categories, create_result, mock_create_task):
    with (
        patch(
            "dialog.call_mcp_list_categories",
            new_callable=AsyncMock,
            return_value=categories,
        ),
        patch(
            "dialog.call_mcp_create_item",
            new_callable=AsyncMock,
            return_value=create_result,
        ),
        patch("dialog.asyncio.create_task", side_effect=mock_create_task),
    ):
        yield


@pytest.fixture
def telegram_session() -> MockSession:
    return MockSession()


@pytest.fixture
def whatsapp_session() -> MockSession:
    return MockSession()


@pytest.fixture
def discord_session() -> MockSession:
    return MockSession()


@pytest.mark.asyncio
async def test_telegram_same_payload(telegram_session, mock_categories, mock_create_task):
    create_result = _capture_create_result()
    with capture_patches(mock_categories, create_result, mock_create_task):
        reply = await dialog.handle_user_message(telegram_session, CAPTURE_TEXT)

    assert "Stash-Check" in reply
    assert "Eintrag sichern" in reply
    assert "Q3 Roadmap" in reply
    assert "Auto-Save in 30s" in reply


@pytest.mark.asyncio
async def test_whatsapp_same_payload(whatsapp_session, mock_categories, mock_create_task):
    create_result = _capture_create_result()
    with capture_patches(mock_categories, create_result, mock_create_task):
        reply = await dialog.handle_user_message(whatsapp_session, CAPTURE_TEXT)

    assert "Stash-Check" in reply
    assert "Eintrag sichern" in reply
    assert "Q3 Roadmap" in reply
    assert "Auto-Save in 30s" in reply


@pytest.mark.asyncio
async def test_discord_same_payload(discord_session, mock_categories, mock_create_task):
    create_result = _capture_create_result()
    with capture_patches(mock_categories, create_result, mock_create_task):
        reply = await dialog.handle_user_message(discord_session, CAPTURE_TEXT)

    assert "Stash-Check" in reply
    assert "Eintrag sichern" in reply
    assert "Q3 Roadmap" in reply
    assert "Auto-Save in 30s" in reply


@pytest.mark.asyncio
async def test_all_channels_identical_payload(
    telegram_session, whatsapp_session, discord_session, mock_categories, mock_create_task
):
    create_result = _capture_create_result()
    replies = []
    for session in (telegram_session, whatsapp_session, discord_session):
        with capture_patches(mock_categories, create_result, mock_create_task):
            replies.append(await dialog.handle_user_message(session, CAPTURE_TEXT))
    assert replies[0] == replies[1] == replies[2]


@pytest.mark.asyncio
async def test_all_channels_no_markdown(
    telegram_session, whatsapp_session, discord_session, mock_categories, mock_create_task
):
    create_result = _capture_create_result()
    for session in (telegram_session, whatsapp_session, discord_session):
        with capture_patches(mock_categories, create_result, mock_create_task):
            reply = await dialog.handle_user_message(session, CAPTURE_TEXT)
        for token in MARKDOWN_TOKENS:
            assert token not in reply
        for char in HTML_CHARS:
            assert char not in reply


@pytest.mark.asyncio
async def test_all_channels_same_edit_ack(
    telegram_session, whatsapp_session, discord_session, active_draft_state
):
    acks = []
    for session in (telegram_session, whatsapp_session, discord_session):
        session._state["active_draft"] = dict(active_draft_state)
        with patch(
            "dialog.call_mcp_update_item",
            new_callable=AsyncMock,
            return_value={"id": TEST_DRAFT},
        ):
            acks.append(
                await dialog.handle_user_message(session, "Titel: Neuer Titel")
            )
    assert acks[0] == acks[1] == acks[2]
    assert acks[0] == "✍️ Änderungen übernommen."


def test_channel_specific_buttons_only_in_adapter():
    pattern = re.compile(r"telegram|whatsapp|discord", re.I)
    for rel in ("dialog.py", "formatters.py"):
        text = (PLUGIN_ROOT / rel).read_text()
        assert not pattern.search(text)
