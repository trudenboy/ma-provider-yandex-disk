"""Tests for the yadisk-backed API client mapping and token handling."""

from __future__ import annotations

import pytest

import provider.api_client as api_client_mod
from provider.api_client import YandexDiskApi, _to_raw_item


class _Resource:
    """Minimal stand-in for a yadisk resource object."""

    def __init__(self, **kwargs: object) -> None:
        self.__dict__.update(kwargs)


def test_to_raw_item_file() -> None:
    """A file resource maps to a RawItem with md5 checksum and size."""
    res = _Resource(path="disk:/Music/a.flac", name="a.flac", type="file", md5="abc", size=123)
    assert _to_raw_item(res) == ("disk:/Music/a.flac", "a.flac", False, "abc", 123)


def test_to_raw_item_dir_has_empty_checksum_and_no_size() -> None:
    """A directory has no size and an empty checksum."""
    res = _Resource(path="disk:/Music", name="Music", type="dir", md5=None, size=None)
    assert _to_raw_item(res) == ("disk:/Music", "Music", True, "", None)


def test_to_raw_item_file_without_md5_falls_back() -> None:
    """A file lacking md5 gets the 'unknown' checksum sentinel."""
    res = _Resource(path="disk:/x.mp3", name="x.mp3", type="file", md5=None, size=1)
    _id, _name, is_dir, checksum, size = _to_raw_item(res)
    assert is_dir is False
    assert checksum == "unknown"
    assert size == 1


@pytest.mark.asyncio
async def test_get_token_mints_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_token mints via mint_disk_token and caches the result."""
    calls: list[str] = []

    async def fake_mint(x_token: str) -> str:
        calls.append(x_token)
        return "disk-tok"

    monkeypatch.setattr(api_client_mod, "mint_disk_token", fake_mint)
    api = YandexDiskApi.__new__(YandexDiskApi)
    api._x_token = "xt"
    api._disk_token = None

    class _Client:
        token = ""

    api._client = _Client()  # type: ignore[assignment]

    assert await api.get_token() == "disk-tok"
    assert await api.get_token() == "disk-tok"  # cached
    assert calls == ["xt"]
    assert api._client.token == "disk-tok"
