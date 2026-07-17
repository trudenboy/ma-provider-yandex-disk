# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-17

### Changed

- Expanded the Russian and English user documentation with OAuth setup, feature guides and known issues.
- Centralized provider configuration text in `strings.json` for upstream compatibility.

### Fixed

- Fixed reauthorization with a stored OAuth client secret by decrypting it before token exchange.
- Included the verification-code redirect in authorization requests so the confirmation-code flow matches the token exchange.

## [0.1.0b1]

### Added
- Initial Yandex Disk filesystem provider: browse and stream audio files from a configured Yandex Disk folder, library sync (tracks/albums/artists/playlists), seek support, and read-only OAuth authentication with automatic token refresh (`cloud_api:disk.read`), mirroring the Google Drive provider. Uses the user's own Yandex OAuth application and Yandex's confirmation-code flow (paste the code Yandex shows — no redirect URI to register).
