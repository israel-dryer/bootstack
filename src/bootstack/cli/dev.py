"""bootstack dev command - Run an application with hot reload.

PROVISIONAL — the dev workflow ships in 0.1.0 but is carved out of the API
freeze and may change in a minor release.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
from pathlib import Path

from bootstack.cli.config import TtkbConfig, find_config


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    """Add the 'dev' subcommand parser."""
    parser = subparsers.add_parser(
        "dev",
        help="Run the application with hot reload",
        description=(
            "Run the application with live reload. Saving a source file updates "
            "the running app. A module-level `with bs.App()` reloads in place "
            "(state preserved); anything else falls back to a process restart."
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to entry point or directory with bootstack.toml (default: current directory)",
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Always reload by restarting the process, even for a module-level app",
    )
    parser.set_defaults(func=run_dev)


def run_dev(args: argparse.Namespace) -> None:
    """Execute the dev command."""
    resolved = _resolve_entry(args.path)
    if resolved is None:
        return
    entry_point, project_root = resolved

    if not entry_point.exists():
        print(f"Error: Entry point '{entry_point}' does not exist.")
        return

    try:
        display_path = entry_point.relative_to(project_root)
    except ValueError:
        display_path = entry_point
    print(f"Starting {display_path} with hot reload...")
    print("(Save a file to reload. Press Ctrl+C to stop.)")
    print()

    env = dict(os.environ)
    env["BOOTSTACK_DEV"] = "1"
    env["BOOTSTACK_DEV_MODE"] = "restart" if args.restart else "inprocess"

    src_dir = project_root / "src"
    if src_dir.exists():
        python_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{src_dir}{os.pathsep}{python_path}" if python_path else str(src_dir)
        )

    # Supervise the app here rather than letting it os.execv itself on restart:
    # on Windows execv does not replace the process in place — it spawns a new
    # PID and terminates the caller, which would drop this supervisor after the
    # first reload and orphan the app. The child re-launches by exiting with
    # DEV_RESTART_EXIT_CODE; looping subprocess.run is portable and re-establishes
    # cwd + env on every relaunch.
    from bootstack.dev._env import DEV_RESTART_EXIT_CODE

    try:
        while True:
            result = subprocess.run(
                [sys.executable, str(entry_point.resolve())],
                cwd=str(project_root),
                env=env,
            )
            if result.returncode == DEV_RESTART_EXIT_CODE:
                continue  # a valid edit asked for a clean restart
            if result.returncode == 0:
                sys.exit(0)  # the app window was closed normally
            # The app crashed (e.g. an edit raised at import). Don't end the
            # session — stay alive and relaunch when the file is fixed and
            # saved. This is the restart-mode counterpart to the in-process
            # error banner's fix-and-save recovery; the child's own watcher
            # died with it, so the supervisor watches in the meantime.
            print(
                f"\n[bootstack dev] app exited with code {result.returncode} - "
                "waiting for a change to retry (Ctrl+C to stop)...",
                flush=True,
            )
            _wait_for_change(str(project_root))
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)


def _wait_for_change(root: str) -> None:
    """Block until a watched source file under `root` changes (or Ctrl+C).

    Used by the restart supervisor to stay alive after the app crashes: rather
    than ending the dev session, it waits for the next save and lets the loop
    relaunch.
    """
    from bootstack.dev._watcher import PollWatcher

    changed = threading.Event()
    watcher = PollWatcher(root, lambda _paths: changed.set())
    watcher.start()
    try:
        # Short timed waits keep Ctrl+C responsive on Windows, where a bare
        # Event.wait() with no timeout can swallow the interrupt.
        while not changed.wait(0.3):
            pass
    finally:
        watcher.stop()


def _resolve_entry(path: str | None) -> tuple[Path, Path] | None:
    """Resolve (entry_point, project_root) from a path or bootstack.toml."""
    if path:
        p = Path(path)
        if p.is_file() and p.suffix == ".py":
            return p, p.parent
        if p.is_dir():
            config_path = p / "bootstack.toml"
            if not config_path.exists():
                print(f"Error: No bootstack.toml found in '{p}'")
                return None
            config = TtkbConfig.load(config_path)
            return p / config.app.entry, p
        print(f"Error: '{path}' is not a valid file or directory")
        return None

    config_path = find_config()
    if config_path is None:
        print("Error: No bootstack.toml found in current directory or parents.")
        print("Pass a path: bootstack dev app.py")
        return None
    config = TtkbConfig.load(config_path)
    project_root = config_path.parent
    return project_root / config.app.entry, project_root