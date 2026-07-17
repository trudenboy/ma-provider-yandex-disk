---
title: Streaming and seeking
sidebar:
  order: 2
---

Files play back at source quality — the provider never transcodes and
serves the bytes as-is.

## How streaming works

Players never talk to Yandex directly: audio flows through Music
Assistant's own proxy route. For every playback the provider fetches a
fresh pre-signed download link from the Disk API, so link expiry never
interrupts playback.

## Seeking

The player's HTTP `Range` header is forwarded to Yandex untouched, so
seeking doesn't require re-downloading the file from the start — noticeable
on long audiobooks and DJ sets.
