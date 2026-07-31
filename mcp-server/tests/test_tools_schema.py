"""Pydantic schema rejection tests for MCP tools (MCP-01)."""

from __future__ import annotations

import pytest
from fastmcp.exceptions import ValidationError
from fastmcp.tools.function_tool import FunctionTool

from tests.conftest import TEST_CATEGORY_ID


@pytest.mark.asyncio
async def test_create_item_missing_type_rejects() -> None:
    from app.tools.items import create_item

    tool = FunctionTool.from_function(create_item)
    with pytest.raises(ValidationError):
        await tool.run({"title": "x", "category_id": TEST_CATEGORY_ID})


@pytest.mark.asyncio
async def test_create_item_invalid_enum_rejects() -> None:
    from app.tools.items import create_item

    tool = FunctionTool.from_function(create_item)
    with pytest.raises(ValidationError):
        await tool.run(
            {"title": "x", "type": "invalid", "category_id": TEST_CATEGORY_ID}
        )


@pytest.mark.asyncio
async def test_create_item_missing_category_id_rejects() -> None:
    from app.tools.items import create_item

    tool = FunctionTool.from_function(create_item)
    with pytest.raises(ValidationError):
        await tool.run({"title": "x", "type": "note"})
