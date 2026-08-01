import pytest

TEST_OWNER = "11111111-1111-4111-8111-111111111111"
TEST_CATEGORY = "33333333-3333-4333-8333-333333333333"
TEST_DRAFT = "22222222-2222-4222-8222-222222222222"


@pytest.fixture
def mock_create_item_result():
    return {
        "id": TEST_DRAFT,
        "status": "draft",
        "title": "Meeting mit Team",
        "type": "note",
        "summary": "Q3 Roadmap besprechen.",
    }
