---
name: feedback-no-v2-terminology
description: Don't call it "v2 public API" — just "public API". The project is pre-release with no versioned public surface.
metadata:
  type: feedback
---

Never refer to the current API as "v2", "v2 public API", or "the v2 layer". Just call it "the public API".

**Why:** bootstack is pre-release. There is no v1 in the wild, so there is no v2. The user has corrected this several times.

**How to apply:** In code comments, docstrings, commit messages, and conversation — always say "public API", never "v2 API" or "v2 public API".