"""Tests for the Yandex Disk auth helpers (implicit OAuth flow)."""

from __future__ import annotations

import pytest

from provider import auth
from provider.constants import OAUTH_APP_REGISTER_URL


def test_authorize_url_returns_configured_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """When an app id is configured, the implicit-flow authorize URL is used."""
    url = "https://oauth.yandex.ru/authorize?response_type=token&client_id=abc"
    monkeypatch.setattr(auth, "YANDEX_OAUTH_URL", url)
    assert auth.authorize_url() == url
    assert auth.is_configured() is True


def test_authorize_url_falls_back_to_register_page(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without an app id, the link points at the app-registration page."""
    monkeypatch.setattr(auth, "YANDEX_OAUTH_URL", OAUTH_APP_REGISTER_URL)
    assert auth.authorize_url() == OAUTH_APP_REGISTER_URL
    assert auth.is_configured() is False
