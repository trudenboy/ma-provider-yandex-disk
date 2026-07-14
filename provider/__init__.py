"""Yandex Disk filesystem provider for Music Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from music_assistant_models.config_entries import ConfigEntry
from music_assistant_models.constants import SECURE_STRING_SUBSTITUTE
from music_assistant_models.enums import ConfigEntryType
from music_assistant_models.errors import LoginFailed

from music_assistant.providers.filesystem_local.constants import (
    CONF_ENTRY_CONTENT_TYPE,
    CONF_ENTRY_CONTENT_TYPE_READ_ONLY,
    CONF_ENTRY_IGNORE_ALBUM_PLAYLISTS,
    CONF_ENTRY_LIBRARY_SYNC_AUDIOBOOKS,
    CONF_ENTRY_LIBRARY_SYNC_PLAYLISTS,
    CONF_ENTRY_LIBRARY_SYNC_PODCASTS,
    CONF_ENTRY_LIBRARY_SYNC_TRACKS,
    CONF_ENTRY_MISSING_ALBUM_ARTIST,
    CONF_ENTRY_PROPAGATE_GENRES,
)

from . import auth
from .constants import (
    CALLBACK_REDIRECT_URL,
    CONF_ACTION_AUTH,
    CONF_ACTION_AUTH_MANUAL,
    CONF_AUTH_CODE,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_REFRESH_TOKEN,
    CONF_ROOT_PATH,
    DISK_ROOT,
)
from .provider import YandexDiskFileSystemProvider

if TYPE_CHECKING:
    from music_assistant_models.config_entries import ConfigValueType, ProviderConfig
    from music_assistant_models.provider import ProviderManifest

    from music_assistant import MusicAssistant
    from music_assistant.models import ProviderInstanceType


async def setup(
    mass: MusicAssistant, manifest: ProviderManifest, config: ProviderConfig
) -> ProviderInstanceType:
    """Initialize a provider instance from its configuration.

    :param mass: The MusicAssistant instance.
    :param manifest: The provider manifest.
    :param config: The provider (instance) configuration.
    :returns: The constructed provider instance.
    """
    # MA calls handle_async_init after setup returns; calling it here too would
    # register the stream route twice.
    return YandexDiskFileSystemProvider(mass, manifest, config)


async def get_config_entries(
    mass: MusicAssistant,
    instance_id: str | None = None,
    action: str | None = None,
    values: dict[str, ConfigValueType] | None = None,
) -> tuple[ConfigEntry, ...]:
    """Return the config entries for this provider.

    :param mass: The MusicAssistant instance.
    :param instance_id: Existing instance id (None on first setup).
    :param action: Optional action key from the config UI.
    :param values: Intermediate raw config values sent with the action.
    :returns: The ordered config entries.
    """
    if values is None:
        values = {}

    await _handle_auth_action(mass, instance_id, action, values)

    client_id = str(values.get(CONF_CLIENT_ID) or "")
    base_entries = (
        ConfigEntry(
            key=CONF_CLIENT_ID,
            type=ConfigEntryType.STRING,
            required=True,
            label="Yandex OAuth Client ID",
            description=(
                "Register an application at https://oauth.yandex.ru/ with the "
                "'cloud_api:disk.read' permission and paste its ID here."
            ),
            value=values.get(CONF_CLIENT_ID),
        ),
        ConfigEntry(
            key=CONF_CLIENT_SECRET,
            type=ConfigEntryType.SECURE_STRING,
            required=True,
            label="Yandex OAuth Client Secret",
            value=values.get(CONF_CLIENT_SECRET),
        ),
        ConfigEntry(
            key=CONF_ACTION_AUTH,
            type=ConfigEntryType.ACTION,
            label="Authorize with Yandex",
            description=(
                "Sign in and grant read-only access. Requires "
                f"'{CALLBACK_REDIRECT_URL}' to be registered as a redirect "
                "URI in your Yandex app."
            ),
            action=CONF_ACTION_AUTH,
            action_label="Authorize with Yandex",
        ),
        ConfigEntry(
            key=CONF_REFRESH_TOKEN,
            type=ConfigEntryType.SECURE_STRING,
            required=True,
            # filled by the authorize action(s) above; hidden from the user
            hidden=True,
            value=values.get(CONF_REFRESH_TOKEN),
        ),
        # advanced fallback (variant B): paste the confirmation code shown by
        # Yandex — no redirect URI needs to be registered
        ConfigEntry(
            key=CONF_AUTH_CODE,
            type=ConfigEntryType.STRING,
            required=False,
            advanced=True,
            label="Confirmation code (manual authorization)",
            description=(
                "Advanced: open the link, allow access, then paste the "
                "confirmation code Yandex shows and press the manual authorize "
                "action below."
            ),
            help_link=auth.manual_authorize_url(client_id) if client_id else None,
            value=values.get(CONF_AUTH_CODE),
        ),
        ConfigEntry(
            key=CONF_ACTION_AUTH_MANUAL,
            type=ConfigEntryType.ACTION,
            advanced=True,
            label="Authorize with pasted code",
            action=CONF_ACTION_AUTH_MANUAL,
            action_label="Authorize with pasted code",
        ),
        ConfigEntry(
            key=CONF_ROOT_PATH,
            type=ConfigEntryType.STRING,
            required=False,
            default_value=DISK_ROOT,
            value=values.get(CONF_ROOT_PATH),
        ),
        CONF_ENTRY_MISSING_ALBUM_ARTIST,
        CONF_ENTRY_IGNORE_ALBUM_PLAYLISTS,
        CONF_ENTRY_LIBRARY_SYNC_TRACKS,
        CONF_ENTRY_LIBRARY_SYNC_PLAYLISTS,
        CONF_ENTRY_LIBRARY_SYNC_PODCASTS,
        CONF_ENTRY_LIBRARY_SYNC_AUDIOBOOKS,
        CONF_ENTRY_PROPAGATE_GENRES,
    )

    # content type is only choosable at initial setup; read-only afterwards
    if instance_id is None:
        return (CONF_ENTRY_CONTENT_TYPE, *base_entries)
    return (*base_entries, CONF_ENTRY_CONTENT_TYPE_READ_ONLY)


async def _handle_auth_action(
    mass: MusicAssistant,
    instance_id: str | None,
    action: str | None,
    values: dict[str, ConfigValueType],
) -> None:
    """Run the selected authorization action, writing the refresh token in place.

    :param mass: The MusicAssistant instance.
    :param instance_id: Existing instance id (for re-fetching a masked secret).
    :param action: The action key from the config UI.
    :param values: The config-flow values (mutated).
    """
    if action not in (CONF_ACTION_AUTH, CONF_ACTION_AUTH_MANUAL):
        return
    client_id = str(values.get(CONF_CLIENT_ID) or "")
    client_secret = str(values.get(CONF_CLIENT_SECRET) or "")
    # the frontend masks a previously stored secret; fetch the real value
    if client_secret == SECURE_STRING_SUBSTITUTE and instance_id:
        client_secret = str(
            mass.config.get_raw_provider_config_value(instance_id, CONF_CLIENT_SECRET) or ""
        )
    if not client_id or not client_secret:
        raise LoginFailed("Enter the Yandex OAuth Client ID and Client Secret first")

    if action == CONF_ACTION_AUTH and values.get("session_id"):
        values[CONF_REFRESH_TOKEN] = await auth.authorize(
            mass, str(values["session_id"]), client_id, client_secret
        )
    elif action == CONF_ACTION_AUTH_MANUAL:
        values[CONF_REFRESH_TOKEN] = await auth.exchange_manual_code(
            mass, str(values.get(CONF_AUTH_CODE) or ""), client_id, client_secret
        )
        # the one-time code must not be persisted
        values[CONF_AUTH_CODE] = None
