from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import dialog
import tools
from tests.conftest import (
    TEST_CATEGORY,
    TEST_DRAFT,
    TEST_LINKS_CATEGORY,
    TEST_TERMINE_CATEGORY,
    MockSession,
    mock_create_item_result,
)


@pytest.mark.asyncio
async def test_handle_user_message_happy_path(
    mock_create_item_result, mock_categories, mock_create_task
):
    session = MockSession()
    with (
        patch(
            "dialog.call_mcp_list_categories",
            new_callable=AsyncMock,
            return_value=mock_categories,
        ),
        patch(
            "dialog.call_mcp_create_item",
            new_callable=AsyncMock,
            return_value=mock_create_item_result,
        ) as mock_create,
        patch("dialog.asyncio.create_task", side_effect=mock_create_task),
    ):
        reply = await dialog.handle_user_message(session, "Meeting mit Team")

    mock_create.assert_awaited_once()
    call_kwargs = mock_create.await_args.kwargs
    assert call_kwargs["type"] == "note"
    assert call_kwargs["category_id"] == TEST_CATEGORY
    assert "Meeting mit Team" in reply
    assert "Stash-Check" in reply
    assert "Eintrag sichern" in reply
    assert session._state.get("active_draft") is not None


def test_plugin_modules_have_no_db_imports():
    forbidden = ("psycopg2", "sqlalchemy", "SQLModel")
    for name in forbidden:
        assert name not in dir(tools)
        assert name not in dir(dialog)


def test_tools_only_mcp_client_path():
    source = open(tools.__file__).read()
    assert "streamable_http_client" in source
    assert "call_api" not in source
    assert "psycopg2" not in source


# --- Task 1: Edit flow + concurrency ---


@pytest.mark.asyncio
async def test_edit_free_text_calls_update_item_only_changed_keys(active_draft_state):
    session = MockSession({"active_draft": active_draft_state})
    with patch(
        "dialog.call_mcp_update_item",
        new_callable=AsyncMock,
        return_value={"id": TEST_DRAFT},
    ) as mock_update:
        await dialog.handle_user_message(session, "Titel: Neuer Titel")

    mock_update.assert_awaited_once_with(TEST_DRAFT, title="Neuer Titel")


@pytest.mark.asyncio
async def test_edit_silent_ack_no_new_card(active_draft_state):
    session = MockSession({"active_draft": active_draft_state})
    with patch("dialog.call_mcp_update_item", new_callable=AsyncMock, return_value={}):
        reply = await dialog.handle_user_message(session, "Titel: Neuer Titel")

    assert reply == "✍️ Änderungen übernommen."
    assert "Stash-Check" not in reply


@pytest.mark.asyncio
async def test_explicit_confirm_calls_confirm_item_draft(active_draft_state):
    session = MockSession({"active_draft": active_draft_state})
    with (
        patch(
            "dialog.call_mcp_get_item_status",
            new_callable=AsyncMock,
            return_value="draft",
        ) as mock_status,
        patch(
            "dialog.call_mcp_confirm_item",
            new_callable=AsyncMock,
            return_value={"status": "confirmed"},
        ) as mock_confirm,
    ):
        reply = await dialog.handle_user_message(session, "Eintrag sichern")

    mock_status.assert_awaited_once_with(TEST_DRAFT)
    mock_confirm.assert_awaited_once_with(TEST_DRAFT)
    assert session._state.get("active_draft") is None
    assert reply == "✅ Eintrag erfolgreich gesichert!"


@pytest.mark.asyncio
async def test_explicit_confirm_status_aware_ack_auto_saved(active_draft_state):
    session = MockSession({"active_draft": active_draft_state})
    with (
        patch(
            "dialog.call_mcp_get_item_status",
            new_callable=AsyncMock,
            return_value="auto_saved",
        ),
        patch(
            "dialog.call_mcp_confirm_item",
            new_callable=AsyncMock,
            return_value={"status": "confirmed"},
        ),
    ):
        reply = await dialog.handle_user_message(session, "Eintrag sichern")

    assert reply == "✅ War schon automatisch gestasht."
    assert "erfolgreich gesichert" not in reply


