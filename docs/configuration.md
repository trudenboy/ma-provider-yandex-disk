# Configuration

Authentication follows the built-in Google Drive provider's token model: you
register your own Yandex OAuth application and authorize Music Assistant against
it. Music Assistant then keeps the access token fresh automatically via the
refresh token. No redirect URI needs to be registered — Yandex shows a
confirmation code that you paste in.

## 1. Register a Yandex OAuth application (one-time)

1. Go to <https://oauth.yandex.ru/> and create an application ("for API access").
2. Under **Data access**, add the permission **`cloud_api:disk.read`**.
3. Copy the application's **ClientID** and **Client secret**.

The redirect URI stays at Yandex's default (`https://oauth.yandex.ru/verification_code`);
you don't need to configure it.

## 2. Add the provider

1. In Music Assistant: **Settings → Providers → Add Provider → Yandex Disk**.
2. Paste the **Client ID** and **Client Secret**.
3. Click the link on the **Confirmation code** field, allow access, and copy the
   code Yandex shows.
4. Paste that code into the **Confirmation code** field and press **Authorize**.
   The provider exchanges it for a refresh token and stores it automatically.
5. Set **Root folder to scan** (e.g. `disk:/Music`; `disk:/` scans everything).
6. Choose the **Content type** (music / audiobooks / podcasts) — first-setup only.

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
- The access token is refreshed automatically; you only re-authorize if you
  revoke access or delete the app.
- Folder listings are cached for 5 minutes; library syncs always fetch fresh
  listings. Change detection uses each file's `md5`.
