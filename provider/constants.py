"""Yandex Disk filesystem provider constants."""

from typing import Final

# Config keys (mirrors the Google Drive provider: the user registers their own
# Yandex OAuth application and enters its credentials).
CONF_CLIENT_ID: Final[str] = "client_id"
CONF_CLIENT_SECRET: Final[str] = "client_secret"
CONF_REFRESH_TOKEN: Final[str] = "refresh_token"
CONF_AUTH_CODE: Final[str] = "auth_code"
CONF_ROOT_PATH: Final[str] = "root_path"

# Config actions.
CONF_ACTION_AUTH: Final[str] = "auth"  # variant A: browser popup + relay callback
CONF_ACTION_AUTH_MANUAL: Final[str] = "auth_manual"  # variant B: paste a code

# Yandex Disk API root and default scan root (the REST API is path-addressed).
DISK_ROOT: Final[str] = "disk:/"

# Yandex OAuth endpoints and the read-only Disk scope.
OAUTH_AUTHORIZE_URL: Final[str] = "https://oauth.yandex.ru/authorize"
OAUTH_TOKEN_URL: Final[str] = "https://oauth.yandex.ru/token"
OAUTH_SCOPE: Final[str] = "cloud_api:disk.read"

# Variant A: the fixed MA relay page (registered as a redirect URI in the user's
# Yandex app); it forwards the OAuth ``code`` to the local callback smuggled in
# ``state`` — the same mechanism the Google Drive provider uses.
CALLBACK_REDIRECT_URL: Final[str] = "https://music-assistant.io/callback"
# Variant B: Yandex shows the code on this page for the user to copy (the default
# redirect for "API access" apps); no redirect URI needs to be registered.
VERIFICATION_CODE_REDIRECT: Final[str] = "https://oauth.yandex.ru/verification_code"
