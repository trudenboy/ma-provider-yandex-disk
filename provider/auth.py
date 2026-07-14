"""Yandex Disk authentication: thin wrappers over ya_passport_auth.ma.

Reuses the fleet's shared Yandex login (device-code page and QR flow). Login
yields a Passport ``x_token`` (plus a ``refresh_token`` for the device flow);
the disk-scoped OAuth token that the Yandex Disk REST API needs is minted from
that ``x_token`` on demand.

The disk-scoped exchange belongs long-term in ``ya-passport-auth`` alongside the
music-scoped one. Until a release ships ``ya_passport_auth.ma.refresh_disk_token``
this module falls back to a self-contained exchange so the provider is usable and
testable; once the library exposes it, that function is preferred automatically.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp
from music_assistant_models.errors import LoginFailed, ProviderUnavailableError, SetupFailedError
from ya_passport_auth import SecretStr
from ya_passport_auth.ma import DevicePageConfig, run_device_flow, run_qr_flow

from .constants import DISK_CLIENT_ID, DISK_CLIENT_SECRET, DISK_TOKEN_URL

if TYPE_CHECKING:
    from music_assistant import MusicAssistant

_LOGGER = logging.getLogger(__name__)

# Prefer the library's disk-token exchange when a release provides it; otherwise
# fall back to the local exchange below. Tests monkeypatch this attribute.
try:
    from ya_passport_auth.ma import refresh_disk_token  # type: ignore[attr-defined]
except ImportError:
    refresh_disk_token = None

PAGE_CONFIG = DevicePageConfig(
    domain="filesystem_yandex_disk",
    title={"en": "Login to Yandex Disk", "ru": "Вход в Яндекс Диск"},
)


async def perform_device_auth(mass: MusicAssistant, session_id: str) -> tuple[str, str | None]:
    """Run the shared device-code flow.

    :param mass: The MusicAssistant instance.
    :param session_id: Auth-session id supplied by the frontend.
    :returns: The Passport ``x_token`` and (device-flow only) refresh token.
    """
    result = await run_device_flow(mass, session_id, PAGE_CONFIG)
    creds = result.credentials
    refresh = creds.refresh_token
    return creds.x_token.get_secret(), (refresh.get_secret() if refresh is not None else None)


async def perform_qr_auth(mass: MusicAssistant, session_id: str) -> str:
    """Run the shared QR flow.

    :param mass: The MusicAssistant instance.
    :param session_id: Auth-session id supplied by the frontend.
    :returns: The Passport ``x_token`` (QR flow yields no refresh token).
    """
    result = await run_qr_flow(mass, session_id)
    return result.credentials.x_token.get_secret()


async def mint_disk_token(x_token: str) -> str:
    """Mint a disk-scoped OAuth token from a Passport ``x_token``.

    :param x_token: The stored Passport x_token.
    :returns: A ``cloud_api:disk.*`` scoped OAuth token as a plain string.
    :raises LoginFailed: No x_token is stored (re-auth required).
    :raises SetupFailedError: Disk client credentials are not configured.
    :raises ProviderUnavailableError: The exchange failed transiently.
    """
    if not x_token:
        raise LoginFailed("No Yandex x_token stored; authenticate first")
    if refresh_disk_token is not None:
        token: SecretStr = await refresh_disk_token(SecretStr(x_token))
        return token.get_secret()
    return await _exchange_x_token_for_disk_token(x_token)


async def _exchange_x_token_for_disk_token(x_token: str) -> str:
    """Exchange an x_token for a disk-scoped token via the mobile OAuth endpoint.

    Self-contained fallback used until ``ya-passport-auth`` ships the exchange.

    :param x_token: The Passport x_token.
    :returns: The disk-scoped OAuth access token.
    """
    if not DISK_CLIENT_ID or not DISK_CLIENT_SECRET:
        raise SetupFailedError(
            "Yandex Disk OAuth client credentials are not configured. "
            "Set DISK_CLIENT_ID/DISK_CLIENT_SECRET (or upgrade ya-passport-auth "
            "to a release exposing refresh_disk_token)."
        )
    data = {
        "grant_type": "x-token",
        "access_token": x_token,
        "client_id": DISK_CLIENT_ID,
        "client_secret": DISK_CLIENT_SECRET,
    }
    try:
        async with (
            aiohttp.ClientSession() as session,
            session.post(DISK_TOKEN_URL, data=data) as resp,
        ):
            payload = await resp.json(content_type=None)
            if resp.status in (400, 401):
                raise LoginFailed(f"Yandex Disk token exchange rejected: {payload}")
            resp.raise_for_status()
    except aiohttp.ClientError as err:
        raise ProviderUnavailableError(f"Yandex Disk token exchange failed: {err}") from err
    access_token = payload.get("access_token") if isinstance(payload, dict) else None
    if not access_token:
        raise LoginFailed("Yandex Disk token exchange returned no access_token")
    return str(access_token)
