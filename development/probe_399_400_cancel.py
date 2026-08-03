"""Measure the #399/#400 interaction.

1. Does the #399 warning escape Subscription.cancel() under -W error?
2. Does cancel() mark cancelled on the unmatched-funcid path?
3. In the reachable unmatched case (wholesale unbind, then per-funcid cancel),
   is the handler genuinely gone — i.e. is marking cancelled the right answer?
"""
import os
import warnings

os.environ["BOOTSTACK_DEBUG"] = "1"
warnings.simplefilter("error")  # what -W error does

import bootstack as bs
from bootstack.events import ChangeEvent

results = {}

with bs.App(title="probe") as app:
    field = bs.TextField()
app._tk_root.update_idletasks()

# --- 3. reachable unmatched case: wholesale unbind, then cancel() --------
seen = []
sub = field.on_change(lambda e: seen.append(e.value))
target = field._event_target("<<Change>>")
target.unbind("<<Change>>")          # wholesale — clears the script
field.emit("change", data=ChangeEvent(value="after-wholesale"))
app._tk_root.update()
results["handler_gone_after_wholesale_unbind"] = (seen == [], f"seen={seen!r}")

# --- 1. does cancel() raise under -W error? ------------------------------
try:
    sub.cancel()
    raised = None
except BaseException as exc:
    raised = f"{type(exc).__name__}: {exc}"
results["cancel_does_not_raise_under_W_error"] = (raised is None, f"raised={raised}")

# --- 2. what does cancelled read? ---------------------------------------
results["cancelled_reads_true_on_unmatched"] = (
    sub.cancelled is True, f"cancelled={sub.cancelled!r}"
)

# --- 4. __exit__ must also survive ---------------------------------------
sub2 = field.on_change(lambda e: None)
t2 = field._event_target("<<Change>>")
t2.unbind("<<Change>>")
try:
    with sub2:
        pass
    exit_raised = None
except BaseException as exc:
    exit_raised = f"{type(exc).__name__}: {exc}"
results["context_exit_does_not_raise"] = (exit_raised is None, f"raised={exit_raised}")

ok = sum(1 for passed, _ in results.values() if passed)
for name, (passed, detail) in results.items():
    print(f"{'PASS' if passed else 'FAIL'}  {name:38} {detail}")
print(f"\n{ok}/{len(results)}")
