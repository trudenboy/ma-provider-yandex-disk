# Configuration

## Adding the provider

1. In Music Assistant, go to **Settings → Providers → Add Provider** and pick
   **Yandex Disk**.
2. Get a Yandex Disk OAuth token via the **implicit flow**:
   - Click the link shown next to the token field. It opens Yandex's
     authorization page (`https://oauth.yandex.ru/authorize?response_type=token&client_id=…`,
     scope `cloud_api:disk.read`).
   - Allow access; Yandex shows you the token. Copy it and paste it into the
     **Yandex Disk OAuth token** field.
3. Set **Root folder to scan** — a path on your Yandex Disk, e.g. `disk:/Music`.
   Leave it as `disk:/` to scan the whole disk.
4. Choose the **Content type** (music / audiobooks / podcasts). This is only
   selectable at first setup and read-only afterwards.

The token is scoped to read-only Disk access and is stored encrypted in Music
Assistant's provider config.

## Why a token and not a login/password?

Yandex Disk's WebDAV access (login + app-password) requires a paid **Yandex 360**
subscription. The REST API used here works on **free** Yandex Disk accounts and
only needs a read-only OAuth token, so it is the default.

## Streaming and seeking

Files are streamed through Music Assistant's own proxy route, which requests a
fresh, short-lived pre-signed download link from Yandex per playback and
forwards HTTP `Range` requests — so seeking works even in long audiobooks.

## Notes

- The provider is **read-only**: it never writes to your Yandex Disk.
- The OAuth token is long-lived (~1 year) but has no refresh; when it expires,
  repeat the authorization step to get a new one.
- Folder listings are cached for 5 minutes to keep browsing snappy; library
  syncs always fetch fresh listings, so new content is never missed.
- Change detection uses each file's `md5`, so re-syncs only reprocess files that
  actually changed.
