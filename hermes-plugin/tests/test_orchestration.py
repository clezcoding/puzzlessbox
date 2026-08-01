from unittest.mock import AsyncMock, patch

import pytest

import dialog
import tools
from tests.conftest import TEST_CATEGORY, TEST_DRAFT, mock_create_item_result


@pytest.mark.asyncio
async def test_handle_user_message_happy_path(mock_create_item_result):
    session = object()
    with patch(
        "dialog.call_mcp_create_item",
        new_callable=AsyncMock,
        return_value=mock_create_item_result,
    ) as mock_create:
        reply = await dialog.handle_user_message(session, "Meeting mit Team")

    mock_create.assert_awaited_once()
    call_kwargs = mock_create.await_args.kwargs
    assert call_kwargs["type"] == "note"
    assert call_kwargs["category_id"] == TEST_CATEGORY
    assert "Meeting mit Team" in reply
    assert "Stash-Check" in reply
    assert "Eintrag sichern" in reply


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
