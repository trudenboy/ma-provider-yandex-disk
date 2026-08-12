# Upstream Review Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare the Yandex Disk provider and its official documentation for another review of `music-assistant/server#4828`, with reproducible lifecycle and manual verification.

**Architecture:** Keep the standalone provider repository as the only source of provider code and tests, and add the user documentation independently through the official docs fork. Preserve `VERSION` because current upstream providers use it; propagate provider changes to the existing server PR only through the release/sync pipeline after maintainer-approved merge.

**Tech Stack:** Python 3.14, pytest/pytest-asyncio, Music Assistant `SetupSession`, `yadisk`, uv, Ruff, mypy, pre-commit, Docker Compose, Astro/Starlight, npm.

## Global Constraints

- Do not push, patch, comment on, resolve threads in, or mark ready `music-assistant/server#4828` directly.
- Keep `VERSION` unchanged at `1.0.2`; the maintainer owns the later release bump.
- Keep `yadisk==3.4.1` as the provider's only runtime dependency.
- Never print, commit, fixture, or include OAuth credentials or tokens in PR text.
- Provider work targets `dev`; official documentation work targets `beta`.
- Use Sphinx-style docstrings and keep private methods below public methods.
- Replies to the human upstream reviewer remain human-authored; provide evidence and a proposed factual outline only.

---

### Task 1: Add setup-to-runtime lifecycle regression coverage

**Files:**
- Modify: `tests/test_setup_flow.py`

**Interfaces:**
- Consumes: `provider.setup_flow.run_setup(session: SetupSession)`, `provider.setup(mass, manifest, config)`, `YandexDiskFileSystemProvider.handle_async_init()`.
- Produces: `test_setup_data_initializes_provider_and_registers_stream_route`, covering the real flow-to-provider boundary while mocking only OAuth, Yandex Disk I/O, and MA service objects.

- [ ] **Step 1: Extend the setup form driver with an explicit folder argument**

Change the helper signature and submitted value:

```python
async def _submit_user_form(
    session: SetupSession,
    secret: str | None = None,
    folder_id: str = "root",
) -> None:
    """Wait for and submit the common cloud setup form."""
    await _wait_for(lambda: session.current_step and session.current_step.type == FlowStepType.FORM)
    session.handle_submit(
        {
            "content_type": "music",
            CONF_CLIENT_ID: "client-id",
            CONF_CLIENT_SECRET: "client-secret" if secret is None else secret,
            CONF_FOLDER_ID: folder_id,
        }
    )
```

- [ ] **Step 2: Add the lifecycle test using real MA models and provider setup**

Add imports for `ProviderConfig`, `ProviderManifest`, `ProviderStage`, `ProviderType`, `provider.setup`, and the provider module used to patch `YandexDiskApi`. Build a real `ProviderConfig` from the values received by the `SetupSession` finish handler:

```python
async def test_setup_data_initializes_provider_and_registers_stream_route() -> None:
    """Setup output initializes the provider and registers its stream route."""
    provider_instance: Any = None
    api = mock.Mock()
    api.validate = mock.AsyncMock()
    api.exists_dir = mock.AsyncMock(return_value=True)
    api.close = mock.AsyncMock()

    mass = mock.Mock()
    mass.http_session = object()
    mass.cache = mock.Mock()
    mass.streams.base_url = "http://ma.local:8095"
    unregister = mock.Mock()
    mass.streams.register_dynamic_route.return_value = unregister
    mass.config.decrypt_string.side_effect = lambda value: value

    manifest = ProviderManifest(
        type=ProviderType.MUSIC,
        domain="filesystem_yandex_disk",
        name="Yandex Disk",
        description="Yandex Disk test provider",
        codeowners=["@TrudenBoy"],
        stage=ProviderStage.BETA,
        requirements=["yadisk==3.4.1"],
        multi_instance=True,
    )

    async def finish(_session: SetupSession, values: dict[str, Any]) -> dict[str, str]:
        nonlocal provider_instance
        config = ProviderConfig(
            values={},
            type=ProviderType.MUSIC,
            domain=manifest.domain,
            instance_id="filesystem_yandex_disk--lifecycle",
            setup_data=dict(values),
        )
        mass.config.get.side_effect = lambda path: (
            config.setup_data if path.endswith("/setup_data") else {}
        )
        provider_instance = await setup_provider(mass, manifest, config)
        await provider_instance.handle_async_init()
        return {"instance_id": config.instance_id}

    session = SetupSession(
        mass,
        "flow-lifecycle",
        SetupFlowContext(
            kind="setup",
            reason="user",
            domain=manifest.domain,
            setup_data={},
        ),
        finish,
    )
    with (
        mock.patch.object(setup_flow, "request_device_code", mock.AsyncMock(return_value=_grant())),
        mock.patch.object(
            setup_flow,
            "poll_device_token",
            mock.AsyncMock(return_value=OAuthTokens("access", "refresh", 3600)),
        ),
        mock.patch.object(provider_module, "YandexDiskApi", return_value=api),
    ):
        task = asyncio.create_task(setup_flow.run_setup(session))
        await _submit_user_form(session, folder_id="disk:/Music")
        await _wait_for(lambda: session.finished)
        await task

    assert provider_instance.root_folder_id == "disk:/Music"
    api.validate.assert_awaited_once_with()
    api.exists_dir.assert_awaited_once_with("disk:/Music")
    mass.streams.register_dynamic_route.assert_called_once()
    assert mass.streams.register_dynamic_route.call_args.args[0] == (
        "/filesystem_yandex_disk--lifecycle_stream"
    )
```

