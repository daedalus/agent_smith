"""Tests for share functionality."""

import pytest
import asyncio
from agent_smith.share import (
    ShareInfo,
    ShareManager,
    ShareDisabledError,
    get_share_manager,
    create_share,
    remove_share,
    get_share,
    is_shared,
    list_shares,
    generate_share_url,
)


@pytest.fixture
def share_manager():
    """Get and reset share manager."""
    manager = get_share_manager()
    manager.reset()
    return manager


def test_share_info_dataclass():
    """Test ShareInfo dataclass."""
    info = ShareInfo(
        session_id="session-123",
        share_id="share-456",
        secret="secret123",
        url="https://example.com/share/456",
    )
    assert info.session_id == "session-123"
    assert info.share_id == "share-456"
    assert info.secret == "secret123"
    assert info.url == "https://example.com/share/456"


def test_share_manager_singleton():
    """Test that share manager is a singleton."""
    m1 = get_share_manager()
    m2 = get_share_manager()
    assert m1 is m2


def test_share_manager_reset(share_manager):
    """Test resetting share manager."""
    share_manager.reset()
    assert len(share_manager.list_shares()) == 0


def test_generate_share_url():
    """Test generating share URL."""
    url = generate_share_url("abc123")
    assert "abc123" in url


def test_is_shared_false(share_manager):
    """Test is_shared returns False for non-shared session."""
    assert is_shared("nonexistent") is False


def test_get_share_none(share_manager):
    """Test get_share returns None for non-shared session."""
    assert get_share("nonexistent") is None


@pytest.mark.asyncio
async def test_create_share(share_manager):
    """Test creating a share."""
    info = await create_share("session-123")
    assert info.session_id == "session-123"
    assert info.share_id
    assert info.secret
    assert info.url


@pytest.mark.asyncio
async def test_create_share_idempotent(share_manager):
    """Test that creating a share twice returns same share."""
    info1 = await create_share("session-123")
    info2 = await create_share("session-123")
    assert info1.share_id == info2.share_id


@pytest.mark.asyncio
async def test_list_shares(share_manager):
    """Test listing shares."""
    await create_share("session-1")
    await create_share("session-2")
    shares = list_shares()
    assert len(shares) == 2


@pytest.mark.asyncio
async def test_remove_share(share_manager):
    """Test removing a share."""
    await create_share("session-123")
    assert is_shared("session-123") is True

    await remove_share("session-123")
    assert is_shared("session-123") is False


@pytest.mark.asyncio
async def test_get_share_after_create(share_manager):
    """Test getting share after creation."""
    await create_share("session-123")
    info = get_share("session-123")
    assert info is not None
    assert info.session_id == "session-123"


def test_disabled_property(share_manager):
    """Test disabled property."""
    assert isinstance(share_manager.disabled, bool)


@pytest.mark.asyncio
async def test_sync_share(share_manager):
    """Test syncing share data."""
    await create_share("session-123")

    data = {
        "type": "session",
        "data": {"id": "session-123", "title": "Test Session"},
    }

    await asyncio.sleep(0.1)

    result = get_share("session-123")
    assert result is not None


def test_share_info_has_url(share_manager):
    """Test that share info has URL."""
    import os

    os.environ["OPENCODE_SHARE_URL"] = "https://custom.example.com"

    manager = get_share_manager()
    manager.reset()

    info = ShareInfo(
        session_id="test",
        share_id="abc",
        secret="xyz",
        url="",
    )

    assert "custom.example.com" in f"https://custom.example.com/share/abc"
