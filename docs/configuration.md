# Configuration

Authentication follows the built-in cloud-filesystem setup model: you register
your own Yandex OAuth application and authorize Music Assistant against it.
Authorization uses Yandex's official Device Flow. Music Assistant shows the
verification URL and short code, waits for confirmation, and stores the refresh
token automatically. There is no manual `auth_code` field or separate Save step.

## 1. Register a Yandex OAuth application (one-time)

1. Go to <https://oauth.yandex.ru/> and create an application.
2. Under **Data access**, add the permission **`cloud_api:disk.read`**.
3. Copy the application's **ClientID** and **Client secret**.

## 2. Add the provider

1. In Music Assistant: **Settings → Providers → Add Provider → Yandex Disk**.
2. Paste the **Client ID** and **Client Secret**.
3. Choose the **Content type** (music / audiobooks / podcasts).
4. Set **Root folder to scan**. Use a path such as `disk:/Music`, or keep
   `root` to scan the whole disk.
5. Continue. Music Assistant shows a short code and the Yandex verification URL.
6. Open that URL, enter the code, and allow access. Music Assistant detects the
   confirmation and completes setup automatically. If the code expires while
   you are signing in, a fresh one is displayed without returning to the form.

During reconfiguration, leave **Client Secret** blank to reuse the securely
stored value. Entering a new secret replaces it after authorization succeeds.

## Why your own app?

Yandex has no API to create OAuth apps programmatically, and no verified public
first-party client that mints Disk tokens. WebDAV (login + app-password) would
avoid an app but requires a paid **Yandex 360** subscription. Registering a
personal OAuth app (free) with the read-only Disk scope is the same model the
Google Drive provider uses and works on free accounts.

## Streaming and seeking

Files stream through Music Assistant's own proxy route, which fetches a fresh
pre-signed download link per playback and forwards HTTP `Range` requests — so
seeking works even in long audiobooks.

## Notes

- The provider is **read-only**; it never writes to your Yandex Disk.
- The access token is refreshed automatically. Rotated refresh tokens are saved
  immediately in encrypted setup data; you only re-authorize if access is
  revoked or the OAuth application is deleted.
- Folder listings are cached for 5 minutes; library syncs always fetch fresh
  listings. Change detection uses each file's `md5`.