- [ ] **Step 3: Prove the new assertion detects the original lifecycle regression**

Temporarily replace `await self._post_init()` in `handle_async_init()` with `return`, run:

```bash
/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin/pytest \
  tests/test_setup_flow.py::test_setup_data_initializes_provider_and_registers_stream_route -q
```

Expected: FAIL because `register_dynamic_route` was not called. Restore the original line with a reverse `apply_patch`, confirm `git diff provider/provider.py` is empty, and rerun the same command. Expected: PASS.

- [ ] **Step 4: Run the setup-flow module tests**

Run:

```bash
/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin/pytest tests/test_setup_flow.py -q
```

Expected: all setup-flow tests pass.

- [ ] **Step 5: Commit lifecycle coverage**

```bash
git add tests/test_setup_flow.py
git commit -m "test: cover setup-to-runtime lifecycle"
```

---

### Task 2: Remove stale dependency metadata and link official documentation

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `provider/manifest.json`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: direct OAuth implementation in `provider/auth.py` and the official docs route created by Task 4.
- Produces: a package whose direct runtime dependencies match `manifest.json`, plus an upstream-facing documentation link.

- [ ] **Step 1: Remove the unused direct dependency**

Run:

```bash
uv remove ya-passport-auth
```

Verify `pyproject.toml` lists only `yadisk==3.4.1` under `[project].dependencies`, and verify `uv.lock` no longer includes `ya-passport-auth` unless it remains solely as a transitive dependency. Confirm source code has no import:

```bash
rg -n "ya[_-]passport|ya-passport" provider pyproject.toml uv.lock
```

- [ ] **Step 2: Pin the official documentation route in the manifest**

Change:

```json
"documentation": "https://music-assistant.io/music-providers/yandex-disk/"
```

- [ ] **Step 3: Add the next changelog block without bumping `VERSION`**

Insert above `1.0.2`:

```markdown
## [1.0.3] - 2026-08-12

### Changed

- Removed the unused `ya-passport-auth` package dependency; OAuth Device Flow
  continues to use Music Assistant's shared HTTP session.
- Linked the provider manifest to the official Yandex Disk documentation and
  added setup-to-runtime lifecycle regression coverage.
```

- [ ] **Step 4: Validate dependency and manifest consistency**

Run:

```bash
/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin/python - <<'PY'
import json
import tomllib

with open("pyproject.toml", "rb") as file:
    project = tomllib.load(file)["project"]
manifest = json.load(open("provider/manifest.json"))
assert project["dependencies"] == ["yadisk==3.4.1"]
assert manifest["requirements"] == ["yadisk==3.4.1"]
assert manifest["documentation"].endswith("/music-providers/yandex-disk/")
PY
```

- [ ] **Step 5: Commit metadata cleanup**

```bash
git add pyproject.toml uv.lock provider/manifest.json CHANGELOG.md
git commit -m "chore: remove stale OAuth dependency"
```

---

### Task 3: Verify the provider automatically and interactively

