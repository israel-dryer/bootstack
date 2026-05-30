---
name: feedback-demo-pattern
description: Demo/feature test scripts should run at module level, not wrapped in a function
metadata:
  type: feedback
---

Don't wrap demo scripts in a function unless the function is truly needed (e.g., called multiple times or requires arguments).

**Why:** Unnecessary wrapper functions add indentation and boilerplate with no benefit for one-shot demo scripts.

**How to apply:** In `tests/features/*.py`, write the `with bs.App(...) as app:` block directly at module level and call `app.run()` at the end. No wrapping function.