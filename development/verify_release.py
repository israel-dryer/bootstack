"""Verify a published bootstack release. Nothing here trusts a summary endpoint.

    python development/verify_release.py 0.4.0

Every check is independent and reports PASS / FAIL / SKIP; the script never stops
at the first failure, because a box that cannot do one check can usually still do
the rest (the #430 lesson -- a probe must be runnable everywhere it informs).
Output is ASCII only: a check mark raises UnicodeEncodeError on the Windows box's
cp1252 console.

Exit code is the number of FAILs.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile

VERSION = sys.argv[1] if len(sys.argv) > 1 else None
RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok))
    tag = {True: "PASS", False: "FAIL", None: "SKIP"}[ok]
    print(f"  [{tag}] {name}" + (f"\n         {detail}" if detail else ""))


def run(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def fetch(url):
    """Return (body, error). urllib has no usable CA bundle on some boxes -- this
    macOS venv raises CERTIFICATE_VERIFY_FAILED for every https call while pip
    works fine, because pip carries its own certs. Fall back to curl, which is
    present on macOS and on Windows 10+, rather than reporting a network failure
    that is really a missing trust store."""
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.read().decode("utf-8"), ""
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception:
        pass
    if not shutil.which("curl"):
        return None, "urllib has no CA bundle here and curl is not installed"
    out = run("curl", "-fsS", "--max-time", "20", url)
    return (out.stdout, "") if out.returncode == 0 else (None, out.stderr.strip()[:100])


def http_status(url):
    """Return (status_code, error), by whichever route works."""
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        pass
    if not shutil.which("curl"):
        return None, "urllib has no CA bundle here and curl is not installed"
    out = run("curl", "-sS", "-o", os.devnull, "-w", "%{http_code}",
              "--max-time", "20", url)
    if out.returncode != 0:
        return None, out.stderr.strip()[:100]
    return int(out.stdout.strip() or 0), ""


def check_pypi_download(tmp):
    """A real download, not /pypi/bootstack/json -- that summary is CDN-cached
    and has lagged behind a successful upload, which reads as a failed one."""
    out = run(sys.executable, "-m", "pip", "download", "--no-deps", "--no-binary", ":none:",
              "-d", tmp, f"bootstack=={VERSION}")
    files = sorted(os.listdir(tmp)) if os.path.isdir(tmp) else []
    wheel = next((f for f in files if f.endswith(".whl")), None)
    record(f"PyPI serves bootstack=={VERSION}", bool(wheel),
           wheel or out.stderr.strip().splitlines()[-1][:120] if out.stderr else "no wheel")
    return os.path.join(tmp, wheel) if wheel else None


def check_version_endpoint():
    """The per-version endpoint, which is not the lagging one."""
    url = f"https://pypi.org/pypi/bootstack/{VERSION}/json"
    body, err = fetch(url)
    if body is None:
        record("per-version PyPI endpoint responds", None, err)
        return
    try:
        data = json.loads(body)
        record("per-version PyPI endpoint responds", True,
               f"{len(data.get('urls', []))} files, version {data['info']['version']}")
    except Exception as e:
        record("per-version PyPI endpoint responds", False, f"{type(e).__name__}: {e}")


def check_wheel_contents(wheel):
    """The fix inside the PUBLISHED artifact, not the source tree -- that is what
    proves a packaging-shaped bug is fixed."""
    if not wheel:
        record("the fix is inside the published wheel", None, "no wheel to open")
        record("NOTICE ships at dist-info/licenses/", None, "no wheel to open")
        return
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
        try:
            src = z.read("bootstack/validation/validation_rules.py").decode("utf-8")
        except KeyError:
            src = ""
    record("the fix is inside the published wheel", "_uncheckable_message" in src,
           "validation_rules.py carries _uncheckable_message (#467)")
    notice = [n for n in names if n.endswith("NOTICE") and ".dist-info/licenses/" in n]
    record("NOTICE ships at dist-info/licenses/", bool(notice),
           notice[0] if notice else "not found under dist-info/licenses/")


def check_import_without_idlelib(tmp, wheel):
    """#430. Grep is NOT enough and gives a false positive -- seven idlelib
    mentions survive in the wheel and all are docstring attributions."""
    if not wheel:
        record("import works with idlelib blocked", None, "no wheel to install")
        return
    venv = os.path.join(tmp, "v")
    if run(sys.executable, "-m", "venv", venv).returncode != 0:
        record("import works with idlelib blocked", None, "could not build a venv")
        return
    py = os.path.join(venv, "Scripts" if os.name == "nt" else "bin",
                      "python.exe" if os.name == "nt" else "python")
    if run(py, "-m", "pip", "install", "-q", wheel).returncode != 0:
        record("import works with idlelib blocked", None, "wheel would not install")
        return
    probe = (
        "import sys\n"
        "class Block:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'idlelib' or name.startswith('idlelib.'):\n"
        "            raise ImportError('idlelib is blocked')\n"
        "sys.meta_path.insert(0, Block())\n"
        # the control: prove the block actually blocks, or the check is vacuous
        "try:\n"
        "    import idlelib\n"
        "    print('CONTROL-FAILED')\n"
        "    raise SystemExit(2)\n"
        "except ImportError:\n"
        "    pass\n"
        "import bootstack, os\n"
        "print('OK', os.path.dirname(bootstack.__file__))\n"
    )
    out = run(py, "-c", probe)
    ok = out.returncode == 0 and out.stdout.startswith("OK")
    where = out.stdout.split(" ", 1)[1].strip() if ok else ""
    record("import works with idlelib blocked (control asserted)", ok,
           where or (out.stdout + out.stderr).strip().splitlines()[-1][:120])
    if ok:
        record("provenance is the installed wheel, not the editable tree",
               venv in where, where)


def check_github_release():
    out = run("gh", "release", "view", f"v{VERSION}", "--json", "assets,name,isDraft")
    if out.returncode != 0:
        record(f"GitHub Release v{VERSION} is live", False, out.stderr.strip()[:120])
        return
    data = json.loads(out.stdout)
    names = [a["name"] for a in data.get("assets", [])]
    has_both = any(n.endswith(".whl") for n in names) and any(n.endswith(".tar.gz") for n in names)
    record(f"GitHub Release v{VERSION} is live", not data.get("isDraft"),
           f"title: {data.get('name')}")
    record("Release carries both a wheel and an sdist", has_both, ", ".join(names) or "no assets")


def check_docs_deploy():
    """docs.yml is CHAINED to release.yml SUCCEEDING, not to the tag. A run that
    shows completed/skipped reads like a no-op and leaves the site stale."""
    out = run("gh", "run", "list", "--workflow", "docs.yml", "--limit", "3",
              "--json", "conclusion,status,createdAt,headBranch")
    if out.returncode != 0:
        record("docs.yml actually ran", None, "gh unavailable")
        return
    runs = json.loads(out.stdout)
    latest = runs[0] if runs else None
    ok = bool(latest) and latest.get("conclusion") == "success"
    record("docs.yml latest run succeeded", ok,
           f"{latest.get('status')}/{latest.get('conclusion')} at {latest.get('createdAt')}"
           if latest else "no runs")


def check_site():
    for url in ("https://bootstack.org", "https://pypi.org/project/bootstack/"):
        code, err = http_status(url)
        if code is None:
            record(f"{url} returns 200", None, err)
        else:
            record(f"{url} returns 200", code == 200, f"HTTP {code}")


def main():
    if not VERSION:
        print(__doc__)
        return 1
    print(f"Verifying bootstack {VERSION}\n")
    tmp = tempfile.mkdtemp(prefix="bootstack-verify-")
    try:
        wheel = check_pypi_download(tmp)
        check_version_endpoint()
        check_wheel_contents(wheel)
        check_import_without_idlelib(tmp, wheel)
        check_github_release()
        check_docs_deploy()
        check_site()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fails = sum(1 for _, ok in RESULTS if ok is False)
    skips = sum(1 for _, ok in RESULTS if ok is None)
    print(f"\n{len(RESULTS) - fails - skips} passed, {fails} failed, {skips} skipped")
    return fails


if __name__ == "__main__":
    raise SystemExit(main())
