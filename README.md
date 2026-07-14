# Yandex Disk Provider for Music Assistant


<!-- >>> ma-provider-tools sync (readme header) — DO NOT EDIT >>> -->
[![CI](https://github.com/trudenboy/ma-provider-yandex-disk/actions/workflows/test.yml/badge.svg)](https://github.com/trudenboy/ma-provider-yandex-disk/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/trudenboy/ma-provider-yandex-disk?display_name=tag)](https://github.com/trudenboy/ma-provider-yandex-disk/releases/latest)
[![License](https://img.shields.io/github/license/trudenboy/ma-provider-yandex-disk)](LICENSE)
[![Music Assistant](https://img.shields.io/badge/Music%20Assistant-9070B8?logo=python&logoColor=white)](https://www.music-assistant.io/)[![stable](https://img.shields.io/endpoint?url=https%3A%2F%2Ftrudenboy.github.io%2Fma-provider-tools%2Fbadges%2Ffilesystem_yandex_disk-stable.json)](https://github.com/music-assistant/server/releases/latest)[![beta](https://img.shields.io/endpoint?url=https%3A%2F%2Ftrudenboy.github.io%2Fma-provider-tools%2Fbadges%2Ffilesystem_yandex_disk-beta.json)](https://github.com/music-assistant/server/releases?q=prerelease)
[![Stars](https://img.shields.io/github/stars/trudenboy/ma-provider-yandex-disk?style=flat&logo=github)](https://github.com/trudenboy/ma-provider-yandex-disk/stargazers)

**📖 [Documentation / Документация](https://trudenboy.github.io/ma-provider-yandex-disk/)** · **🔄 [Changelog / Журнал](CHANGELOG.md)** · **🐛 [Issues / Проблемы](https://github.com/trudenboy/ma-provider-yandex-disk/issues)** · **💬 [Discussions / Обсуждения](https://github.com/trudenboy/ma-provider-yandex-disk/discussions)**

**Related providers:** [Yandex Music](https://github.com/trudenboy/ma-provider-yandex-music)
<!-- <<< ma-provider-tools sync (readme header) <<< -->

Стриминг и синхронизация вашей личной музыки, хранящейся на **Яндекс Диске**, в Music Assistant.

Provider that streams and syncs your personal music files stored on **Yandex Disk** into Music Assistant. Built on Music Assistant's shared `CloudFileSystemProvider` (the same base as the built-in Google Drive provider), authenticating with your own Yandex OAuth application (read-only Disk scope) — the same model the Google Drive provider uses.

## Возможности / Features

- Просмотр каталога (Browse) и синхронизация библиотеки: треки, альбомы, исполнители, плейлисты.
- Стриминг с перемоткой (HTTP Range / seek).
- Авторизация как в Google Drive: своё OAuth-приложение Яндекса (`cloud_api:disk.read`) + код подтверждения (redirect URI не нужен) и авто-refresh токена. Работает на бесплатных аккаунтах.
- Настраиваемая корневая папка (например, `disk:/Music`).

## Установка / Installation

See the [documentation site](https://trudenboy.github.io/ma-provider-yandex-disk/) for setup and configuration.
