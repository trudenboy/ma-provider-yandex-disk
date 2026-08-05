---
title: Authorization
sidebar:
  order: 3
---

The provider authenticates through **your own** Yandex OAuth application
with a single permission — read-only Disk access (`cloud_api:disk.read`).
This is the same model the built-in Google Drive provider uses.

## Device Flow

After submitting the setup form, Music Assistant displays a short code and the
Yandex verification URL. Enter the code on Yandex and approve access; the flow
detects confirmation and completes automatically. Expired codes are replaced
in place. There is no manual `auth_code` field or separate authentication
status to save.

## Token refresh

The access token is refreshed automatically via the refresh token. If Yandex
rotates the refresh token, the replacement is immediately persisted in
encrypted setup data. Re-authorization is only needed if access is revoked or
the application itself is deleted.

## Read-only

The scope grants read-only access — the provider physically cannot modify
or delete anything on your Disk.

Step-by-step application registration is covered on the
[Configuration](../../configuration/) page.
