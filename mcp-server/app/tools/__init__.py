from app.tools.categories import (
    create_category,
    list_categories,
    register_tools as register_category_tools,
)
from app.tools.items import (
    confirm_item,
    create_item,
    discard_item,
    get_draft_status,
    move_item,
    register_tools as register_item_tools,
    update_item,
)


def register_tools(mcp, client) -> None:
    register_item_tools(mcp, client)
    register_category_tools(mcp, client)


__all__ = [
    "create_item",
    "confirm_item",
    "update_item",
    "move_item",
    "discard_item",
    "get_draft_status",
    "list_categories",
    "create_category",
    "register_tools",
]
