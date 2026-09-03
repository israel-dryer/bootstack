# Releasing bootstack

The complete procedure, start to finish. Follow it in order; every step says what to check before moving on.

**The shape of a release:** promote the CHANGELOG in its own commit → `bumpversion` commits the version and creates the tag → push `main` and the tag → `release.yml` builds, publishes to PyPI and creates the GitHub Release → `docs.yml` deploys the site → verify → close out.

---

## Before you start

| Check | Command | Wanted |
|---|---|---|
| On `main`, up to date | `git status` / `git pull` | clean tree, nothing to pull |
| **Working tree is CLEAN** | `git status --porcelain` | empty — `bumpversion` refuses a dirty tree (`allow_dirty = false`) |
| Suite is green | `py -3.12 tests/run_gui.py` | exit 0 |
| `bumpversion` is installed | `py -3.12 -m bumpversion --version` | a version string |

⚠ **`bumpversion` DISAPPEARS. Check it every single time** — it has been recorded installed twice and gone twice. Install with `py -3.12 -m pip install bump-my-version`. **The import name is `bumpversion`, not `bump_my_version`** — probing the wrong one reports "no module" on an interpreter that has it.

⚠ **Use `py -3.12 -m bumpversion`, never the `.venv` shim** — the checked-in `.venv` is stale and dies with *"Access is denied"*.

⚠ **Never pipe a build or test command to `tail`, `head` or `Select-String`** — you capture the pipe's exit code, not the command's, and a real failure reads as success. Redirect to a file, read `$LASTEXITCODE` on the next statement, then grep the file.

### Decide the version first

| The release contains | Version | Verb |
|---|---|---|
| bug fixes only, no new public surface | patch — `0.4.1` → `0.4.2` | `bump patch` |
| **any** new public API, even if nothing breaks | minor — `0.4.1` → `0.5.0` | `bump minor` |
| a behavior change that raises where it used to accept | minor | `bump minor` |

⚠ **The verb decides the number, and you cannot move a tag a release has already run on.** `bump patch` on a release that should have been minor ships the wrong version permanently.

⚠ **The rule is one-directional.** An addition *requires* a minor; a minor does not require additions and may carry as many plain fixes as you like. So when a minor is being cut anyway, ask what else is ready rather than parking fixes out of habit.

---

## Step 1 — Settle the CHANGELOG

Fixes land during development writing under `## [Unreleased]`. Before promoting, **read the whole section end to end as its audience reads it** — someone asking *"was I affected?"*.

- **Every entry must be REACHABLE from public API.** An entry for a defect no user can hit is a false positive. CI, test-harness and internal-only fixes ship with no entry — say so in the commit message instead, since that is where the omitted work stays documented.
- **Check `### Added` against the version you chose.** An `### Added` section in a patch release means you picked the wrong verb.
- **A claim about PRIOR behavior must be checked against the OLD code**, not against the fix: `git show <last-tag>:<file>`. An entry once said a misspelled value *"previously turned both menus off silently"* when it did the opposite, because the sentence was written from the fix's point of view.
- **Entries under the right heading.** `### Changed` is for upgrade risk. Three plain bug fixes once sat under `Changed` and handed a reader three false alarms before the one that mattered.
- **ONE PARAGRAPH PER LINE — do not hard-wrap.** The section is lifted verbatim into the GitHub Release body, which renders a soft line break as a visible one. Older sections are left wrapped; do not reformat shipped history.

## Step 2 — Promote the section, in its OWN commit

Rename the heading and add the link definition at the bottom of the file:

```
## [Unreleased]              →   ## [X.Y.Z] — Descriptive title
```

```
[X.Y.Z]: https://github.com/israel-dryer/bootstack/releases/tag/vX.Y.Z
```

⚠ **THE DESCRIPTIVE SUFFIX IS REQUIRED.** It becomes the GitHub Release *title*. A section promoted as bare `## [X.Y.Z]` ships a release titled bare `X.Y.Z`.

