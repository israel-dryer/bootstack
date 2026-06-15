from __future__ import annotations

from typing import Any, Callable, Literal, TYPE_CHECKING

from bootstack.validation import RuleType
from bootstack.widgets.types import AccentToken

if TYPE_CHECKING:
    from bootstack.signals import Signal


class FieldAddonMixin:
    """Mixin that exposes `insert_addon` and `addons` on public field wrappers.

    Requires the inheriting class to have `self._internal` pointing to a
    `Field`-based composite that implements `insert_addon` / `addons`.
    """

    _ADDON_TYPES = {
        "button":  "bootstack.widgets._impl.primitives.button::Button",
        "label":   "bootstack.widgets._impl.primitives.label::Label",
        "toggle":  "bootstack.widgets._impl.primitives.checktoggle::CheckToggle",
    }

    def insert_addon(
        self,
        widget: Literal["button", "label", "toggle"],
        position: Literal["before", "after"],
        *,
        name: str | None = None,
        text: str | None = None,
        icon: str | None = None,
        accent: AccentToken | str | None = None,
        on_click: Callable[[], Any] | None = None,
        signal: "Signal | None" = None,
        active_when_readonly: bool = False,
    ) -> Any:
        """Insert a small widget inside the field border, before or after the input.

        Use this for affordances such as a clear button, a search icon, a unit
        suffix label, or an on/off toggle.

        Args:
            widget: Addon type — `'button'` (clickable), `'label'` (static
                text or icon), or `'toggle'` (on/off control).
            position: `'before'` (left of the input) or `'after'` (right).
            name: Key to retrieve the addon later via `addons`. Auto-generated
                if omitted.
            text: Text shown on the addon. Applies to any addon type.
            icon: Bootstrap Icons name shown on the addon (e.g. `'search'`,
                `'x-lg'`). An icon-only addon is rendered when `icon` is given
                without `text`.
            accent: Accent token for the addon. Prefer an accent for a
                text-only button.
            on_click: Called with no arguments when a `'button'` or `'toggle'`
                addon is activated.
            signal: Reactive `Signal[bool]` bound to a `'toggle'` addon's
                on/off state.
            active_when_readonly: Keep the addon interactive while the field is
                read-only. Off by default, so addons follow the field's
                read-only state — appropriate since most act on the value (a
                clear button, the spin buttons). Set `True` only for a
                read-only-safe action such as a copy or reveal button; it still
                dims when the field is fully disabled.

        Returns:
            The created addon widget instance.
        """
        if widget not in self._ADDON_TYPES:
            raise ValueError(f"widget must be 'button', 'label', or 'toggle'; got {widget!r}")
        if on_click is not None and widget == "label":
            raise ValueError("on_click is not valid for a 'label' addon")
        if signal is not None and widget != "toggle":
            raise ValueError("signal is only valid for a 'toggle' addon")

        module_path, cls_name = self._ADDON_TYPES[widget].split("::")
        import importlib
        cls = getattr(importlib.import_module(module_path), cls_name)

        if name is None:
            seq = getattr(self, "_addon_seq", 0)
            self._addon_seq = seq + 1
            name = f"addon_{seq}"

        addon_kwargs: dict[str, Any] = {}
        if text is not None:
            addon_kwargs["text"] = text
        if icon is not None:
            addon_kwargs["icon"] = icon
        if on_click is not None:
            addon_kwargs["command"] = on_click
        if signal is not None:
            addon_kwargs["signal"] = signal

        return self._internal.insert_addon(
            cls, position, name=name, accent=accent,
            active_when_readonly=active_when_readonly, **addon_kwargs,
        )

    def update_addon(
        self,
        name: str,
        *,
        text: str | None = None,
        icon: str | None = None,
        accent: AccentToken | str | None = None,
        on_click: Callable[[], Any] | None = None,
    ) -> None:
        """Reconfigure an existing addon in place.

        Only the options you pass are changed. Use this, for example, to flip a
        toggle addon's label between two units, or swap a button's icon.

        Args:
            name: The addon's name (as passed to `insert_addon`).
            text: New text for the addon.
            icon: New Bootstrap Icons name for the addon.
            accent: New accent token for the addon.
            on_click: New click handler for a `'button'` or `'toggle'` addon.

        Raises:
            KeyError: If no addon with that name exists.
        """
        try:
            addon = self._internal.addons[name]
        except KeyError:
            raise KeyError(f"no addon named {name!r}") from None
        config: dict[str, Any] = {}
        if text is not None:
            config["text"] = text
        if icon is not None:
            config["icon"] = icon
        if accent is not None:
            config["accent"] = accent
        if on_click is not None:
            config["command"] = on_click
        if config:
            addon.configure(**config)

    def remove_addon(self, name: str) -> None:
        """Remove an addon inserted with `insert_addon()`.

        Args:
            name: The addon's name (as passed to `insert_addon`).

        Raises:
            KeyError: If no addon with that name exists.
        """
        self._internal.remove_addon(name)

    @property
    def addons(self) -> dict[str, Any]:
        """Named addon widgets inserted via `insert_addon()`."""
        return self._internal.addons

    @property
    def text(self) -> str:
        """The current display text shown in the field.

        This is the formatted string the user sees, as opposed to `value`, which
        is the raw parsed datum (e.g. for a `DateField`, `text` is `'Jan 2, 2024'`
        while `value` is a `date`). Read-only — assign to `value` to change it.
        """
        return self._internal.get()

    def add_validation_rule(self, rule_type: RuleType, **kwargs: Any) -> None:
        """Add a validation rule to the field.

        Rules run automatically on blur or key events depending on the rule
        type, or manually via ``validate()``. Multiple rules can be added;
        they are evaluated in order and stop at the first failure.

        Args:
            rule_type: The kind of validation rule to apply.
            **kwargs: Rule-specific options:

                - ``message`` *(all rules)* — override the default error message.
                - ``trigger`` *(all rules)* — when to run: ``'always'`` (key and
                  blur), ``'key'``, ``'blur'``, or ``'manual'``. Each rule type
                  has its own sensible default (see the Validation reference).
                - ``min``, ``max`` *(stringLength)* — minimum/maximum character count.
                - ``pattern`` *(pattern)* — regex string the value must match.
                - ``other_field`` *(compare)* — field whose value must match.
                - ``func`` *(custom)* — callable ``(value: str) -> bool``.

        Example::

            field.add_validation_rule("required")
            field.add_validation_rule("stringLength", min=3, max=50)
            field.add_validation_rule("email", message="Enter a valid email.")
            field.add_validation_rule("custom", func=lambda v: v.isdigit())
        """
        self._internal.add_validation_rule(rule_type, **kwargs)


