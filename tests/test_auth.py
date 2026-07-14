"""Tests for the Yandex Disk auth wrappers."""

from __future__ import annotations

import pytest
from music_assistant_models.errors import LoginFailed, SetupFailedError
from ya_passport_auth.credentials import SecretStr

from provider import auth


@pytest.mark.asyncio
async def test_mint_disk_token_delegates_to_library(monkeypatch: pytest.MonkeyPatch) -> None:
    """mint_disk_token prefers the library exchange when available."""

    async def fake_refresh(x_token: SecretStr) -> SecretStr:
        assert x_token.get_secret() == "xt"
        return SecretStr("disk-tok")

    monkeypatch.setattr(auth, "refresh_disk_token", fake_refresh)
    assert await auth.mint_disk_token("xt") == "disk-tok"


@pytest.mark.asyncio
async def test_mint_disk_token_empty_raises() -> None:
    """An empty x_token is a terminal auth failure."""
    with pytest.raises(LoginFailed):
        await auth.mint_disk_token("")


@pytest.mark.asyncio
async def test_mint_disk_token_fallback_requires_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without library support and without configured creds the mint fails clearly."""
    monkeypatch.setattr(auth, "refresh_disk_token", None)
    monkeypatch.setattr(auth, "DISK_CLIENT_ID", "")
    monkeypatch.setattr(auth, "DISK_CLIENT_SECRET", "")
    with pytest.raises(SetupFailedError):
        await auth.mint_disk_token("xt")


def test_page_config_domain() -> None:
    """The device-code page is branded for this provider."""
    assert auth.PAGE_CONFIG.domain == "filesystem_yandex_disk"
