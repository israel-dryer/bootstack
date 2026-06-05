from __future__ import annotations

import time
import tkinter as tk
from datetime import datetime
from typing import Any, Callable, Optional


class Job:
    """Handle for a scheduled task.

    Returned by every `Schedule` method. Call `.cancel()` to stop a pending
    job before it fires. Truthy while active, falsy once cancelled or complete.
    """

    __slots__ = ("_owner", "_after_id", "_active", "_discard")

    def __init__(self, owner: tk.Misc, discard: Callable[[], None]) -> None:
        self._owner = owner
        self._after_id: Optional[str] = None
        self._active: bool = True
        self._discard = discard

    def cancel(self) -> None:
        """Cancel the job if it has not already fired or been cancelled."""
        if not self._active:
            return
        try:
            if self._after_id is not None:
                self._owner.after_cancel(self._after_id)
        except Exception:
            pass
        finally:
            self._after_id = None
            self._active = False
            self._discard()

    def __bool__(self) -> bool:
        return self._active

    def __repr__(self) -> str:
        state = "active" if self._active else "cancelled"
        return f"<Job {state}>"


class Schedule:
    """Timed task scheduler tied to a widget's lifetime.

    Runs callbacks after a delay, at idle, at an absolute time, or on a repeat,
    with automatic cleanup: all pending jobs are cancelled when the owner widget
    is destroyed.

    Usage::

        sched = widget.schedule          # property on every public widget
        sched = bs.Schedule(widget)      # or construct directly

        job = sched.delay(500, callback)   # one-shot after delay
        sched.idle(callback)               # one-shot at next idle
        sched.at(datetime(...), callback)  # one-shot at absolute time
        job = sched.every(1000, tick)      # repeating every 1 second

        job.cancel()        # cancel one job
        sched.cancel_all()  # cancel everything

    All jobs are automatically cancelled when `owner` is destroyed.

    Args:
        owner: Widget that owns this scheduler. Its lifetime bounds all created
            jobs.
    """

    __slots__ = ("_owner", "_jobs")

    def __init__(self, owner: Any) -> None:
        # Accept both public wrapper widgets and the underlying widget object.
        if hasattr(owner, "_internal"):
            owner = owner._internal
        self._owner: tk.Misc = owner
        self._jobs: set[Job] = set()
        try:
            owner.bind("<Destroy>", self._on_destroy, add=True)
        except Exception:
            pass

    # ----- public API --------------------------------------------------------

    def delay(self, ms: int, fn: Callable, *args: Any, **kwargs: Any) -> Job:
        """Schedule `fn` to run once after `ms` milliseconds.

        Args:
            ms: Delay in milliseconds (clamped to 0).
            fn: Callable to invoke.
            *args: Positional arguments forwarded to `fn`.
            **kwargs: Keyword arguments forwarded to `fn`.

        Returns:
            Job handle — call `.cancel()` to prevent execution.
        """
        ms = max(0, int(ms))
        job = Job(self._owner, lambda: self._jobs.discard(job))

        def _run():
            job._after_id = None
            if job._active:
                job._active = False
                self._jobs.discard(job)
                fn(*args, **kwargs)

        job._after_id = self._owner.after(ms, _run)
        self._jobs.add(job)
        return job

    def idle(self, fn: Callable, *args: Any, **kwargs: Any) -> Job:
        """Schedule `fn` to run once when the event loop is next idle.

        Args:
            fn: Callable to invoke.
            *args: Positional arguments forwarded to `fn`.
            **kwargs: Keyword arguments forwarded to `fn`.

        Returns:
            Job handle — call `.cancel()` to prevent execution.
        """
        job = Job(self._owner, lambda: self._jobs.discard(job))

        def _run():
            job._after_id = None
            if job._active:
                job._active = False
                self._jobs.discard(job)
                fn(*args, **kwargs)

        job._after_id = self._owner.after_idle(_run)
        self._jobs.add(job)
        return job

    def at(self, when: datetime, fn: Callable, *args: Any, **kwargs: Any) -> Job:
        """Schedule `fn` to run at an absolute `datetime`.

        If `when` is in the past the job runs as soon as possible.

        Args:
            when: Target `datetime` (local time).
            fn: Callable to invoke.
            *args: Positional arguments forwarded to `fn`.
            **kwargs: Keyword arguments forwarded to `fn`.

        Returns:
            Job handle.
        """
        delay_ms = max(0, int((when - datetime.now()).total_seconds() * 1000))
        return self.delay(delay_ms, fn, *args, **kwargs)

    def every(self, ms: int, fn: Callable, *args: Any, **kwargs: Any) -> Job:
        """Schedule `fn` to run repeatedly every `ms` milliseconds.

        Compensates for callback execution time to reduce drift. If the
        callback raises an exception the interval is stopped and the exception
        is re-raised into the application's error handler.

        Args:
            ms: Period in milliseconds (minimum 1).
            fn: Callable to invoke on each tick.
            *args: Positional arguments forwarded to `fn`.
            **kwargs: Keyword arguments forwarded to `fn`.

        Returns:
            Job handle — call `.cancel()` to stop the repeating task.
        """
        period = max(1, int(ms))
        job = Job(self._owner, lambda: self._jobs.discard(job))

        def _tick():
            if not job._active:
                return
            start = time.perf_counter()
            try:
                fn(*args, **kwargs)
            except Exception:
                # Stop the interval cleanly before re-raising.
                job._active = False
                job._after_id = None
                self._jobs.discard(job)
                raise
            if job._active:
                elapsed = int((time.perf_counter() - start) * 1000)
                next_ms = max(0, period - elapsed)
                try:
                    job._after_id = self._owner.after(next_ms, _tick)
                except Exception:
                    job._active = False
                    job._after_id = None
                    self._jobs.discard(job)

        job._after_id = self._owner.after(period, _tick)
        self._jobs.add(job)
        return job

    def cancel_all(self) -> None:
        """Cancel all pending jobs created by this `Schedule`."""
        for j in list(self._jobs):
            try:
                j.cancel()
            except Exception:
                pass
        self._jobs.clear()

    # ----- internal ----------------------------------------------------------

    def _on_destroy(self, *_: Any) -> None:
        self.cancel_all()