@pytest.mark.asyncio
async def test_explicit_discard_calls_discard_item(active_draft_state):
    session = MockSession({"active_draft": active_draft_state})
    with patch(
        "dialog.call_mcp_discard_item",
        new_callable=AsyncMock,
        return_value={"status": "discarded"},
    ) as mock_discard:
        reply = await dialog.handle_user_message(session, "Verwerfen")

    mock_discard.assert_awaited_once_with(TEST_DRAFT)
    assert session._state.get("active_draft") is None
    assert reply == "🗑️ Eintrag verworfen."


@pytest.mark.asyncio
async def test_single_active_draft_conflict(active_draft_state, mock_categories):
    session = MockSession({"active_draft": active_draft_state})
    with (
        patch("dialog.call_mcp_list_categories", new_callable=AsyncMock) as mock_cats,
        patch("dialog.call_mcp_create_item", new_callable=AsyncMock) as mock_create,
    ):
        reply = await dialog.handle_user_message(session, "Neue Notiz während Draft")

    mock_cats.assert_not_awaited()
    mock_create.assert_not_awaited()
    assert "offenen Entwurf" in reply
    assert session._state.get("pending_capture_text") == "Neue Notiz während Draft"


@pytest.mark.asyncio
async def test_single_active_draft_wait_branch(active_draft_state):
    session = MockSession(
        {
            "active_draft": active_draft_state,
            "pending_capture_text": "Neue Notiz während Draft",
        }
    )
    with patch("dialog.call_mcp_create_item", new_callable=AsyncMock) as mock_create:
        reply = await dialog.handle_user_message(session, "warten")

    mock_create.assert_not_awaited()
    assert session._state.get("active_draft") is not None
    assert session._state.get("pending_capture_text") == "Neue Notiz während Draft"
    assert "halte die neue Notiz zurück" in reply


@pytest.mark.asyncio
async def test_single_active_draft_sichern_branch(
    active_draft_state, mock_create_item_result, mock_categories, mock_create_task
):
    session = MockSession(
        {
            "active_draft": active_draft_state,
            "pending_capture_text": "Zweite Notiz",
        }
    )
    with (
        patch(
            "dialog.call_mcp_confirm_item",
            new_callable=AsyncMock,
            return_value={"status": "confirmed"},
        ) as mock_confirm,
        patch(
            "dialog.call_mcp_list_categories",
            new_callable=AsyncMock,
            return_value=mock_categories,
        ),
        patch(
            "dialog.call_mcp_create_item",
            new_callable=AsyncMock,
            return_value=mock_create_item_result,
        ) as mock_create,
        patch("dialog.asyncio.create_task", side_effect=mock_create_task),
    ):
        reply = await dialog.handle_user_message(session, "sichern")

    mock_confirm.assert_awaited_once_with(TEST_DRAFT)
    mock_create.assert_awaited_once()
    assert session._state.get("pending_capture_text") is None
    assert "Stash-Check" in reply


@pytest.mark.asyncio
async def test_single_active_draft_verwerfen_branch(
    active_draft_state, mock_create_item_result, mock_categories, mock_create_task
):
    session = MockSession(
        {
            "active_draft": active_draft_state,
            "pending_capture_text": "Zweite Notiz",
        }
    )
    with (
        patch(
            "dialog.call_mcp_discard_item",
            new_callable=AsyncMock,
            return_value={"status": "discarded"},
        ) as mock_discard,
        patch(
            "dialog.call_mcp_list_categories",
            new_callable=AsyncMock,
            return_value=mock_categories,
        ),
        patch(
            "dialog.call_mcp_create_item",
            new_callable=AsyncMock,
            return_value=mock_create_item_result,
        ) as mock_create,
        patch("dialog.asyncio.create_task", side_effect=mock_create_task),
    ):
        reply = await dialog.handle_user_message(session, "verwerfen")

    mock_discard.assert_awaited_once_with(TEST_DRAFT)
    mock_create.assert_awaited_once()
    assert session._state.get("pending_capture_text") is None
    assert "Stash-Check" in reply


@pytest.mark.asyncio
async def test_list_categories_called_before_create_item(
    mock_create_item_result, mock_categories, mock_create_task
):
    session = MockSession()
    call_order: list[str] = []

    async def track_categories():
        call_order.append("list_categories")
        return mock_categories

    async def track_create(**_kwargs):
        call_order.append("create_item")
        return mock_create_item_result

    with (
        patch("dialog.call_mcp_list_categories", side_effect=track_categories),
        patch("dialog.call_mcp_create_item", side_effect=track_create),
        patch("dialog.asyncio.create_task", side_effect=mock_create_task),
    ):
        await dialog.handle_user_message(session, "Einkaufsliste")

    assert call_order == ["list_categories", "create_item"]


