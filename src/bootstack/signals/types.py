"""Type aliases for the signal and variable tracing system."""
from typing import Literal

TraceOperation = Literal["array", "read", "write", "unset"]
"""The kind of variable access a trace callback reports — an `array` element
access, a `read`, a `write`, or an `unset`."""
