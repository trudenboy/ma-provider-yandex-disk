"""Yandex Disk filesystem provider constants."""

from typing import Final

# Config keys for the shared ya-passport-auth credential block.
CONF_X_TOKEN: Final[str] = "x_token"
CONF_DISK_TOKEN: Final[str] = "disk_token"
CONF_REFRESH_TOKEN: Final[str] = "refresh_token"
CONF_REMEMBER_SESSION: Final[str] = "remember_session"

# Provider-specific config.
CONF_ROOT_PATH: Final[str] = "root_path"

# Yandex Disk API root and default scan root (the REST API is path-addressed).
DISK_ROOT: Final[str] = "disk:/"

# ---------------------------------------------------------------------------
# Disk-scoped OAuth token exchange (x_token -> cloud_api:disk.* token).
#
# The shared login (ya-passport-auth) yields a Passport ``x_token``; the Yandex
# Disk REST API needs a disk-scoped OAuth token minted from it via the mobile
# OAuth endpoint with ``grant_type=x-token`` and a first-party Disk client.
#
# These are public first-party client credentials (compiled into the Yandex
# Disk Android app), NOT secrets — analogous to the music/passport clients in
# ``ya_passport_auth.constants``. They MUST be filled with the real published
# values before the exchange can succeed; until then ``mint_disk_token`` raises
# a clear error. The permanent home for these is ``ya-passport-auth`` itself
# (see the provider spec); the provider prefers the library's
# ``refresh_disk_token`` when a release ships it.
# ---------------------------------------------------------------------------
DISK_CLIENT_ID: Final[str] = ""  # TODO: public Yandex Disk Android client_id
DISK_CLIENT_SECRET: Final[str] = ""  # TODO: public Yandex Disk Android client_secret
DISK_TOKEN_URL: Final[str] = "https://oauth.mobile.yandex.net/1/token"
