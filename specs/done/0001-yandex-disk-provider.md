---
id: 0001
title: Yandex Disk filesystem provider
size: L
status: done
priority: P1
effort_minutes: 480
feature_id: BROWSE
---

## Problem Statement

Music Assistant has cloud filesystem providers for Google Drive and generic
cloud storage, but none for **Yandex Disk** — a popular storage service in the
provider fleet's primary (Russian-speaking) audience. Users who keep their
personal music on Yandex Disk cannot browse, sync or stream it in MA. This
provider closes that gap by subclassing the shared `CloudFileSystemProvider`
(the same base Google Drive uses) and authenticating with a read-only Yandex
Disk OAuth token obtained via the implicit flow (`response_type=token`), the
same pattern the yandex_smarthome provider uses for its skill token.

Auth alternatives were evaluated and rejected: the `x_token` exchange via
`ya-passport-auth` has no verified first-party Disk client; WebDAV
(login + app-password) requires a paid Yandex 360 subscription. The REST API
with an OAuth token works on free accounts and is the default.

## Acceptance Criteria

1. A `filesystem_yandex_disk` provider instance can be added in MA by pasting a
   `cloud_api:disk.read` OAuth token (obtained via the linked implicit-flow
   authorize URL), with a configurable root path (default `disk:/`).
2. Library sync populates tracks, albums, artists and playlists from audio files
   under the configured root; a re-sync with no disk changes reports no changes
   (checksum = resource `md5`).
3. Browsing folders works interactively (served from the base's 300s dir cache).
4. Playback streams a track through MA's own proxy route; ffmpeg reads tags and
   embedded art over that route.
5. Seeking mid-track works — the client `Range` header reaches Yandex's
   pre-signed download href and returns HTTP 206.
6. Deleting a file on Yandex Disk and re-syncing removes it from the library.
7. Auth/transport failures map to MA errors: `LoginFailed` (re-auth),
   `ProviderUnavailableError` (transient), `MediaNotFoundError` (missing item),
   `SetupFailedError` (bad root/misconfig).

## Test Plan

- Unit: `_to_raw_item` mapping (file/dir/missing-md5); `mint_disk_token`
  delegation + failure modes; provider hook delegation incl. Range passthrough
  and empty-folder → disk-root; config flow entries (first-setup vs reconfigure,
  auth actions present).
- Integration (`@pytest.mark.integration`): the real
  `CloudFileSystemProvider._scandir` maps a fixture listing into `FileSystemItem`s
  with MA proxy stream URLs.
- End-to-end (manual, requires a real Yandex account + a registered Disk OAuth
  app): add an instance via `./scripts/dev-server.sh`, paste a token, sync
  `disk:/Music`, verify browse/playback/seek/delete-resync.

## Sequence Diagram

```
Setup:
User → opens YANDEX_OAUTH_URL (response_type=token, client_id=<MA disk app>)
Yandex → shows cloud_api:disk.read token → user pastes it into disk_token field
MA stores disk_token (hidden, secure)

Sync/Browse:
CloudFileSystemProvider._scandir → _api_list_children(path)
    → YandexDiskApi.list_children → yadisk AsyncClient.listdir (paginated)
    → RawItem[] → FileSystemItem[] (absolute_path = MA proxy URL)

Playback:
player → GET {base_url}/{instance_id}_stream?path=...
    → _handle_stream_request (forwards Range)
    → _api_download_response → YandexDiskApi.download_response
    → get_download_link (fresh pre-signed href) → aiohttp GET (Range) → 200/206
```

## Data Model

`RawItem = tuple[str, str, bool, str, int | None]` = `(id, name, is_dir, checksum, size)`.
For Yandex Disk the path-addressed API means **id = the resource path**
(`disk:/...`). Mapping from a yadisk resource:

| yadisk resource field | RawItem slot | notes |
|-----------------------|--------------|-------|
| `path`                | id           | `disk:/...` |
| `name`                | name         | slashes → `_` by the base |
| `type == "dir"`       | is_dir       | |
| `md5` (files)         | checksum     | `""` for dirs, `"unknown"` if missing |
| `size` (files)        | size         | `None` for dirs |

`FileSystemItem.absolute_path` for files is MA's proxy URL
`{base_url}/{instance_id}_stream?path=<relative_path>` (set by the base's
`_to_item`).

## Notes / Follow-ups

- **Required before use:** register one Music Assistant Yandex OAuth application at
  <https://oauth.yandex.ru/> with the `cloud_api:disk.read` permission and set its
  id in `DISK_OAUTH_CLIENT_ID` (`provider/constants.py`). Until it is set, the
  config flow links to the app-registration page instead of a working authorize
  URL. This is the rclone-style "one shared app" model — end users register
  nothing.
- **Auto-capture (optional UX improvement):** replace the manual token paste with
  an `AuthenticationHelper` + a small JS relay route that reads the implicit-flow
  token from the URL fragment and stores it automatically. Manual paste then
  becomes the advanced fallback.
- **Rejected alternatives:** `x_token` exchange via `ya-passport-auth` (no verified
  first-party Disk client that accepts `grant_type=x-token`); WebDAV +
  app-password (requires a paid Yandex 360 subscription). A standalone
  `ya-passport-auth` disk-token-exchange branch (`feat/disk-token-exchange`)
  exists but is unused by this provider.