**Files:**
- No committed files.
- Runtime-only data: `.ma-data/` inside the provider worktree.

**Interfaces:**
- Consumes: provider branch after Tasks 1-2.
- Produces: command output and a manual verification record for the draft PR description.

- [ ] **Step 1: Run focused and full automated gates**

```bash
/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin/pytest -q
/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin/ruff check provider tests
/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin/ruff format --check provider tests
/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin/mypy provider tests
PATH="/mnt/data/Projects/mass/ma-provider-yandex-disk/.venv/bin:$PATH" \
  pre-commit run --all-files
```

Expected: every command exits zero with no new warnings.

- [ ] **Step 2: Start a current Music Assistant nightly with the worktree provider**

```bash
docker compose -f docker-compose.dev.yml pull
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml logs --tail=120 ma
```

Wait until the log reports the server listening on `http://localhost:8095`.

- [ ] **Step 3: Complete guided setup with the maintainer**

Ask the maintainer to open `http://localhost:8095`, add Yandex Disk, enter their own OAuth application Client ID and secret, choose `disk:/Music` or a real folder, and approve the displayed Device Flow code. Confirm from redacted logs that the instance initializes without `LoginFailed`, `SetupFailedError`, or credential values.

- [ ] **Step 4: Verify scan, playback, and seeking**

Trigger a provider sync, confirm real files appear, start one audio item, and seek forward. Inspect only provider/error log lines:

```bash
docker compose -f docker-compose.dev.yml logs ma | \
  rg -i "filesystem_yandex_disk|yandex disk|error|exception|traceback|failed"
```

Expected: successful sync/playback activity and no provider traceback or leaked secret.

- [ ] **Step 5: Verify restart, refresh, and reconfigure**

Restart the service, confirm the provider returns without reauthorization, then reconfigure it while leaving Client Secret blank and complete Device Flow again:

```bash
docker compose -f docker-compose.dev.yml restart ma
docker compose -f docker-compose.dev.yml logs --tail=180 ma
```

Expected: stored setup data is reused, playback still works, and token refresh produces no authentication error. Stop the environment after verification:

```bash
docker compose -f docker-compose.dev.yml down
```

---

### Task 4: Add the official Yandex Disk documentation page

**Files:**
- Create in docs worktree: `src/content/docs/music-providers/yandex-disk.md`

**Interfaces:**
- Consumes: current `upstream/beta` Astro content collection and the provider behavior verified in Task 3.
- Produces: official route `/music-providers/yandex-disk/`; the Music Sources sidebar discovers it automatically.

- [ ] **Step 1: Create an isolated docs worktree from current upstream beta**

In `/mnt/data/Projects/mass/music-assistant.io`, add `.worktrees/` to `.git/info/exclude` if needed, then run:

```bash
git fetch upstream beta
git worktree add .worktrees/yandex-disk -b docs/yandex-disk upstream/beta
```

- [ ] **Step 2: Verify the docs baseline**

```bash
npm ci
npm run build
```

Expected: Astro production build succeeds before the new page is added.

- [ ] **Step 3: Add the user-focused page**

Create `src/content/docs/music-providers/yandex-disk.md` with this structure and content:

```markdown
---
title: "Yandex Disk"
description: Play personal music, audiobooks, and podcasts stored on Yandex Disk
---

# Yandex Disk

Music Assistant can browse, sync, and play audio files stored in your personal
Yandex Disk. Contributed and maintained by
[TrudenBoy](https://github.com/TrudenBoy).

> [!CAUTION]
> This is an unofficial integration and is not affiliated with or endorsed by
> Yandex.

## Features

- Supports music, audiobooks, podcasts, playlists, artwork, and lyrics stored as files
- Streams files without downloading the complete library to Music Assistant
- Supports seeking in tracks and long audiobook files
- Can scan the complete disk or one selected folder
- Uses read-only Yandex Disk access and supports multiple provider instances

## Configuration

### Create a Yandex OAuth application

1. Open [Yandex OAuth](https://oauth.yandex.ru/) and create an application.
2. Under **Data access**, add the **`cloud_api:disk.read`** permission.
3. Copy the application's **Client ID** and **Client Secret**.

### Add Yandex Disk to Music Assistant

1. In Music Assistant, open **Settings → Providers → Add Provider → Yandex Disk**.
2. Enter the Client ID and Client Secret from your OAuth application.
3. Select whether this instance contains music, audiobooks, or podcasts.
4. Keep **Root folder to scan** set to `root` for the complete disk, or enter a
   path such as `disk:/Music`.
5. Continue, open the displayed verification URL, enter the short code, and
   approve read-only access. Music Assistant completes setup automatically.

Create a separate provider instance for each content type you want to use.

### Settings

After setup, the provider settings control which items are imported into the
Music Assistant library, how missing album artists are handled, whether album
playlists are ignored, and whether track genres are propagated to albums and
artists.

## Known Issues / Notes

- The provider is read-only and cannot upload, rename, or delete Yandex Disk files.
- Access tokens refresh automatically. Reauthorization is required if access is
  revoked or the OAuth application is deleted.
- Changes made on Yandex Disk are discovered during the next library sync.
- Correct embedded tags and a consistent artist/album folder structure produce
  the best library matches.
```

