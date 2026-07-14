"""Yandex Disk filesystem provider constants."""

from typing import Final

# Config keys.
# The disk-scoped OAuth token, obtained by the user via the implicit flow
# (``response_type=token``) and pasted into a SECURE_STRING field — the same
# approach as the yandex_smarthome provider.
CONF_DISK_TOKEN: Final[str] = "disk_token"
CONF_ROOT_PATH: Final[str] = "root_path"

# Yandex Disk API root and default scan root (the REST API is path-addressed).
DISK_ROOT: Final[str] = "disk:/"

# ---------------------------------------------------------------------------
# Implicit OAuth flow (response_type=token).
#
# The user opens YANDEX_OAUTH_URL, Yandex returns a ``cloud_api:disk.read``
# scoped token directly in the browser, and the user pastes it into the token
# field. No client_secret is involved.
#
# DISK_OAUTH_CLIENT_ID must be the id of a Yandex OAuth application registered
# with the "cloud_api:disk.read" permission (register once at
# https://oauth.yandex.ru/ — the same one-app pattern yandex_smarthome uses).
# Until it is filled, the config flow links to the app-registration page instead
# of a broken authorize URL.
# ---------------------------------------------------------------------------
DISK_OAUTH_CLIENT_ID: Final[str] = ""  # TODO: id of the MA Yandex Disk OAuth app
OAUTH_APP_REGISTER_URL: Final[str] = "https://oauth.yandex.ru/"
YANDEX_OAUTH_URL: Final[str] = (
    f"https://oauth.yandex.ru/authorize?response_type=token&client_id={DISK_OAUTH_CLIENT_ID}"
    if DISK_OAUTH_CLIENT_ID
    else OAUTH_APP_REGISTER_URL
)
