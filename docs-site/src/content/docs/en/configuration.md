---
title: Configuration
---

Authentication uses Music Assistant's guided cloud-provider setup: you
register your **own** Yandex OAuth application and authorize Music Assistant
against it. Music Assistant shows Yandex's Device Flow URL and short code,
waits for confirmation and stores the refresh token automatically. Nothing is
pasted back into the provider form and there is no separate Save step.

## 1. Register a Yandex OAuth application (one-time)

1. Go to <https://oauth.yandex.ru/> and create an application.
2. Under **Data access**, add the permission **`cloud_api:disk.read`**.
3. Copy the application's **ClientID** and **Client secret**.

## 2. Add the provider

1. In Music Assistant: **Settings → Providers → Add Provider → Yandex Disk**.
2. Paste the **Client ID** and **Client Secret**.
3. Choose the **Content type** (music / audiobooks / podcasts).
4. Set **Root folder to scan**. Use a path such as `disk:/Music`, or keep
   `root` to scan everything.
5. Continue. Music Assistant displays a short code and the Yandex verification
   URL.
6. Open the URL, enter the code and allow access. Music Assistant detects the
   confirmation and completes setup automatically. An expired code is replaced
   without sending you back to the form.

When reconfiguring, leave **Client Secret** blank to reuse the securely stored
secret.

## Why your own app?

Yandex has no API to create OAuth apps programmatically, and no verified
public first-party client that mints Disk tokens. WebDAV (login +
app-password) would avoid an app but requires a paid **Yandex 360**
subscription. Registering a personal OAuth app (free) with the read-only Disk
scope is the same model the Google Drive provider uses and works on free
accounts.

## Streaming and seeking

Files stream through Music Assistant's own proxy route, which fetches a fresh
pre-signed download link per playback and forwards HTTP `Range` requests — so
seeking works even in long audiobooks.

## Notes

- The provider is **read-only**; it never writes to your Yandex Disk.
- The access token is refreshed automatically and rotated refresh tokens are
  immediately saved in encrypted setup data. You only re-authorize if you
  revoke access or delete the app.
- Folder listings are cached for 5 minutes; library syncs always fetch fresh
  listings. Change detection uses each file's `md5`.
