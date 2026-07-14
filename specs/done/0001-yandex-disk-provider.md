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
(the same base Google Drive uses) and reusing the fleet's shared Yandex login
library so the auth experience matches the other Yandex providers.

## Acceptance Criteria

1. A `filesystem_yandex_disk` provider instance can be added in MA, authenticated
   via the shared device-code or QR flow, with a configurable root path
   (default `disk:/`).
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
- End-to-end (manual, requires real Yandex account + Disk OAuth client): add an
  instance via `./scripts/dev-server.sh`, log in, sync `disk:/Music`, verify
  browse/playback/seek/delete-resync.

## Sequence Diagram

```
User → MA config: click "Login (device code)"
MA → ya_passport_auth: run_device_flow → x_token (+refresh_token)
MA → provider.auth.mint_disk_token(x_token)
provider.auth → (ya_passport_auth.ma.refresh_disk_token | local x-token exchange)
            → cloud_api:disk.* access token
MA stores x_token + disk_token (hidden, secure)

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

- The disk-scoped token exchange (`x_token → cloud_api:disk.*`) currently lives
  in `provider/auth.py` as a self-contained fallback and prefers
  `ya_passport_auth.ma.refresh_disk_token` when a release provides it. Its
  permanent home is `ya-passport-auth` (add `DISK_CLIENT_ID`/`DISK_CLIENT_SECRET`
  + `exchange_x_token_for_disk_token`), then bump the manifest/registry pin.
- `DISK_CLIENT_ID`/`DISK_CLIENT_SECRET` in `provider/constants.py` are
  placeholders and MUST be filled with the real public first-party Yandex Disk
  client credentials before the exchange can succeed.
- Borrow-from-`yandex_music` (reuse a linked instance's x_token) is a planned
  refinement via `ya_passport_auth.ma.borrow`.
