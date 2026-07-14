"""Yandex Disk filesystem provider for Music Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from music_assistant_models.config_entries import ConfigEntry
from music_assistant_models.enums import ConfigEntryType

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
from .constants import CONF_DISK_TOKEN, CONF_ROOT_PATH, DISK_ROOT
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
    mass: MusicAssistant,  # noqa: ARG001  # part of the MA plugin API signature
    instance_id: str | None = None,
    action: str | None = None,  # noqa: ARG001  # part of the MA plugin API signature
    values: dict[str, ConfigValueType] | None = None,
) -> tuple[ConfigEntry, ...]:
    """Return the config entries for this provider.

    :param mass: The MusicAssistant instance.
    :param instance_id: Existing instance id (None on first setup).
    :param action: Optional action key from the config UI.
    :param values: Intermediate raw config values sent with the action.
    :returns: The ordered config entries.
    """
    token_description = (
        "Open the link, allow access, then paste the token from the page here. "
        "The token is scoped to read-only Yandex Disk access."
    )
    if not auth.is_configured():
        token_description += (
            " NOTE: no Yandex Disk OAuth application is configured yet — register "
            "one (with the cloud_api:disk.read permission) at the linked page and "
            "set its client id in the provider."
        )

    base_entries = (
        ConfigEntry(
            key=CONF_DISK_TOKEN,
            type=ConfigEntryType.SECURE_STRING,
            required=True,
            label="Yandex Disk OAuth token",
            description=token_description,
            help_link=auth.authorize_url(),
            value=values.get(CONF_DISK_TOKEN) if values else None,
        ),
        ConfigEntry(
            key=CONF_ROOT_PATH,
            type=ConfigEntryType.STRING,
            required=False,
            default_value=DISK_ROOT,
            value=values.get(CONF_ROOT_PATH) if values else None,
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
