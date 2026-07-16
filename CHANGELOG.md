# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- refactor(config): drop the hardcoded `ConfigEntry` label/description/action_label duplicates from `get_config_entries` — the texts already live in `provider/strings.json`, which is now the single source (upstream `check_config_entries` compliance).
- fix(tests): `_FakeResp.__aenter__` returns `Self` (PYI034), per the upstream dev ruff rules.
- style: ruff 0.15 safe autofixes matching the upstream dev lint rules.

## [0.1.0b1]

### Added
- Initial Yandex Disk filesystem provider: browse and stream audio files from a configured Yandex Disk folder, library sync (tracks/albums/artists/playlists), seek support, and read-only OAuth authentication with automatic token refresh (`cloud_api:disk.read`), mirroring the Google Drive provider. Uses the user's own Yandex OAuth application and Yandex's confirmation-code flow (paste the code Yandex shows — no redirect URI to register).
