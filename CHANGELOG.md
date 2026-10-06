# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2026-10-06

### Removed

- Dropped the fallback that read the scan folder from the pre-1.0.0 `root_path`
  setting. Music Assistant no longer passes that value to the provider, so the
  fallback never took effect; instances created before 1.0.0 need to be set up
  again.

## [1.0.5] - 2026-10-05

### Fixed

- Files that Yandex Disk reports without an MD5 hash are rescanned after being
  replaced, instead of always being treated as unchanged.
- Long streams such as audiobooks are no longer cut off after five minutes.
- Rejected OAuth application credentials now ask for reauthorization instead of
  leaving the provider retrying indefinitely, and a malformed OAuth error
  response is reported as a provider error instead of crashing.
- Setup ends after 15 minutes even while an activation code is still valid, and
  token polling respects Yandex's interval from the first request.
- The provider's options page shows the library sync options again; they were
  defined where the current Music Assistant server no longer looks for them.
- Simultaneous requests after the access token expires share one token refresh,
  so a rotated refresh token can no longer be overwritten by a parallel refresh.

## [1.0.4] - 2026-08-28

### Fixed

- Return the metadata token required by Music Assistant's cloud filesystem item contract.

## [1.0.3] - 2026-08-12

### Changed

- Removed the unused `ya-passport-auth` package dependency; OAuth Device Flow
  continues to use Music Assistant's shared HTTP session.
- Linked the provider manifest to the official Yandex Disk documentation and
  added setup-to-runtime lifecycle regression coverage.

## [1.0.2] - 2026-08-11

### Changed

- Updated the `ya-passport-auth` dependency to 1.8.0.
- Synchronized the reusable repository workflow wrappers.

## [1.0.1] - 2026-08-05

### Fixed

- Made provider tests compatible with Music Assistant's upstream import-path
  rewrite and removed an upstream-unknown pytest marker.

## [1.0.0] - 2026-08-05

### Changed

- Replaced the legacy configuration action with Music Assistant's guided
  `SetupSession` flow. The provider now displays the Yandex verification URL and
  device code, polls for confirmation, refreshes expired codes automatically and
  completes setup without a manual `auth_code` or separate authentication status.
- Moved OAuth credentials, refresh token, content type and scan root into
  encrypted provider `setup_data`, with legacy config-value read-through for
  existing installations.
- Implemented the Yandex OAuth Device Flow and token refresh locally with the
  shared Music Assistant HTTP session, removing the unused `ya-passport-auth`
  dependency from this provider.
- Renamed the scan-root setup key to the cloud-provider standard `folder_id`;
  `root` selects the complete Yandex Disk and paths such as `disk:/Music` select
  a subfolder.
- Provider configuration now contains only runtime library-sync options, and the
  manifest links to Music Assistant's filesystem-provider documentation.

## [0.2.0] - 2026-07-29

### Added

- Official Yandex OAuth Device Flow through the shared `ya-passport-auth`
  Music Assistant integration, including the hosted confirmation page and a
  visible connected/not-connected status.

### Changed

- Replaced the placeholder provider artwork with the official Yandex Disk icon
  and moved the provider stage to `alpha` while the new authentication flow is
  validated upstream.
- Removed the manual `auth_code` field and authorization-code exchange.
- Token refresh now uses the provider-neutral `refresh_oauth_tokens` helper;
  OAuth application creation remains an explicit user step and is not part of
  the production flow.
- Rotated refresh tokens are persisted immediately in encrypted provider
  configuration, so they survive a Music Assistant restart.

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
