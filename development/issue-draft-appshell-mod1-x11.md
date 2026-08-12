# Issue draft — `test_bare_b_does_not_toggle_the_sidebar` asserts a Windows-only modifier premise

**Not yet filed.** The WSL box that measured this has no `gh`, no
`GH_TOKEN`/`GITHUB_TOKEN`, and no github.com credential, so the issue has to be
opened from the Windows box. This draft lives in the repo rather than in a
session, because this project has already lost one handoff artifact and one whole
patch to a scratch directory.

Found while answering the #447 fork (`development/report-447-linux-focus.md`).
**It is not #447** — it is window-manager independent and reproduces with a real
compositor.

Body is written one paragraph per line, per the no-hard-wrap rule.

---

## Suggested title

```
test_bare_b_does_not_toggle_the_sidebar asserts a Windows-only modifier premise and fails on X11
```

## Suggested labels / milestone

`test-infra`. **No milestone** — assigning one unasked is against the standing rule; it looks like patch-line material but that is the maintainer's call.

## Body

`tests/widgets/public/test_appshell_shortcuts.py::test_bare_b_does_not_toggle_the_sidebar` fails deterministically on Linux/X11 — 5 runs out of 5 standalone, and in every arm of the #447 investigation including WSLg with a real compositor and Xvfb with `xfwm4`. It is **not** the missing-window-manager problem that #447 turned out to be; a window manager does not fix it.

```
assert expanded._field.text == "b"
E  AssertionError: assert '' == 'b'
```

**The test file already documents the cause on its own line 20.** The test synthesizes `state=8` to stand in for "NumLock is on":

```python
_MOD1 = 8   # Tk's Mod1 bit — set by NumLock on Windows, by Alt on X11.
expanded._entry_widget.event_generate("<KeyPress-b>", state=_MOD1)
assert expanded._field.text == "b"
```

Bit 3 is `Mod1`, and what `Mod1` is bound to is a property of the X server's modifier map, not of Tk. On Windows Tk reports NumLock there, and NumLock does not suppress typing — which is why the test was written this way and why it is green on Windows. On X11 `Mod1` is **Alt**, and an Entry correctly refuses to insert a character while Alt is held, because that is the Alt+b accelerator rather than text input.

So **an empty field on X11 is correct toolkit behavior**, and the assertion encodes a Windows-only premise. Measured with a control by `development/probe_447b_mod1_alt_on_x11.py`, identical under WSLg and under Xvfb + `xfwm4` (Ubuntu 22.04.5, Python 3.13.11, Tk 8.6.12):

```
modifier map: mod1  Alt_L, Alt_R, Meta_L | mod2  Num_Lock

state=0   -> field='b'    plain b (CONTROL)
state=8   -> field=''     Mod1: NumLock on Windows, Alt on X11 — what the test sends
state=16  -> field='b'    Mod2: what X11 actually uses for NumLock
```

The X server names it outright: `mod1` is Alt, `mod2` is `Num_Lock`. The `state=0` control arm types, so the probe is demonstrably capable of observing an insert and the non-insert under `state=8` is the modifier rather than a dead harness.

**`AppShell` is not implicated.** The test's first assertion, `sidebar_mode == "expanded"`, passes on every platform and every arm — and that is the half actually guarding the #403/#404 regression this test exists for. Only the typing half is unportable.

Suggested fix: express the NumLock premise per platform — `Mod2` (16) on X11, `Mod1` (8) on Windows — or gate the typing assertion to Windows and keep the sidebar assertion everywhere. Either keeps the regression guard intact on all platforms.

This is the same class as `test_field_hidpi_padding::{test_field_padding_tracks_dpi,test_textarea_padding_tracks_dpi}`, which also fail on Tk 8.6.12 and pass in CI: tests that are correct on Windows and unportable off it. Worth sweeping the suite for other hardcoded modifier bits and `int()`-on-`cget` reads once CI actually runs Linux (#380 / PR #451), because until now nothing ran the suite on X11 at all.

## Command to file it, from a box with `gh`

```bash
gh issue create \
  --repo israel-dryer/bootstack \
  --title "test_bare_b_does_not_toggle_the_sidebar asserts a Windows-only modifier premise and fails on X11" \
  --label test-infra \
  --body-file development/issue-draft-appshell-mod1-x11.md
```

⚠ `--body-file` would post this whole draft, including the header above. Paste the **Body** section only, or split it into its own file first.
