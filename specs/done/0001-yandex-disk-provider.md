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
(the same base Google Drive uses) and authenticating exactly like the Google
Drive provider: the user registers their own Yandex OAuth application
(`cloud_api:disk.read`) and authorizes via the authorization-code flow, which
yields a refresh token; `MAYandexDiskAuth` keeps the access token fresh.

Auth alternatives were evaluated and rejected: the `x_token` exchange via
`ya-passport-auth` has no verified first-party Disk client; WebDAV
(login + app-password) requires a paid Yandex 360 subscription; Yandex has no
API to auto-create an OAuth app; a single shared app was rejected in favour of
the Google-Drive-style per-user app (no shared secret to ship/rotate). The REST
API with an OAuth token works on free accounts.

## Acceptance Criteria

1. A `filesystem_yandex_disk` instance can be added by entering the user's own
   Yandex OAuth `client_id` + `client_secret` and pressing **Authorize** (browser
   flow, variant A) or pasting a confirmation code (advanced, variant B); a
   refresh token is stored and the access token auto-refreshes. Root path is
   configurable (default `disk:/`).
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

- Unit: `_to_raw_item` mapping (file/dir/missing-md5); code exchange +
  `MAYandexDiskAuth` refresh (success/cache, rejected→LoginFailed,
  5xx→ProviderUnavailableError); provider hook delegation incl. Range passthrough
  and empty-folder → disk-root; config flow entries (OAuth fields, hidden refresh
  token, manual-code help link, first-setup vs reconfigure).
- Integration (`@pytest.mark.integration`): the real
  `CloudFileSystemProvider._scandir` maps a fixture listing into `FileSystemItem`s
  with MA proxy stream URLs.
- End-to-end (manual, requires a real Yandex account + a registered Disk OAuth
  app): add an instance via `./scripts/dev-server.sh`, paste a token, sync
  `disk:/Music`, verify browse/playback/seek/delete-resync.

## Sequence Diagram

```
Setup (variant A, default):
User enters client_id + client_secret → clicks Authorize
MA → AuthenticationHelper opens oauth.yandex.ru/authorize (response_type=code,
     redirect_uri=music-assistant.io/callback, state=local_cb, scope=disk.read)
Yandex → relay → local /callback/{session_id}?code=...
MA → POST oauth.yandex.ru/token (grant_type=authorization_code, secret)
     → access_token + refresh_token → stores refresh_token (hidden)
(variant B: user pastes the verification_code shown by Yandex → same token POST)

Runtime token:
MAYandexDiskAuth.async_get_access_token → cached, else POST token
     (grant_type=refresh_token) 60s before expiry; 400/401→LoginFailed, 5xx→transient

Sync/Browse:
CloudFileSystemProvider._scandir → _api_list_children(path)
    → YandexDiskApi.list_children (sets fresh access token on yadisk client)
    → yadisk AsyncClient.listdir (paginated)
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

- **Per-user app, no shared credentials:** each user registers their own Yandex
  OAuth app (free) with `cloud_api:disk.read`. Variant A additionally needs
  `https://music-assistant.io/callback` registered as a redirect URI; variant B
  (advanced) uses Yandex's `verification_code` page and needs no redirect URI.
  This is the Google-Drive-style model — nothing is shipped in the provider.
- **Rejected alternatives:** `x_token` exchange via `ya-passport-auth` (no verified
  first-party Disk client accepting `grant_type=x-token`); WebDAV + app-password
  (requires a paid Yandex 360 subscription); programmatic OAuth-app creation
  (Yandex exposes no such API for consumer accounts); a single shared MA app
  (would ship a client secret and centralise quota/rotation). A standalone
  `ya-passport-auth` disk-token-exchange branch (`feat/disk-token-exchange`)
  exists but is unused by this provider.
