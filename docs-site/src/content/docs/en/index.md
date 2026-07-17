---
title: Yandex Disk Provider
description: Yandex Disk provider documentation for Music Assistant
---

<img src="https://raw.githubusercontent.com/trudenboy/ma-provider-yandex-disk/dev/provider/icon.svg" alt="Yandex Disk" style="width: 72px; float: right; margin: 0 0 1rem 1.5rem;" />


> Yandex Disk provider for Music Assistant — stream your own music files from Yandex Disk


[![CI](https://github.com/trudenboy/ma-provider-yandex-disk/actions/workflows/test.yml/badge.svg)](https://github.com/trudenboy/ma-provider-yandex-disk/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/trudenboy/ma-provider-yandex-disk?display_name=tag)](https://github.com/trudenboy/ma-provider-yandex-disk/releases/latest)
[![License](https://img.shields.io/github/license/trudenboy/ma-provider-yandex-disk)](https://github.com/trudenboy/ma-provider-yandex-disk/blob/dev/LICENSE)
[![Music Assistant](https://img.shields.io/badge/Music%20Assistant-provider-9070B8?logo=python&logoColor=white)](https://www.music-assistant.io/)
[![Stars](https://img.shields.io/github/stars/trudenboy/ma-provider-yandex-disk?style=flat&logo=github)](https://github.com/trudenboy/ma-provider-yandex-disk/stargazers)


<div class="topic-pills"> <code>music-assistant</code> <code>home-assistant</code> <code>python</code> <code>yandex-disk</code> <code>yandex</code>
</div>



Music Assistant supports [Yandex Disk](https://360.yandex.com/disk/) — a cloud file storage: the provider streams and syncs your personal collection of music, audiobooks and podcasts stored on the Disk.
Created and maintained by [TrudenBoy](https://github.com/TrudenBoy).



**Related providers:** [Yandex Music](https://github.com/trudenboy/ma-provider-yandex-music)



## Features


| Feature | Support |
|:--------|:-------:|
| [Browse](features/browse/) | ✅ |
| [Library sync](features/browse/) | ✅ |
| [Streaming with seek](features/streaming/) | ✅ |
| Max quality | Source quality (files as-is) |
| [Sign-in method](features/auth/) | Your own Yandex OAuth app (confirmation code, cloud_api:disk.read, auto-refresh) |



## Configuration


See the [Configuration](configuration/) page for setup instructions.

## Known issues

Full list on the [Known Issues](known-issues/) page.
