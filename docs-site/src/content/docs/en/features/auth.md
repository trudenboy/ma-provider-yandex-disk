---
title: Authorization
sidebar:
  order: 3
---

The provider authenticates through **your own** Yandex OAuth application
with a single permission — read-only Disk access (`cloud_api:disk.read`).
This is the same model the built-in Google Drive provider uses.

## Device Flow

Press **Sign in with Yandex** in the setup form. Music Assistant hosts a page
with a short code and a link to Yandex. Enter that code on Yandex and approve
access; the provider receives the access/refresh token pair automatically.
There is no manual `auth_code` field.

## Token refresh

The access token is refreshed automatically via the refresh token;
re-authorization is only needed if the application's access is revoked or
the application itself is deleted.

## Read-only

The scope grants read-only access — the provider physically cannot modify
or delete anything on your Disk.

Step-by-step application registration is covered on the
[Configuration](../../configuration/) page.