def test_llm_heuristic_url_to_link(mock_categories):
    item_type, _cat_id, _cat_name, _conf = dialog._llm_choose_type_category(
        "https://example.com/article", mock_categories
    )
    assert item_type == "link"

    item_type, _cat_id, _cat_name, _conf = dialog._llm_choose_type_category(
        "2026-08-15 14:00 Team-Meeting", mock_categories
    )
    assert item_type == "event"

    item_type, _cat_id, _cat_name, _conf = dialog._llm_choose_type_category(
        "Einkaufsliste Milch", mock_categories
    )
    assert item_type == "note"


def test_low_confidence_falls_back_to_inbox():
    sparse_categories = [{"id": "99999999-9999-4999-8999-999999999999", "name": "Misc"}]
    _item_type, cat_id, cat_name, confidence = dialog._llm_choose_type_category(
        "https://example.com", sparse_categories
    )
    assert confidence < 0.5
    assert cat_name == "Inbox"
    assert cat_id == "33333333-3333-4333-8333-333333333333"


# --- Task 2: Post-autosave poll ---


@pytest.mark.asyncio
async def test_schedule_autosave_poll_calls_get_item_status():
    session = MockSession()
    with patch(
        "dialog.call_mcp_get_item_status",
        new_callable=AsyncMock,
        return_value="draft",
    ) as mock_status:
        await dialog.schedule_autosave_poll(session, TEST_DRAFT, delay_seconds=0.01)

    mock_status.assert_awaited_once_with(TEST_DRAFT)


@pytest.mark.asyncio
async def test_autosave_ping_sent_on_auto_saved(active_draft_state):
    session = MockSession({"active_draft": dict(active_draft_state)})
    with patch(
        "dialog.call_mcp_get_item_status",
        new_callable=AsyncMock,
        return_value="auto_saved",
    ):
        await dialog.schedule_autosave_poll(session, TEST_DRAFT, delay_seconds=0.01)

    assert len(session.sent_messages) == 1
    assert "Automatisch gestasht" in session.sent_messages[0]
    assert session._state["active_draft"]["status"] == "auto_saved"


@pytest.mark.asyncio
async def test_autosave_ping_silent_on_confirmed():
    session = MockSession()
    with patch(
        "dialog.call_mcp_get_item_status",
        new_callable=AsyncMock,
        return_value="confirmed",
    ):
        await dialog.schedule_autosave_poll(session, TEST_DRAFT, delay_seconds=0.01)

    assert session.sent_messages == []


@pytest.mark.asyncio
async def test_autosave_ping_silent_on_discarded():
    session = MockSession()
    with patch(
        "dialog.call_mcp_get_item_status",
        new_callable=AsyncMock,
        return_value="discarded",
    ):
        await dialog.schedule_autosave_poll(session, TEST_DRAFT, delay_seconds=0.01)

    assert session.sent_messages == []


@pytest.mark.asyncio
async def test_poll_does_not_drive_timer():
    import inspect

    source = inspect.getsource(dialog.schedule_autosave_poll)
    assert "asyncio.sleep" in source
    assert "cron" not in source.lower()


@pytest.mark.asyncio
async def test_poll_then_confirm_uses_live_status(active_draft_state):
    session = MockSession({"active_draft": dict(active_draft_state)})
    status_calls: list[str] = []

    async def track_status(item_id):
        status_calls.append("poll" if len(status_calls) == 0 else "confirm")
        return "auto_saved"

    with (
        patch("dialog.call_mcp_get_item_status", side_effect=track_status),
        patch(
            "dialog.call_mcp_confirm_item",
            new_callable=AsyncMock,
            return_value={"status": "confirmed"},
        ),
    ):
        await dialog.schedule_autosave_poll(session, TEST_DRAFT, delay_seconds=0.01)
        reply = await dialog.handle_user_message(session, "Eintrag sichern")

    assert status_calls == ["poll", "confirm"]
    assert reply == "✅ War schon automatisch gestasht."
