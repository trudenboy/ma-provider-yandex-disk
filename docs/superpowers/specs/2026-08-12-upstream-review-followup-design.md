# Upstream Review Follow-up Design

## Goal

Prepare the Yandex Disk provider for another review of
`music-assistant/server#4828` by removing stale dependency metadata, adding a
setup-to-runtime lifecycle regression test, publishing user-focused official
documentation, and verifying the provider against a current Music Assistant
development build.

## Repository Boundaries

The provider repository remains the source of truth for provider code and
tests. The documentation page belongs in `music-assistant/music-assistant.io`
and is developed through the `trudenboy/music-assistant.io` fork. No provider
code is copied manually into `trudenboy/ma-server` or
`music-assistant/server`; the existing release and upstream-sync workflows
remain the only forward-sync path.

The provider `VERSION` file remains part of the upstream payload. Current
`music-assistant/server@dev` already contains provider-local `VERSION` files
for multiple externally maintained providers, and `ma-provider-tools` uses the
file to report the exact provider version shipped by each Music Assistant
release. The older request to remove it is therefore answered with current
repository evidence rather than a code change.

## Provider Changes

The provider draft PR targets `dev` from `fix/upstream-review-followup` and
contains four focused changes:

1. Remove the unused `ya-passport-auth[ma]` direct dependency from
   `pyproject.toml` and regenerate `uv.lock`. The provider performs OAuth
   Device Flow directly with the shared Music Assistant `aiohttp` session, and
   its upstream runtime manifest already requires only `yadisk==3.4.1`.
2. Change the manifest documentation URL to the official Yandex Disk page at
   `https://music-assistant.io/music-providers/yandex-disk/`.
3. Add a lifecycle regression test that drives a real `SetupSession` through
   the Yandex Device Flow boundary with deterministic OAuth responses, uses
   the resulting setup data to construct the real provider class, calls
   `handle_async_init()`, and verifies API validation plus stream-route
   registration.
4. Add a changelog entry describing the dependency cleanup, official
   documentation link, and lifecycle coverage without changing `VERSION`.

The lifecycle test mocks only external boundaries: Yandex OAuth, Yandex Disk
network access, and Music Assistant services that are outside the provider.
It exercises existing production behavior without requiring a production-code
change; the new assertion is validated with a deliberate mutation check before
the final passing run.

## Official Documentation

The documentation draft PR targets `beta` in
`music-assistant/music-assistant.io`. It adds
`src/content/docs/music-providers/yandex-disk.md`. The current Music Sources
sidebar is generated automatically from that directory, so no sidebar
configuration change is required.

Following the reviewed final form of documentation PR #626, the page is
user-focused. It explains supported media, read-only behavior, creating a
personal Yandex OAuth application, selecting `cloud_api:disk.read`, Device
Flow confirmation, the `root` and `disk:/Music` folder formats, configurable
sync behavior, seeking, token refresh, and practical limitations. It omits
internal protocol details and links to the standalone personal documentation
site.

## Verification

Automated provider verification consists of the new red-green lifecycle test,
the full pytest suite, Ruff check and format verification, mypy, and the full
pre-commit gate. Documentation verification consists of dependency install
when necessary and a production Astro build.

Manual verification uses `docker-compose.dev.yml` to run the local provider on
a current Music Assistant nightly image. The maintainer completes the Yandex
Device Flow when the user code appears. The verification records successful
provider creation, root-folder scan, audio playback, Range-based seek, Music
Assistant restart, access-token refresh after restart, and reconfiguration
with an empty Client Secret.

Secrets and token values are never printed, committed, copied into test
fixtures, or included in PR text.

## Publication and Upstream Update

The implementation publishes two new draft PRs:

1. `trudenboy/ma-provider-yandex-disk`, targeting `dev`;
2. `music-assistant/music-assistant.io`, targeting `beta`, from the matching
   branch in `trudenboy/music-assistant.io`.

The existing `music-assistant/server#4828` remains draft. It is not patched or
commented on directly. After the provider PR is reviewed, merged, and released
with explicit maintainer approval, the standard sync workflow updates its
fork branch from current upstream `dev` and refreshes PR #4828. Until that
merge-and-release checkpoint, the draft provider PR is the reviewable source
for the pending server changes.
