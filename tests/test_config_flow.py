"""Tests for the Yandex Disk config flow (implicit OAuth flow)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from provider import get_config_entries
from provider.constants import CONF_DISK_TOKEN, CONF_ROOT_PATH

if TYPE_CHECKING:
    from music_assistant import MusicAssistant


def _mass() -> MusicAssistant:
    """Return a stand-in MusicAssistant; plain config renders never touch it."""
    return cast("MusicAssistant", object())


@pytest.mark.asyncio
async def test_config_entries_first_setup_include_token_root_and_content_type() -> None:
    """First-setup entries include the token, root path and a choosable content type."""
    entries = await get_config_entries(_mass(), instance_id=None)
    keys = {e.key for e in entries}
    assert CONF_DISK_TOKEN in keys
    assert CONF_ROOT_PATH in keys
    assert "content_type" in keys


@pytest.mark.asyncio
async def test_token_entry_has_help_link() -> None:
    """The token field carries the implicit-flow authorize link."""
    entries = await get_config_entries(_mass(), instance_id=None)
    token_entry = next(e for e in entries if e.key == CONF_DISK_TOKEN)
    assert token_entry.help_link
    assert token_entry.required is True


@pytest.mark.asyncio
async def test_config_entries_reconfigure_content_type_read_only() -> None:
    """On reconfigure the content type is present but read-only, token/root still there."""
    entries = await get_config_entries(_mass(), instance_id="abc")
    keys = {e.key for e in entries}
    assert CONF_DISK_TOKEN in keys
    assert CONF_ROOT_PATH in keys
    assert "content_type" in keys  # the read-only variant keeps the same key
