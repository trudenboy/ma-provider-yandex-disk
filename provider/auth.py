"""Yandex Disk authentication (implicit OAuth flow).

Yandex Disk uses the implicit token flow (``response_type=token``), mirroring the
yandex_smarthome provider: the user opens the authorize URL, Yandex hands back a
``cloud_api:disk.read`` scoped token in the browser, and the user pastes it into
a SECURE_STRING config field. There is therefore no server-side auth exchange —
the pasted token *is* the credential used directly by the Yandex Disk API. This
module only builds the authorize link shown to the user.
"""

from __future__ import annotations

from .constants import OAUTH_APP_REGISTER_URL, YANDEX_OAUTH_URL


def authorize_url() -> str:
    """Return the implicit-flow authorize URL to show the user.

    :returns: The ``response_type=token`` authorize URL when an OAuth app id is
        configured, otherwise the app-registration page.
    """
    return YANDEX_OAUTH_URL


def is_configured() -> bool:
    """Return whether a Yandex Disk OAuth app id has been configured.

    :returns: True when :func:`authorize_url` yields a real authorize URL rather
        than the app-registration fallback.
    """
    return YANDEX_OAUTH_URL != OAUTH_APP_REGISTER_URL
