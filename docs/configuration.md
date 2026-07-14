# Configuration

## Adding the provider

1. In Music Assistant, go to **Settings → Providers → Add Provider** and pick
   **Yandex Disk**.
2. Authenticate with your Yandex account using one of the shared login flows:
   - **Login (device code)** — a short code is shown on an MA-hosted page; open
     the Yandex verification URL and confirm. Yields a refresh token so the
     session can be renewed silently.
   - **Login (QR)** — scan a QR code with the Yandex app.
3. Set **Root folder to scan** — a path on your Yandex Disk, e.g. `disk:/Music`.
   Leave it as `disk:/` to scan the whole disk.
4. Choose the **Content type** (music / audiobooks / podcasts). This is only
   selectable at first setup and read-only afterwards.

## How authentication works

The shared login yields a Yandex Passport `x_token` (and, for device flow, a
refresh token). The Yandex Disk REST API needs a *disk-scoped* OAuth token,
which the provider mints from the `x_token` on demand and caches. Tokens are
stored encrypted in MA's provider config and never shown in the UI.

If a token is rejected the provider raises a login error and you re-run the
login flow; transient Yandex outages surface as "provider unavailable" and do
not clear your stored credentials.

## Streaming and seeking

Files are streamed through Music Assistant's own proxy route, which requests a
fresh, short-lived pre-signed download link from Yandex per playback and
forwards HTTP `Range` requests — so seeking works even in long audiobooks.

## Notes

- The provider is **read-only**: it never writes to your Yandex Disk.
- Folder listings are cached for 5 minutes to keep browsing snappy; library
  syncs always fetch fresh listings, so new content is never missed.
- Change detection uses each file's `md5`, so re-syncs only reprocess files that
  actually changed.
