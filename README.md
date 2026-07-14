# Yandex Disk Provider for Music Assistant

Стриминг и синхронизация вашей личной музыки, хранящейся на **Яндекс Диске**, в Music Assistant.

Provider that streams and syncs your personal music files stored on **Yandex Disk** into Music Assistant. Built on Music Assistant's shared `CloudFileSystemProvider` (the same base as the built-in Google Drive provider) and the fleet's shared Yandex login library.

## Возможности / Features

- Просмотр каталога (Browse) и синхронизация библиотеки: треки, альбомы, исполнители, плейлисты.
- Стриминг с перемоткой (HTTP Range / seek).
- Авторизация по OAuth-токену Яндекс Диска (implicit flow, `cloud_api:disk.read`) — работает на бесплатных аккаунтах.
- Настраиваемая корневая папка (например, `disk:/Music`).

## Установка / Installation

See the [documentation site](https://trudenboy.github.io/ma-provider-yandex-disk/) for setup and configuration.