⚠ **This MUST be its own commit, BEFORE `bumpversion`.** `bumpversion` commits `pyproject.toml` alone — it will not sweep the rename in, and a release whose notes still say `## [Unreleased]` breaks `release.yml`'s section extraction.

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): promote [Unreleased] to X.Y.Z"
```

## Step 3 — Verify the extraction against the real file

Not a simulation — the file you are about to tag:

```bash
py -3.12 -c "import sys; sys.path.insert(0,'.github/scripts'); from release_notes import extract; t,b = extract('X.Y.Z', open('CHANGELOG.md',encoding='utf-8').read())[:2]; print('TITLE:', t); print(b)"
```

Confirm: the title is `X.Y.Z — Descriptive title`, the body starts at `### Fixed` (or `### Added`), and **no bottom link definitions leaked in**.

(The em dash prints as `?` or `�` on the Windows console's cp1252 — that is the terminal, not the title. What matters is that the suffix is there.)

## Step 4 — Bump and tag

```bash
py -3.12 -m bumpversion bump patch      # or: bump minor
```

This one command edits `pyproject.toml`, commits it as `Release X.Y.Z`, and creates the annotated tag `vX.Y.Z`. Confirm before pushing:

```bash
git log --oneline -3
git tag --sort=-creatordate | head -3
git show vX.Y.Z --stat
```

## Step 5 — Push the commit and the tag

```bash
git push origin main
git push origin vX.Y.Z
```

`release.yml` fires on the **tag** push only. Pushing `main` alone does nothing.

## Step 6 — Watch the workflows

```bash
gh run list --workflow=release.yml --limit 3
gh run watch <run-id>
```

Three jobs run in order: **build** (sdist + wheel) → **publish** (PyPI via OIDC trusted publishing) → **release** (GitHub Release with both artifacts attached).

Then `docs.yml` deploys the site.

⚠ **`docs.yml` is CHAINED to `release.yml` SUCCEEDING** — it triggers on `workflow_run` of "Release" `completed` and is gated on `conclusion == 'success'`. **Any release that does not go through a green `release.yml` run leaves the docs site stale, silently**: the run shows as `completed/skipped`, which reads like a deliberate no-op. Kick it by hand when that happens:

```bash
gh workflow run docs.yml --ref main
```

## Step 7 — Verify the published release

```bash
py -3.12 development/verify_release.py X.Y.Z
echo "EXIT=$?"
```

⚠ **Read the exit code WITHOUT a pipe** — it is the number of failed checks. A first control run was piped to `tail` and reported `EXIT=0` over three failures.

The script checks, independently and without trusting any summary endpoint: a real `pip download` from PyPI, the per-version PyPI endpoint, the fix inside the published wheel, `NOTICE` at `dist-info/licenses/`, `import bootstack` with `idlelib` blocked (with a control asserting the block works), provenance (that the test imported the wheel and not the editable tree), both assets on the GitHub Release, the chained `docs.yml` run, and the live site.

⚠⚠ **THE "fix is inside the published wheel" CHECK IS HARDCODED TO A PAST RELEASE.** It asserts `_uncheckable_message` appears in `bootstack/validation/validation_rules.py` — that was #467, in `0.4.0`. It will keep passing forever while proving nothing about the release you just cut. **Edit `check_wheel_contents` in `development/verify_release.py` to look for this release's fix before you trust that line**, or read it as a no-op.

⚠ **Do NOT re-prove the `idlelib` check with grep** — it gives a false positive. Seven `idlelib` mentions survive in the wheel and all are docstring attributions.

⚠ **The `/pypi/bootstack/json` summary endpoint is CDN-cached and has lagged behind a successful upload.** Never read a stale summary as a failed upload and re-publish. Use the per-version endpoint or a real download.

## Step 8 — Close out

1. **Close the release milestone** if it is a numbered one.
   ⚠ **A rolling line — `0.4.x — Patch line` — does NOT close when a patch ships.** Renaming or closing a turned-over line would relabel work that has already shipped. When it does turn over, create a NEW milestone; never rename.
2. **Check every shipped issue carries the right milestone**, closed ones included:
   `gh issue list --milestone "<title>" --state all`
   ⚠ Sweep a turning-over line with `--state all` — a 2026-08-27 turnover missed two issues because both were already closed.
3. **Comment on the shipped issues** if you want to.
   ⚠ **`gh issue close --comment "..."` SILENTLY DROPS THE COMMENT when the issue is already closed** — and a PR body containing `Closes #N` closes it at merge, which is the normal case. Use `gh issue comment N --body ...` and verify it landed with `gh issue view N --json comments`.
4. **Sweep `CLAUDE.md` the same day** — the released version, the START HERE section, the milestone table and the suite counts. Archive the shipped initiative into `docs/_dev/handoff-archive.md` **the day the release ships**; CLAUDE.md has been force-split twice because releases accreted there instead.

---

## Appendix A — Publishing BY HAND when Actions is down

Used for `0.2.2` during a major Actions outage; it worked cleanly and will be needed again.

⚠ **Under an outage the run state itself is unreliable** — `gh run cancel` once said "already completed" while `gh run view` said `queued`. **Check PyPI, not the run**, to decide whether anything was published.

```bash
# 1. Build from a PRISTINE checkout of the tag, never the working tree
#    (development/ carries dozens of untracked files).
git worktree add <scratch>/rel-X.Y.Z vX.Y.Z

# 2-3. Build and check
py -3.12 -m pip install --upgrade build twine
cd <scratch>/rel-X.Y.Z
py -3.12 -m build
py -3.12 -m twine check dist/*

# 4. Upload
py -3.12 -m twine upload --config-file D:/Development/bootstack/.pypirc --non-interactive dist/*

# 5. GitHub Release (title from the release_notes.py command in Step 3)
gh release create vX.Y.Z dist/* --title "<title>" --notes-file RELEASE_NOTES.md --generate-notes

# 6. A manual publish SKIPS THE DOCS DEPLOY, silently
gh workflow run docs.yml --ref main

# 7. Clean up
git worktree remove <path> --force
```

⚠ **`twine.exe` is NOT on PATH** — always `py -3.12 -m twine`.

⚠ **The token lives at `D:\Development\bootstack\.pypirc`** (repo root, **not** `~/.pypirc`, which does not exist), gitignored and untracked. Because it is not in the home directory, twine needs `--config-file` explicitly.

⚠ **`release.yml` publishes via OIDC trusted publishing, so there is NO token in CI.** The local `.pypirc` is the only credential path for a manual publish, and CI's path cannot be reproduced locally.

---

## Appendix B — What the automation actually does

**`.github/workflows/release.yml`** — triggers on `push` of a `v*` tag.

- **build** — Python 3.12, `python -m build`, uploads `dist/` as an artifact.
- **publish** — downloads `dist/`, publishes with `pypa/gh-action-pypi-publish` using OIDC (`id-token: write`). No stored token.
- **release** — runs `.github/scripts/release_notes.py <version> RELEASE_NOTES.md $GITHUB_OUTPUT`, then `softprops/action-gh-release` with the extracted title, that body, `generate_release_notes: true` (GitHub's "What's Changed" is appended below the curated notes) and `files: dist/*`. A tag containing `a`, `b` or `rc` is marked a prerelease automatically.

**`.github/scripts/release_notes.py`** — takes the title from the descriptive suffix after `## [X.Y.Z] —` and the body from the section **without** its heading, so the title is not repeated and `[X.Y.Z]` does not render as a self-link. A version with no CHANGELOG section falls back to a `vX.Y.Z` title and an empty body.

**`.github/workflows/docs.yml`** — `workflow_run` on "Release" `completed`, gated on `conclusion == 'success'`; also `workflow_dispatch`. The `workflow_run` trigger is deliberate rather than a `release`/tag trigger: it runs in the `main` context, so `deploy-pages` passes the `github-pages` environment's branch protection, which rejects a tag-ref deployment.

**`[tool.bumpversion]` in `pyproject.toml`** — `current_version`, `commit = true`, `tag = true`, `tag_name = "v{new_version}"`, `message = "Release {new_version}"`, `allow_dirty = false`. It rewrites the version in `pyproject.toml` only.

**There is no `development` branch.** Releases are cut from `main`.

---

## Appendix C — Known divergences

⚠ **`v0.3.1`, `v0.3.2` and `main` DIFFER BY DESIGN.** Each CHANGELOG was reworded *after* its tag and the GitHub Release body edited to match with `gh release edit --notes-file`. **THE TAGS WERE NOT MOVED.** Never move a tag a release has already run on — reword the file and edit the published body instead.

⚠ **Read the notes as their audience reads them BEFORE promoting**, not after. Verifying the *extraction* is not reviewing the *notes*, and this project has reworded two CHANGELOGs after tagging.
