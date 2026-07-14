# Configuration

Authentication mirrors the built-in Google Drive provider: you register your own
Yandex OAuth application and authorize Music Assistant against it. Music
Assistant then keeps the access token fresh automatically via the refresh token.

## 1. Register a Yandex OAuth application (one-time)

1. Go to <https://oauth.yandex.ru/> and create an application.
2. Under **Data access**, add the permission **`cloud_api:disk.read`**.
3. Under **Platforms**, choose **Web services** and add the redirect URI
   `https://music-assistant.io/callback` (needed for the one-click flow below).
4. Copy the application's **ClientID** and **Client secret**.

## 2. Add the provider

1. In Music Assistant: **Settings → Providers → Add Provider → Yandex Disk**.
2. Paste the **Client ID** and **Client Secret**.
3. Click **Authorize with Yandex** — a Yandex page opens; allow access. The
   provider stores the resulting refresh token automatically.
4. Set **Root folder to scan** (e.g. `disk:/Music`; `disk:/` scans everything).
5. Choose the **Content type** (music / audiobooks / podcasts) — first-setup only.

### Advanced: manual authorization (no redirect URI)

If you don't want to register the redirect URI, use the **advanced** fields:
open the link on the *Confirmation code* field, allow access, copy the code
Yandex shows, paste it into that field and press **Authorize with pasted code**.
This uses Yandex's `verification_code` page, so no redirect URI is needed.

## Why your own app and not a shared one?

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
- The access token is refreshed automatically; you only re-authorize if you
  revoke access or delete the app.
- Folder listings are cached for 5 minutes; library syncs always fetch fresh
  listings. Change detection uses each file's `md5`.
