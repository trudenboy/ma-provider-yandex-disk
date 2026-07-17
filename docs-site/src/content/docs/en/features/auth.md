---
title: Authorization
sidebar:
  order: 3
---

The provider authenticates through **your own** Yandex OAuth application
with a single permission — read-only Disk access (`cloud_api:disk.read`).
This is the same model the built-in Google Drive provider uses.

## Confirmation-code flow

No redirect URI needs to be registered: the application uses Yandex's
standard confirmation-code page. You follow the link from the setup form,
allow access, copy the code Yandex shows and paste it back — the provider
exchanges the code for an access/refresh token pair.

## Token refresh

The access token is refreshed automatically via the refresh token;
re-authorization is only needed if the application's access is revoked or
the application itself is deleted.

## Read-only

The scope grants read-only access — the provider physically cannot modify
or delete anything on your Disk.

Step-by-step application registration is covered on the
[Configuration](../../configuration/) page.