- [ ] **Step 4: Build and inspect the generated route**

```bash
npm run build
test -f dist/music-providers/yandex-disk/index.html
```

Expected: build succeeds and the generated HTML contains the headings `Yandex Disk`, `Configuration`, and `Known Issues / Notes`.

- [ ] **Step 5: Commit, push, and open the official docs draft PR**

```bash
git add src/content/docs/music-providers/yandex-disk.md
git commit -m "docs(music-providers): add Yandex Disk source"
git push -u origin docs/yandex-disk
gh pr create --repo music-assistant/music-assistant.io \
  --head trudenboy:docs/yandex-disk --base beta --draft \
  --title "docs(music-providers): add Yandex Disk source" \
  --body-file /tmp/yandex-disk-docs-pr.md
```

The body file must summarize the user-facing page, link `music-assistant/server#4828`, and list `npm run build` plus the generated-route check as the test plan.

---

### Task 5: Publish the provider draft PR and prepare upstream handoff

**Files:**
- Modify: `docs/superpowers/plans/2026-08-12-upstream-review-followup.md` only to mark executed checkboxes if useful.

**Interfaces:**
- Consumes: verified provider commits, official docs draft PR URL, current PR #4828 state.
- Produces: provider draft PR targeting `dev` and a factual maintainer handoff for the existing upstream review.

- [ ] **Step 1: Update the provider manifest link if the docs route changed during review**

Confirm the docs draft PR still generates `/music-providers/yandex-disk/`. If it does, make no further change. If upstream requires a different slug, change only `provider/manifest.json`, rerun manifest consistency validation, and commit with `docs: align official Yandex Disk link`.

- [ ] **Step 2: Review the complete provider diff**

```bash
git diff dev...HEAD --stat
git diff --check dev...HEAD
git diff dev...HEAD -- provider tests pyproject.toml uv.lock CHANGELOG.md
git status -sb
```

Confirm no secret, `.ma-data`, generated cache, or unrelated file is tracked.

- [ ] **Step 3: Push and open the provider draft PR**

```bash
git push -u origin fix/upstream-review-followup
gh pr create --repo trudenboy/ma-provider-yandex-disk \
  --head fix/upstream-review-followup --base dev --draft \
  --title "test: address upstream Yandex Disk review" \
  --body-file /tmp/yandex-disk-provider-pr.md
```

The PR body must state that `VERSION` is intentionally unchanged, link the docs draft PR and upstream PR #4828, summarize automated and manual verification truthfully, and leave unchecked any manual item not completed.

- [ ] **Step 4: Re-read the upstream review state without writing to it**

Use the thread-aware comment script and `gh pr view 4828 --repo music-assistant/server` to confirm no new unresolved thread appeared during implementation. Record `DRAFT`, `BEHIND`, review decision, and check state in the handoff.

- [ ] **Step 5: Prepare the post-merge sequence**

Document these maintainer-controlled steps without executing them:

1. Review and merge the provider PR into `dev`.
2. Apply the maintainer-owned `VERSION` bump to `1.0.3` and release it.
3. Let the standard stable sync refresh `upstream/filesystem_yandex_disk` from current upstream `dev`.
4. Verify server PR #4828 CI, then have the human owner post the factual `VERSION` evidence and mark the PR Ready for review.

Do not merge either new draft PR, bump `VERSION`, dispatch the release workflow, or write to PR #4828 without a later explicit maintainer instruction.
