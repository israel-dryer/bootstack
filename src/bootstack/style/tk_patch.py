"""Shim so style imports keep working while runtime owns tk_patch."""

from bootstack.runtime.tk_patch import install_tk_autostyle

__all__ = ["install_tk_autostyle"]
