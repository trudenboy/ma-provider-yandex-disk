"""Async Yandex Disk API wrapper built on the yadisk library.

Owns a yadisk ``AsyncClient`` bound to Music Assistant's shared aiohttp session
(never closing it), mints/caches the disk-scoped token, and exposes the small
surface the ``CloudFileSystemProvider`` hooks need: folder listing, small-file
download, and a streaming download response that honours HTTP Range.

The Yandex Disk REST API is path-addressed, so resource paths (``disk:/...``)
double as the opaque "file id" the base class passes around.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp
import yadisk
from music_assistant_models.errors import (
    LoginFailed,
    MediaNotFoundError,
    ProviderUnavailableError,
)
from yadisk.exceptions import (
    PathNotFoundError,
    TooManyRequestsError,
    UnauthorizedError,
    YaDiskError,
)
from yadisk.sessions.aiohttp_session import AIOHTTPSession

from .auth import mint_disk_token

if TYPE_CHECKING:
    from music_assistant import MusicAssistant
    from music_assistant.providers.filesystem_cloud.base import RawItem

# fields requested per resource to keep listings slim
_FIELDS = ("name", "path", "type", "size", "md5", "modified")


class _SharedAIOHTTPSession(AIOHTTPSession):
    """AIOHTTPSession that reuses MA's shared ClientSession and never closes it."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Wrap an existing session without taking ownership of it.

        :param session: Music Assistant's shared aiohttp ClientSession.
        """
        # deliberately skip AIOHTTPSession.__init__ (it creates its own session)
        self._session = session

    async def close(self) -> None:
        """No-op: Music Assistant owns the shared session's lifecycle."""


def _to_raw_item(resource: object) -> RawItem:
    """Map a yadisk resource object to the base's ``RawItem`` tuple.

    :param resource: A yadisk (Async)ResourceObject.
    :returns: ``(id, name, is_dir, checksum, size)`` where id is the disk path.
    """
    is_dir = getattr(resource, "type", None) == "dir"
    checksum = "" if is_dir else (getattr(resource, "md5", None) or "unknown")
    size = None if is_dir else getattr(resource, "size", None)
    return (
        str(getattr(resource, "path", "")),
        str(getattr(resource, "name", "")),
        is_dir,
        checksum,
        size,
    )


class YandexDiskApi:
    """Thin async facade over yadisk for the filesystem provider."""

    def __init__(self, mass: MusicAssistant, x_token: str) -> None:
        """Initialise the API wrapper.

        :param mass: The MusicAssistant instance (for its shared http session).
        :param x_token: The stored Passport x_token used to mint disk tokens.
        """
        self.mass = mass
        self._x_token = x_token
        self._disk_token: str | None = None
        self._client = yadisk.AsyncClient(
            token="",
            session=_SharedAIOHTTPSession(mass.http_session),
        )

    async def get_token(self) -> str:
        """Return a valid disk-scoped token, minting one if needed.

        :returns: The disk-scoped OAuth token.
        """
        if self._disk_token is None:
            self._disk_token = await mint_disk_token(self._x_token)
            self._client.token = self._disk_token
        return self._disk_token

    async def list_children(self, folder_path: str) -> list[RawItem]:
        """List a folder's children (yadisk auto-paginates).

        :param folder_path: Disk path of the folder (``disk:/...``).
        :returns: One ``RawItem`` per child.
        """
        await self.get_token()
        try:
            return await self._collect_children(folder_path)
        except UnauthorizedError:
            await self._reauth()
            return await self._collect_children(folder_path)
        except PathNotFoundError as err:
            raise MediaNotFoundError(f"Yandex Disk folder not found: {folder_path}") from err
        except TooManyRequestsError as err:
            raise ProviderUnavailableError(f"Yandex Disk rate limited: {err}") from err
        except YaDiskError as err:
            raise ProviderUnavailableError(f"Yandex Disk API error: {err}") from err

    async def download_bytes(self, file_path: str) -> bytes:
        """Download a small file's full contents (nfo/m3u/lrc/images).

        :param file_path: Disk path of the file.
        :returns: The file contents.
        """
        link = await self._download_link(file_path)
        try:
            async with self.mass.http_session.get(link) as resp:
                resp.raise_for_status()
                return await resp.read()
        except aiohttp.ClientError as err:
            raise ProviderUnavailableError(f"Yandex Disk download failed: {err}") from err

    async def download_response(
        self, file_path: str, headers: dict[str, str]
    ) -> aiohttp.ClientResponse:
        """Open a streaming download for a file (fresh pre-signed href per call).

        :param file_path: Disk path of the file.
        :param headers: Request headers (may include ``Range`` for seeking).
        :returns: An open aiohttp response; the caller closes it.
        """
        link = await self._download_link(file_path)
        try:
            # pre-signed downloader href: no Authorization header needed
            return await self.mass.http_session.get(link, headers=headers)
        except aiohttp.ClientError as err:
            raise ProviderUnavailableError(f"Yandex Disk stream failed: {err}") from err

    async def exists_dir(self, path: str) -> bool:
        """Return True if *path* exists and is a directory.

        :param path: Disk path to check.
        :returns: Whether the path is an existing directory.
        """
        await self.get_token()
        try:
            return await self._client.is_dir(path)
        except UnauthorizedError as err:
            raise LoginFailed(f"Yandex Disk authentication failed: {err}") from err
        except YaDiskError as err:
            raise ProviderUnavailableError(f"Yandex Disk API error: {err}") from err

    async def close(self) -> None:
        """Release the yadisk client (does not close MA's shared session)."""
        await self._client.close()

    async def _collect_children(self, folder_path: str) -> list[RawItem]:
        """Iterate a folder's children into ``RawItem`` tuples."""
        items: list[RawItem] = []
        async for entry in self._client.listdir(folder_path, fields=list(_FIELDS)):
            items.append(_to_raw_item(entry))
        return items

    async def _reauth(self) -> None:
        """Force a fresh disk token (called after a 401)."""
        self._disk_token = None
        await self.get_token()

    async def _download_link(self, file_path: str) -> str:
        """Fetch a fresh, short-lived pre-signed download href for *file_path*."""
        await self.get_token()
        try:
            return await self._client.get_download_link(file_path)
        except UnauthorizedError:
            await self._reauth()
            return await self._client.get_download_link(file_path)
        except PathNotFoundError as err:
            raise MediaNotFoundError(f"Yandex Disk file not found: {file_path}") from err
        except TooManyRequestsError as err:
            raise ProviderUnavailableError(f"Yandex Disk rate limited: {err}") from err
        except YaDiskError as err:
            raise ProviderUnavailableError(f"Yandex Disk API error: {err}") from err