class ValueSignalMixin:
    """Two-way binds a field's typed `.value` to a public `signal`.

    The signal carries the field's **value** (a number, date, time, …) — not its
    text. The inheriting wrapper must expose a `value` property (get and set) and
    an `on_change` event; this mixin keeps the two in sync, seeding the field from
    the signal and updating the signal when the field commits a new value.
    """

    value: Any
    on_change: Callable

    def _bind_value_signal(self, signal: "Signal") -> None:
        """Establish the two-way binding between `self.value` and `signal`."""
        self._value_signal = signal
        self._value_syncing = False

        current = signal()
        if current is not None:
            self.value = current
        else:
            self._push_to_signal(self.value)

        def _from_signal(v: Any) -> None:
            if self._value_syncing or v is None:
                return
            self._value_syncing = True
            try:
                self.value = v
            finally:
                self._value_syncing = False

        def _to_signal(_event: Any) -> None:
            if self._value_syncing:
                return
            v = self.value
            if v is None:
                return
            self._value_syncing = True
            try:
                self._push_to_signal(v)
            finally:
                self._value_syncing = False

        # Hold the subscription id so it can be released on destroy. A Signal
        # usually outlives the widgets bound to it, so a dangling subscription
        # would pin a destroyed field (and all it references) in memory.
        self._value_sub = signal.subscribe(_from_signal)
        self.on_change(_to_signal)
        self.on_destroy(lambda _e: self._release_value_signal())

    def _push_to_signal(self, value: Any) -> None:
        """Write `value` to the bound signal, reconciling numeric types.

        `Signal` is strict about value type (it only widens `int` into a
        `float`-typed signal). A numeric field can produce either an `int` or a
        `float`, so reconcile the two here. If the signal's type is genuinely
        incompatible (for example an `int`-typed signal and a fractional value),
        leave the signal unchanged rather than raising into the Tk event loop.
        """
        signal = self._value_signal
        target = getattr(signal, "_type", None)
        if target is not None and type(value) is not target:
            if target is float and type(value) is int:
                value = float(value)
            elif target is int and type(value) is float and value.is_integer():
                value = int(value)
        try:
            signal.set(value)
        except TypeError:
            pass

    def _release_value_signal(self) -> None:
        """Drop the value-signal subscription (called on widget destroy)."""
        sub = getattr(self, "_value_sub", None)
        if sub is not None:
            try:
                sub.cancel()
            except Exception:
                pass
            self._value_sub = None

    @property
    def signal(self) -> "Signal | None":
        """The reactive `Signal` bound to this field's value, or `None`."""
        return getattr(self, "_value_signal", None)
