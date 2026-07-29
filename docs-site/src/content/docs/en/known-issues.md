---
title: Known Issues
---

## Your own Yandex OAuth application is required

**Symptoms:** the provider can't be connected "in one click" — the form asks
for a Client ID and Client Secret.

**Cause:** Yandex has no verified public first-party client that mints Disk
tokens, and WebDAV app-password access requires a paid Yandex 360
subscription.

**Solution:** register a free application with the `cloud_api:disk.read`
permission — the [Configuration](../configuration/) page walks through it.
It's a one-time step.

---

## New files show up in Browse with a delay

**Symptoms:** a file was just uploaded to the Disk but is not yet visible in
the Browse tab.

**Cause:** folder listings are cached for 5 minutes to avoid hammering the
Yandex API on every click.

**Solution:** wait up to 5 minutes or trigger a library sync — syncs always
fetch fresh listings.

---

## Content type can't be changed after setup

**Symptoms:** the content type (music / audiobooks / podcasts) is not
editable on an existing instance.

**Cause:** the content type defines how the library is indexed and is set at
first setup only.

**Solution:** add a separate provider instance with the desired content type
(multiple instances are supported — e.g. one for `disk:/Music`, another for
`disk:/Audiobooks`).

---

## Provider stopped working after access was revoked

**Symptoms:** sync and playback fail with an authorization error.

**Cause:** the refresh token became invalid — the application's access was
revoked on [Yandex's access management page](https://id.yandex.ru/security)
or the application itself was deleted. As long as access is not revoked, the
token refreshes automatically and no re-authorization is needed.

**Solution:** re-authorize in the provider settings with **Sign in with
Yandex**, then enter the new Device Flow code on Yandex's page.

---

## First sync of a large library takes a while

**Symptoms:** after adding the provider the library fills up gradually and
the sync takes noticeable time.

**Cause:** on the first pass Music Assistant reads tags from the files
themselves, which means downloading portions of them from the Disk.

**Solution:** this is a one-time operation — let the first pass finish;
subsequent syncs compare file `md5` checksums and only process changes.
