"""Backwards compatibility layer - constants moved to bootstack.constants.

!!! warning "Deprecated"
    Import from `bootstack.constants` instead of `bootstack.core.constants`.

This module re-exports all constants from the root-level constants module
for backwards compatibility with existing code.

Example:
    ```python
    # New (preferred)
    from bootstack.constants import *

    # Old (still works but deprecated)
    from bootstack.core.constants import *
    ```
"""

# Re-export everything from root constants module
from bootstack.constants import *  # noqa: F401, F403