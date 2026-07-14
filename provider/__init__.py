"""Yandex Disk filesystem provider for Music Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from music_assistant_models.config_entries import ConfigEntry
from music_assistant_models.enums import ConfigEntryType
from ya_passport_auth.ma import (
    ACTION_AUTH_DEVICE,
    ACTION_AUTH_QR,
    ACTION_CLEAR_AUTH,
    AuthConfigSpec,
    KeySpec,
    build_auth_config_entries,
)

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
    CONF_DISK_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_REMEMBER_SESSION,
    CONF_ROOT_PATH,
    CONF_X_TOKEN,
    DISK_ROOT,
)
from .provider import YandexDiskFileSystemProvider

if TYPE_CHECKING:
    from music_assistant_models.config_entries import ConfigValueType, ProviderConfig
    from music_assistant_models.provider import ProviderManifest

    from music_assistant import MusicAssistant
    from music_assistant.models import ProviderInstanceType

# The disk-scoped token is minted from the x_token; it is stored in the
# ``music_token`` slot of the shared cascade KeySpec so the library's
# authenticated-state and hidden-storage logic works unchanged.
_AUTH_SPEC = AuthConfigSpec(
    keys=KeySpec(
        x_token=CONF_X_TOKEN,
        music_token=CONF_DISK_TOKEN,
        refresh_token=CONF_REFRESH_TOKEN,
        remember_session=CONF_REMEMBER_SESSION,
    ),
    flows=frozenset({"device", "qr"}),
)


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

    await _handle_auth_action(mass, action, values)

    authed = bool(values.get(CONF_X_TOKEN))
    status_label = "Authenticated to Yandex Disk." if authed else "Not authenticated."
    auth_entries = build_auth_config_entries(_AUTH_SPEC, values, status_label=status_label)

    root_entry = ConfigEntry(
        key=CONF_ROOT_PATH,
        type=ConfigEntryType.STRING,
        required=False,
        default_value=DISK_ROOT,
        value=values.get(CONF_ROOT_PATH),
    )

    base_entries = (
        *auth_entries,
        root_entry,
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
    mass: MusicAssistant, action: str | None, values: dict[str, ConfigValueType]
) -> None:
    """Run the selected login flow, writing tokens into *values* in place.

    :param mass: The MusicAssistant instance.
    :param action: The action key from the config UI.
    :param values: The config-flow values (mutated).
    """
    if action in (ACTION_AUTH_DEVICE, ACTION_AUTH_QR) and values.get("session_id"):
        session_id = str(values["session_id"])
        if action == ACTION_AUTH_DEVICE:
            x_token, refresh = await auth.perform_device_auth(mass, session_id)
            values[CONF_REFRESH_TOKEN] = refresh
        else:
            x_token = await auth.perform_qr_auth(mass, session_id)
            values[CONF_REFRESH_TOKEN] = None
        values[CONF_X_TOKEN] = x_token
        # mint the disk token now so is_authenticated() reflects success
        values[CONF_DISK_TOKEN] = await auth.mint_disk_token(x_token)
    elif action == ACTION_CLEAR_AUTH:
        values[CONF_X_TOKEN] = None
        values[CONF_DISK_TOKEN] = None
        values[CONF_REFRESH_TOKEN] = None
