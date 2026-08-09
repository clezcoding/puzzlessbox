from unittest.mock import MagicMock

import pytest


def mock_create_task(coro, *args, **kwargs):
    if hasattr(coro, "close"):
        coro.close()
    return MagicMock()


@pytest.fixture(name="mock_create_task")
def _mock_create_task_fixture():
    return mock_create_task

TEST_OWNER = "11111111-1111-4111-8111-111111111111"
TEST_CATEGORY = "33333333-3333-4333-8333-333333333333"
TEST_DRAFT = "22222222-2222-4222-8222-222222222222"
TEST_LINKS_CATEGORY = "44444444-4444-4444-8444-444444444444"
TEST_TERMINE_CATEGORY = "55555555-5555-4555-8555-555555555555"


class MockSession:
    def __init__(self, state: dict | None = None) -> None:
        self._state = dict(state or {})
        self.sent_messages: list[str] = []

    async def get_state(self, key: str):
        return self._state.get(key)

    async def set_state(self, key: str, value) -> None:
        self._state[key] = value

    async def clear_state(self, key: str) -> None:
        self._state.pop(key, None)

    async def send_message(self, message: str) -> None:
        self.sent_messages.append(message)


@pytest.fixture
def mock_categories():
    return [
        {"id": TEST_CATEGORY, "name": "Inbox"},
        {"id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "name": "Notizen"},
        {"id": TEST_LINKS_CATEGORY, "name": "Links"},
        {"id": TEST_TERMINE_CATEGORY, "name": "Termine"},
    ]


@pytest.fixture
def active_draft_state():
    return {
        "id": TEST_DRAFT,
        "title": "Meeting mit Team",
        "type": "note",
        "category": "Inbox",
        "summary": "Q3 Roadmap besprechen.",
        "status": "draft",
    }


@pytest.fixture
def mock_create_item_result():
    return {
        "id": TEST_DRAFT,
        "status": "draft",
        "title": "Meeting mit Team",
        "type": "note",
        "summary": "Q3 Roadmap besprechen.",
    }
