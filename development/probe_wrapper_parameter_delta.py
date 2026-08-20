"""Probe: wrapper vs internal parameter delta (#463).

WHAT THIS IS
------------
A mechanical scan of the public wrapper layer against the internal widgets it
composes. The internal widget is the specification; this probe diffs the two
signatures and classifies the delta.

It exists because the check this project has been using --
`git show main:<wrapper> | grep <kwarg>` -- catches exactly ONE of the five
ways a wrapper goes wrong (the mode table below), and the one that keeps
landing (mode 2, forwarded to the WRONG destination: #458, #461) is not it.

THE FIVE FAILURE MODES
----------------------
  1 never forwarded      the kwarg exists on the wrapper, never reaches the
                         internal                                 (#383 gap 3)
  2 wrong destination    forwarded, to the wrong internal parameter (#458, #461)
  3 swallowed as layout  falls into **kwargs, _split_layout_kwargs eats it,
                         nothing raises                                 (#456)
  4 accepted then        reaches the internal and is overwritten by something
    ignored              recomputed                                     (#453)
  5 the type lies        the annotation describes a value the code cannot
                         produce                                        (#460)

Modes 1, 2, 3 and 5 are static and are what this probe measures. Mode 4 is NOT
statically decidable and this probe DOES NOT claim to find it -- see
`--arm roundtrip` and the honesty note it prints.

ARMS
----
  --arm scan       the static pass (default)
  --arm control    the non-vacuity controls; run this before believing any
                   "no findings" result
  --arm roundtrip  the runtime construct-and-read-back heuristic (needs a
                   display; a PARTIAL view of mode 4, limits printed inline)

SCOPE -- stated mechanically, because a completeness claim whose scope was
never written down reads as global and is checked as local:

  scanned:  src/bootstack/widgets/*.py           (override with --src)
  NOT scanned unless asked: src/bootstack/dialogs/  (--src accepts it)
  skipped classes and the reason are printed in the SKIPPED section
  forwarding idioms understood are printed in the IDIOMS section; a wrapper
  whose idiom is not understood is reported as UNANALYZED, never as clean

Output is ASCII only (the Windows box console is cp1252).
"""

from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


# --------------------------------------------------------------------------
# source loading -- utf-8-sig, and NO bare except swallowing a parse failure
# --------------------------------------------------------------------------

def load_module_asts(src: Path) -> tuple[dict[str, ast.Module], list[str]]:
    """Parse every .py under `src`. Returns (asts_by_stem, failures).

    A completeness scan in this project once reported zero hits because
    `ast.parse` choked on a UTF-8 BOM and a bare `except Exception: continue`
    swallowed it. Files are read as utf-8-sig and every failure is COUNTED and
    RETURNED, so `files_parsed + failures == files_found` can be asserted.
    """
    trees: dict[str, ast.Module] = {}
    failures: list[str] = []
    for path in sorted(src.glob("*.py")):
        text = path.read_bytes().decode("utf-8-sig")
        try:
            trees[path.stem] = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append("%s: %s" % (path.name, exc))
    return trees, failures


# --------------------------------------------------------------------------
# static model of one module
# --------------------------------------------------------------------------

def import_alias_map(tree: ast.Module) -> dict[str, str]:
    """Map a bound name to the dotted path it was imported from.

    Walks the whole tree, not just the module body: several wrappers import the
    internal inside `__init__` or under `if TYPE_CHECKING`.
    """
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for a in node.names:
                aliases.setdefault(a.asname or a.name, "%s.%s" % (node.module, a.name))
        elif isinstance(node, ast.Import):
            for a in node.names:
                aliases.setdefault(a.asname or a.name, a.name)
    return aliases


def classes_of(tree: ast.Module) -> dict[str, ast.ClassDef]:
    return {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}


def base_names(cls: ast.ClassDef) -> list[str]:
    out = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out


def find_in_mro(name: str, classes: dict[str, ast.ClassDef], want):
    """Walk `name` and its bases within this module for what `want` returns."""
    seen: set[str] = set()
    stack = [name]
    while stack:
        cur = stack.pop(0)
        if cur in seen or cur not in classes:
            continue
        seen.add(cur)
        found = want(classes[cur])
        if found is not None:
            return found, cur
        stack.extend(base_names(classes[cur]))
    return None, None


def _own_init(cls: ast.ClassDef):
    for n in cls.body:
        if isinstance(n, ast.FunctionDef) and n.name == "__init__":
            return n
    return None


def _own_internal_class(cls: ast.ClassDef):
    for n in cls.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == "_internal_class" \
                        and isinstance(n.value, ast.Name):
                    return n.value.id
    return None


def init_params(fn: ast.FunctionDef) -> tuple[list[str], str | None]:
    """Return ([param names in declaration order], kwargs catch-all name)."""
    a = fn.args
    names = [arg.arg for arg in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)
             if arg.arg != "self"]
    return names, (a.kwarg.arg if a.kwarg else None)


def names_in(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


# --------------------------------------------------------------------------
# the forwarding analysis
# --------------------------------------------------------------------------

class Dest:
    """One key the wrapper writes into the internal's kwargs."""

    def __init__(self, key: str, names: set[str], guards: set[str],
                 direct: str | None, text: str, line: int) -> None:
        self.key = key
        self.names = names          # params flowing into the VALUE
        self.guards = guards        # params only guarding whether it is written
        self.direct = direct        # param name if the value is exactly that name
        self.text = text
        self.line = line


class Forwarding:
    def __init__(self) -> None:
        self.internal_expr: str | None = None
        self.dest: list[Dest] = []
        self.splat_vars: list[str] = []
        self.opaque: list[str] = []
        self.forwards_catchall = False
        self.passthrough: set[str] = set()   # params merged in wholesale
        self.understood = False
        self.why_not = ""
        self.via = ""               # non-empty when not the plain idiom
        self.terminal: Any = None   # the __init__ that builds the internal


def _assignments(fn: ast.FunctionDef):
    """Every simple assignment in `fn`, as (target_node, value_node)."""
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            yield node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            yield node.target, node.value


def _is_self_attr(node: ast.AST, attr: str | None = None) -> bool:
    return (isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name) and node.value.id == "self"
            and (attr is None or node.attr == attr))


def _find_internal_call(fn: ast.FunctionDef,
                        aliases: dict[str, str] | None = None):
    """The call that builds the internal widget, and how it was reached.

    Three idioms, in order:
      1. `self._internal = Internal(...)`                       -- the common one
      2. `self._tk_root = Internal(...)` ... `self._internal = self._tk_root`
         -- the window family (App, Window, Splash) builds the root first and
         aliases it afterwards, so a tool that only matches idiom 1 reports
         those wrappers (80+ parameters) as unanalysable
      3. no `self._internal` at all -- a page/handle class that builds a layout
         frame directly. Analysed against that frame, and LABELLED, because it
         is not the wrapper-over-internal shape this audit is about.
    """
    # idiom 1
    for target, value in _assignments(fn):
        if _is_self_attr(target, "_internal") and isinstance(value, ast.Call):
            return value, ""
    # idiom 2 -- one alias hop
    alias_of = None
    for target, value in _assignments(fn):
        if _is_self_attr(target, "_internal"):
            if _is_self_attr(value):
                alias_of = value.attr
            elif isinstance(value, ast.Name):
                alias_of = value.id
    if alias_of is not None:
        for target, value in _assignments(fn):
            hit = (_is_self_attr(target) and target.attr == alias_of) or (
                isinstance(target, ast.Name) and target.id == alias_of)
            if hit and isinstance(value, ast.Call):
                return value, "self._internal = self.%s, built earlier" % alias_of
    # idiom 3 -- a handle class; use the first _impl widget it builds
    if aliases:
        for target, value in _assignments(fn):
            if not (isinstance(value, ast.Call) and _is_self_attr(target)):
                continue
            func = value.func
            name = func.id if isinstance(func, ast.Name) else None
            if name and "_impl" in aliases.get(name, ""):
                return value, ("no self._internal; analysed against self.%s = %s()"
                               % (target.attr, name))
    return None, ""


def _dict_writes(fn: ast.FunctionDef, var: str, catchall: str | None,
                 fwd: Forwarding) -> None:
    """Collect every write into `var`, remembering the `if` tests that guard it.

    The guard matters: `if disabled: kw['state'] = 'disabled'` forwards the
    parameter even though its name never appears in the value.
    """

    def visit(stmts, guards: set[str]) -> None:
        for st in stmts:
            if isinstance(st, ast.If):
                g = guards | names_in(st.test)
                visit(st.body, g)
                visit(st.orelse, g)
                continue
            if isinstance(st, (ast.For, ast.AsyncFor)):
                # `for k, v in {"padding": padding, ...}.items(): var[k] = v`
                # -- Grid's idiom for "only forward the ones that are set". The
                # key is a loop variable, so the plain subscript rule sees a
                # computed key and gives up; the dict literal right there names
                # every key and value. Without this, `Grid(padding=)` reads as
                # never forwarded, which it plainly is.
                literal = None
                if (isinstance(st.iter, ast.Call)
                        and isinstance(st.iter.func, ast.Attribute)
                        and st.iter.func.attr == "items"
                        and isinstance(st.iter.func.value, ast.Dict)):
                    literal = st.iter.func.value
                if literal is not None and isinstance(st.target, ast.Tuple) \
                        and len(st.target.elts) == 2:
                    kvar = st.target.elts[0]
                    vvar = st.target.elts[1]
                    writes_through = any(
                        isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                        and t.value.id == var
                        and isinstance(t.slice, ast.Name)
                        and isinstance(kvar, ast.Name) and t.slice.id == kvar.id
                        and isinstance(val, ast.Name) and isinstance(vvar, ast.Name)
                        and val.id == vvar.id
                        for t, val in _assignments(st))
                    if writes_through:
                        for k, v in zip(literal.keys, literal.values):
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                _add(fwd, k.value, v, guards)
                        continue
                visit(st.body, guards | names_in(st.iter))
                visit(st.orelse, guards)
                continue
            if isinstance(st, (ast.While, ast.With, ast.AsyncWith)):
                visit(st.body, guards)
                visit(getattr(st, "orelse", []), guards)
                continue
            if isinstance(st, ast.Try):
                visit(st.body, guards)
                for h in st.handlers:
                    visit(h.body, guards)
                visit(st.orelse, guards)
                visit(st.finalbody, guards)
                continue

            tgt = None
            if isinstance(st, ast.Assign) and len(st.targets) == 1:
                tgt = st.targets[0]
            elif isinstance(st, ast.AnnAssign):
                tgt = st.target

            # var = {...}
            if isinstance(tgt, ast.Name) and tgt.id == var and st.value is not None \
                    and isinstance(st.value, ast.Dict):
                for k, v in zip(st.value.keys, st.value.values):
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        _add(fwd, k.value, v, guards)
                    else:
                        fwd.opaque.append("non-literal key in %s" % var)
            # var["k"] = expr
            if isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Name) \
                    and tgt.value.id == var and st.value is not None:
                if isinstance(tgt.slice, ast.Constant) and isinstance(tgt.slice.value, str):
                    _add(fwd, tgt.slice.value, st.value, guards)
                else:
                    fwd.opaque.append("computed key into %s" % var)
            # var.update(...) / var.setdefault("k", expr)
            for node in ast.walk(st):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == var):
                    continue
                if node.func.attr == "update" and node.args:
                    arg0 = node.args[0]
                    if isinstance(arg0, ast.Dict):
                        for k, v in zip(arg0.keys, arg0.values):
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                _add(fwd, k.value, v, guards)
                    elif isinstance(arg0, ast.Name) and catchall and arg0.id == catchall:
                        fwd.forwards_catchall = True
                    elif isinstance(arg0, ast.Name):
                        # `internal_kwargs.update(_internal_options)` -- a
                        # pass-through slot. The keys are not visible here; a
                        # subclass fills the dict and hands it down, so the
                        # composition step resolves them.
                        fwd.passthrough.add(arg0.id)
                    else:
                        fwd.opaque.append("%s.update(%s)" % (var, ast.unparse(arg0)))
                elif node.func.attr == "setdefault" and len(node.args) == 2:
                    k = node.args[0]
                    if isinstance(k, ast.Constant) and isinstance(k.value, str):
                        _add(fwd, k.value, node.args[1], guards)

    visit(fn.body, set())


def _add(fwd: Forwarding, key: str, value: ast.AST, guards: set[str]) -> None:
    direct = value.id if isinstance(value, ast.Name) else None
    fwd.dest.append(Dest(key, names_in(value), set(guards), direct,
                         ast.unparse(value), getattr(value, "lineno", 0)))


def analyse_construction(fn: ast.FunctionDef, catchall: str | None,
                         aliases: dict[str, str] | None = None) -> Forwarding:
    fwd = Forwarding()
    call, via = _find_internal_call(fn, aliases)
    if call is None:
        fwd.why_not = "this __init__ builds no internal widget"
        return fwd

    fwd.via = via
    fwd.terminal = fn
    fwd.internal_expr = ast.unparse(call.func)
    for kw in call.keywords:
        if kw.arg is None:
            if isinstance(kw.value, ast.Name):
                if catchall and kw.value.id == catchall:
                    fwd.forwards_catchall = True
                else:
                    fwd.splat_vars.append(kw.value.id)
            else:
                fwd.opaque.append(ast.unparse(kw.value))
        else:
            _add(fwd, kw.arg, kw.value, set())
    for var in fwd.splat_vars:
        _dict_writes(fn, var, catchall, fwd)

    # `for k, v in kwargs.items(): internal_kwargs[k] = v` -- MenuButton merges
    # leftovers with a loop rather than `.update()`. The cross-check arm caught
    # this: static said the leftovers were dropped, and MenuButton actually
    # raises because they reach the internal.
    if catchall:
        for node in ast.walk(fn):
            if not (isinstance(node, ast.For) and isinstance(node.iter, ast.Call)
                    and isinstance(node.iter.func, ast.Attribute)
                    and node.iter.func.attr == "items"
                    and isinstance(node.iter.func.value, ast.Name)
                    and node.iter.func.value.id == catchall):
                continue
            for target, _value in _assignments(node):
                if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name) \
                        and target.value.id in fwd.splat_vars:
                    fwd.forwards_catchall = True

    fwd.understood = True
    return fwd


def _find_super_init(fn: ast.FunctionDef) -> ast.Call | None:
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "__init__"
            and isinstance(node.func.value, ast.Call)
            and isinstance(node.func.value.func, ast.Name)
            and node.func.value.func.id == "super"
        ):
            return node
    return None


def analyse_chain(cls_name: str, classes: dict[str, ast.ClassDef],
                  aliases: dict[str, str], depth: int = 0):
    """Forwarding for `cls_name`, following `super().__init__` when the class
    does not build the internal itself.

    Several families (`Checkbox`/`Switch`/`ToggleButton`, `Radio`, `Row`/`Column`)
    give each subclass its own `__init__` for the Sphinx signature and construct
    the internal in a shared private base. A tool that stops at the subclass
    reports 40-odd parameters as unanalysable.

    Returns (fwd, init_fn, defining_class) with `fwd.dest` expressed in terms of
    `init_fn`'s OWN parameter names.
    """
    init, init_from = find_in_mro(cls_name, classes, _own_init)
    if init is None:
        return None, None, None
    _params, catchall = init_params(init)
    fwd = analyse_construction(init, catchall, aliases)
    if fwd.understood or depth >= 4:
        return fwd, init, init_from

    supercall = _find_super_init(init)
    if supercall is None:
        return fwd, init, init_from

    base = None
    for b in base_names(classes[init_from]):
        cand, _ = find_in_mro(b, classes, _own_init)
        if cand is not None:
            base = b
            break
    if base is None:
        return fwd, init, init_from

    base_fwd, base_init, base_from = analyse_chain(base, classes, aliases, depth + 1)
    if base_fwd is None or not base_fwd.understood:
        return fwd, init, init_from

    base_params, _ = init_params(base_init)
    argmap: dict[str, ast.AST] = {}
    for i, a in enumerate(supercall.args):
        if i < len(base_params):
            argmap[base_params[i]] = a
    for kw in supercall.keywords:
        if kw.arg is not None:
            argmap[kw.arg] = kw.value
        elif isinstance(kw.value, ast.Name) and kw.value.id == catchall:
            fwd.forwards_catchall = fwd.forwards_catchall or base_fwd.forwards_catchall

    composed = Forwarding()
    composed.understood = True
    composed.internal_expr = base_fwd.internal_expr
    composed.splat_vars = list(base_fwd.splat_vars)
    composed.opaque = list(base_fwd.opaque)
    composed.forwards_catchall = base_fwd.forwards_catchall or fwd.forwards_catchall
    composed.terminal = base_fwd.terminal
    composed.via = "super().__init__ -> %s" % base_from

    def translate(base_name_set: set[str]) -> tuple[set[str], str | None]:
        own: set[str] = set()
        only = None
        for bn in base_name_set:
            if bn in argmap:
                sub = names_in(argmap[bn])
                own |= sub
                if isinstance(argmap[bn], ast.Name):
                    only = argmap[bn].id
        return own, only

    for d in base_fwd.dest:
        own_names, direct_own = translate(d.names)
        own_guards, _ = translate(d.guards)
        direct = None
        if d.direct is not None and d.direct in argmap \
                and isinstance(argmap[d.direct], ast.Name):
            direct = argmap[d.direct].id
        elif direct_own is not None and len(d.names) == 1 and d.direct is not None:
            direct = direct_own
        if not own_names and not own_guards:
            continue
        composed.dest.append(Dest(d.key, own_names, own_guards, direct,
                                  "%s  [via %s]" % (d.text, base_from), d.line))

    # Resolve the base's pass-through slots against the dict the subclass fills.
    # `Checkbox` builds a local `options` dict of icon/indicator keys and hands
    # it down as `_internal_options=`, which the base merges wholesale. Without
    # this step those parameters read as "referenced but never forwarded".
    for slot in base_fwd.passthrough:
        arg = argmap.get(slot)
        if not isinstance(arg, ast.Name):
            composed.opaque.append("pass-through slot %r unresolved" % slot)
            continue
        local = Forwarding()
        _dict_writes(init, arg.id, catchall, local)
        for d in local.dest:
            composed.dest.append(Dest(d.key, d.names, d.guards, d.direct,
                                      "%s  [via %s=%s]" % (d.text, slot, arg.id),
                                      d.line))
    return composed, init, init_from


def leftover_policy(fn: ast.FunctionDef, forwards_catchall: bool) -> str:
    """What happens to a name the wrapper does not recognise.

    `_split_layout_kwargs` strips the layout keys in place; whatever is left is
    either forwarded to the internal (where it raises), rejected explicitly, or
    silently discarded. Only the third is mode 3.
    """
    _params, catchall = init_params(fn)
    if not catchall:
        return "no catch-all"
    splits = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "_split_layout_kwargs" for n in ast.walk(fn))
    if not splits:
        return "no split"
    if forwards_catchall:
        return "forwarded"
    for node in ast.walk(fn):
        # `if kwargs: raise` -- a LEFTOVER guard. NOT `if "textsignal" in kwargs:
        # raise`, which rejects one known name and says nothing about the rest.
        # Accepting the looser test credited Select, DateField, NumberField and
        # TimeField with rejecting unknown names; all four construct silently.
        # Measured, not reasoned: see `--arm leftovers`.
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name) \
                and node.test.id == catchall:
            if any(isinstance(n, ast.Raise) for n in ast.walk(node)):
                return "rejected"
    return "dropped"


def local_origins(fn: ast.FunctionDef, params: list[str]) -> dict[str, set[str]]:
    """Map each local name to the parameters its value derives from.

    `ToggleButton` computes `resolved_on = on_icon if on_icon is not None else
    icon` and files THAT into the options dict. Matching on the parameter name
    alone would report `on_icon` and `icon` as never forwarded, which is the
    same false-clean the existing grep produces.
    """
    origins: dict[str, set[str]] = {}
    pset = set(params)
    for _ in range(3):                     # fixpoint; three passes is plenty
        changed = False
        for target, value in _assignments(fn):
            if not isinstance(target, ast.Name):
                continue
            derived: set[str] = set()
            for n in names_in(value):
                if n in pset:
                    derived.add(n)
                elif n in origins:
                    derived |= origins[n]
            if derived and origins.get(target.id) != origins.get(target.id, set()) | derived:
                origins[target.id] = origins.get(target.id, set()) | derived
                changed = True
        if not changed:
            break
    return origins


def expand(names: set[str], origins: dict[str, set[str]], params: set[str]) -> set[str]:
    """Resolve a Dest's name set back to the parameters that fed it."""
    out = {n for n in names if n in params}
    for n in names:
        if n not in params and n in origins:
            out |= origins[n]
    return out


def param_uses(fn: ast.FunctionDef, param: str) -> list[int]:
    """Lines in the body (not the signature) that mention `param`."""
    return sorted({n.lineno for n in ast.walk(fn)
                   if isinstance(n, ast.Name) and n.id == param})


def classify_other_use(fn: ast.FunctionDef, param: str) -> str:
    """Why a parameter that reaches no internal kwarg is still referenced."""
    via_calls: list[str] = []
    stored = False

    # A second widget: several wrappers build a content FRAME beside the widget
    # this audit calls "the internal" (App and Window build the root, then a
    # FlexFrame for content). Those parameters ARE forwarded -- just not to the
    # object the tool measured -- and saying so is the difference between a
    # finding and a false alarm.
    dict_vars: set[str] = set()
    for target, value in _assignments(fn):
        if param not in names_in(value):
            continue
        if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
            dict_vars.add(target.value.id)
        elif isinstance(target, ast.Name) and isinstance(value, ast.Dict):
            dict_vars.add(target.id)
    for target, value in _assignments(fn):
        if isinstance(target, ast.Name) and isinstance(value, ast.Dict):
            for k, v in zip(value.keys, value.values):
                if k is not None and param in names_in(v):
                    dict_vars.add(target.id)
    if dict_vars:
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            for kw in node.keywords:
                if kw.arg is None and isinstance(kw.value, ast.Name) \
                        and kw.value.id in dict_vars:
                    callee = (node.func.id if isinstance(node.func, ast.Name)
                              else ast.unparse(node.func))
                    return "into %s, splatted into %s() -- a SECOND widget, not " \
                           "the internal measured here" % (kw.value.id, callee)

    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            args = list(node.args) + [k.value for k in node.keywords]
            if any(param in names_in(a) for a in args):
                func = node.func
                if isinstance(func, ast.Attribute):
                    owner = ast.unparse(func.value)
                    via_calls.append("%s.%s()" % (owner, func.attr)
                                     if owner in ("self", "self._internal")
                                     else "%s()" % func.attr)
                elif isinstance(func, ast.Name):
                    via_calls.append("%s()" % func.id)
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                        and t.value.id == "self" and param in names_in(node.value):
                    stored = True
    if via_calls:
        uniq = sorted(set(via_calls))
        return "passed to %s" % ", ".join(uniq[:3])
    if stored:
        return "stored on self, never forwarded"
    return "referenced but neither forwarded nor stored"


# --------------------------------------------------------------------------
# the internal side -- resolved at runtime, so the oracle is the real signature
# --------------------------------------------------------------------------

def resolve_internal(expr: str, aliases: dict[str, str], internal_cls_name: str | None):
    """Import the internal class the wrapper builds. Returns (cls, note)."""
    name = expr
    if name.startswith("self."):
        if internal_cls_name is None:
            return None, "self._internal_class is not bound in this module"
        name = internal_cls_name
    dotted = aliases.get(name)
    if dotted is None:
        return None, "no import binds %r in this module" % name
    mod_path, _, attr = dotted.rpartition(".")
    try:
        mod = importlib.import_module(mod_path)
    except ImportError as exc:
        return None, "import %s failed: %s" % (mod_path, exc)
    cls = getattr(mod, attr, None)
    if cls is None:
        return None, "%s has no attribute %r" % (mod_path, attr)
    return cls, ""


_UNPACK = __import__("re").compile(r"Unpack\[\s*([A-Za-z_][A-Za-z0-9_]*)\s*\]")


def internal_signature(cls) -> tuple[set[str], bool, str]:
    """What the internal accepts: (names, still open-ended, note).

    Naming the parameters is not enough. The internals take
    `**kwargs: Unpack[SomeKwargs]` and declare their real vocabulary in that
    TypedDict -- `OptionMenu` names four parameters and accepts twenty-four.
    A tool reading only the signature concludes every destination key is
    unrecognised, and then has to disable the check entirely to avoid drowning
    in false alarms. Resolving the TypedDict (which merges its bases' keys at
    class creation) turns the destination check back on.
    """
    names: set[str] = set()
    var_kw = False
    open_ended = False
    # Union the WHOLE mro, not just this class. `TimeEntry` names eight
    # parameters and hands the rest to `Field`, which is where `readonly` is
    # accepted -- a first pass read only the leaf class and reported
    # `TimeField(read_only=True)` as writing a key nothing accepts. It works;
    # the tool was wrong. A vocabulary that stops at the leaf manufactures
    # false alarms in exactly the wrappers that delegate most.
    for klass in getattr(cls, "__mro__", [cls]):
        init = klass.__dict__.get("__init__")
        if init is None:
            continue
        try:
            sig = inspect.signature(init)
        except (ValueError, TypeError) as exc:
            return set(), True, "signature unavailable: %s" % exc
        for p in sig.parameters.values():
            if p.name == "self":
                continue
            if p.kind is inspect.Parameter.VAR_KEYWORD:
                var_kw = True
                ann = p.annotation
                match = _UNPACK.search(ann if isinstance(ann, str) else "")
                resolved = False
                if match:
                    mod = sys.modules.get(klass.__module__)
                    td = getattr(mod, match.group(1), None) if mod else None
                    keys = getattr(td, "__annotations__", None)
                    if keys:
                        names |= set(keys)
                        resolved = True
                if not resolved:
                    open_ended = True
            elif p.kind is not inspect.Parameter.VAR_POSITIONAL:
                names.add(p.name)
    note = "" if not var_kw else (
        "vocabulary is the union over the internal's mro"
        if not open_ended
        else "some class in the mro takes an unannotated **kwargs -- the "
             "vocabulary is open-ended and destinations are NOT checked")
    return names, open_ended, note


# --------------------------------------------------------------------------
# mode 5 -- an annotation that cannot be produced
# --------------------------------------------------------------------------

def _getattr_none_property(fn: ast.FunctionDef):
    """`@property def x(self) -> T | None: return getattr(self._internal, 'a', None)`"""
    if not any(isinstance(d, ast.Name) and d.id == "property" for d in fn.decorator_list):
        return None
    ann = ast.unparse(fn.returns) if fn.returns is not None else ""
    if "None" not in ann:
        return None
    body = [n for n in fn.body
            if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return None
    call = body[0].value
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
            and call.func.id == "getattr" and len(call.args) == 3):
        return None
    obj, attr, default = call.args
    if not (isinstance(obj, ast.Attribute) and obj.attr == "_internal"):
        return None
    if not (isinstance(attr, ast.Constant) and isinstance(attr.value, str)):
        return None
    if not (isinstance(default, ast.Constant) and default.value is None):
        return None
    return ann.strip('"\''), attr.value, fn.lineno


def internal_can_be_absent(internal, attr: str) -> tuple[str, str]:
    """Can `getattr(internal, attr, None)` ever fall through to the default?"""
    if internal is None:
        return "UNKNOWN", "internal class unresolved"
    member = inspect.getattr_static(internal, attr, None)
    if member is None:
        return "OK", ("the internal has no class-level %r, so the instance "
                      "attribute may legitimately be absent" % attr)
    if isinstance(member, property):
        try:
            src = inspect.getsource(member.fget)
        except (OSError, TypeError) as exc:
            return "UNKNOWN", "property source unavailable: %s" % exc
        # A property ALWAYS resolves, so the getattr default is dead. The only
        # way the wrapper can still answer None is the property itself doing so.
        if "return None" in src or "or None" in src:
            return "OK", "the internal property has a `return None` path"
        return "DEAD-DEFAULT", (
            "the internal defines %r as a property with no None path, so the "
            "getattr default is unreachable and `| None` cannot occur" % attr)
    return "OK", "the internal binds %r as %s" % (attr, type(member).__name__)


# --------------------------------------------------------------------------
# the scan
# --------------------------------------------------------------------------

MODE_NAMES = {
    1: "never forwarded",
    2: "wrong destination",
    3: "swallowed as a layout key",
    5: "the type lies",
}


def public_names() -> set[str]:
    """Names the framework actually exports, resolved at runtime."""
    names: set[str] = set()
    try:
        import bootstack
        names |= set(getattr(bootstack, "__all__", []))
        import bootstack.widgets as _w
        names |= set(getattr(_w, "__all__", []))
        import bootstack.dialogs as _d
        names |= set(getattr(_d, "__all__", []))
    except ImportError as exc:
        print("WARNING: could not import bootstack to resolve the export list "
              "(%s); falling back to name-based publicity" % exc)
    return names


def scan(src: Path) -> dict:
    trees, failures = load_module_asts(src)
    found = len(list(src.glob("*.py")))
    exported = public_names()

    rows: list[dict] = []
    skipped: list[tuple[str, str]] = []
    mode5: list[dict] = []
    idioms: dict[str, int] = {}

    def bump(key: str) -> None:
        idioms[key] = idioms.get(key, 0) + 1

    for module, tree in sorted(trees.items()):
        aliases = import_alias_map(tree)
        classes = classes_of(tree)

        for cname in sorted(classes):
            if cname.startswith("_"):
                continue
            if exported and cname not in exported:
                skipped.append(("%s.%s" % (module, cname), "not in a public __all__"))
                continue

            fwd, init, init_from = analyse_chain(cname, classes, aliases)
            if init is None:
                skipped.append(("%s.%s" % (module, cname),
                                "no __init__ in this module's class graph"))
                continue
            params, catchall = init_params(init)
            icname, _ = find_in_mro(cname, classes, _own_internal_class)
            inherited = None if init_from == cname else init_from

            internal, note = (None, "")
            if fwd.understood and fwd.internal_expr:
                internal, note = resolve_internal(fwd.internal_expr, aliases, icname)

            base = {"module": module, "class": cname, "inherited_init": inherited,
                    "via": fwd.via}

            if not fwd.understood:
                bump("UNANALYZED: %s" % fwd.why_not)
                for pname in params:
                    if pname in ("parent", "master"):
                        continue
                    uses = param_uses(init, pname)
                    rows.append(dict(base, param=pname, dest="-",
                                     verdict="UNANALYZED" if uses else "UNUSED",
                                     mode=None if uses else 1, note=fwd.why_not))
                continue

            bump("understood: %s%s" % (
                "direct keywords" if not fwd.splat_vars
                else "dict splat (%s)" % ",".join(fwd.splat_vars),
                " via super()" if fwd.via else ""))
            isig, ivar_kw, isig_note = (internal_signature(internal) if internal
                                        else (set(), True, note))

            pset = set(params)
            origins = local_origins(init, params)
            if fwd.terminal is not None and fwd.terminal is not init:
                for k, v in local_origins(fwd.terminal, params).items():
                    origins[k] = origins.get(k, set()) | v
            for d in fwd.dest:
                d.names = expand(d.names, origins, pset) | (d.names & pset)
                d.guards = expand(d.guards, origins, pset) | (d.guards & pset)

            for pname in params:
                if pname in ("parent", "master"):
                    continue
                by_value = [d for d in fwd.dest if pname in d.names]
                by_guard = [d for d in fwd.dest if pname in d.guards and pname not in d.names]
                uses = param_uses(init, pname)

                if not by_value and not by_guard:
                    if not uses:
                        rows.append(dict(base, param=pname, dest="-", verdict="UNUSED",
                                         mode=1,
                                         note="the name appears nowhere in the "
                                              "__init__ body"))
                    else:
                        rows.append(dict(base, param=pname, dest="-",
                                         verdict="USED-ELSEWHERE", mode=None,
                                         note=classify_other_use(init, pname)))
                    continue

                for d in by_value:
                    direct = d.direct == pname
                    if d.key == pname:
                        verdict, mode = ("FORWARDED" if direct
                                         else "FORWARDED-TRANSFORMED"), None
                    else:
                        verdict, mode = ("RENAMED" if direct
                                         else "RENAMED-TRANSFORMED"), 2
                    why = isig_note
                    if internal is not None and not ivar_kw and d.key not in isig:
                        verdict, mode = "DEST-NOT-A-PARAM", 2
                        why = "the internal %s does not accept %r" % (
                            internal.__name__, d.key)
                    # THE RANKING SIGNAL. A rename is ordinary (`max_value` ->
                    # `maxvalue`). A rename is SUSPECT when the internal also
                    # has a parameter of the wrapper's own name -- the wrapper
                    # had that slot available and passed it over. That is
                    # exactly the shape of #458 and #461: `signal` existed on
                    # the internal and the wrapper wrote `textsignal`.
                    collision = (internal is not None and mode == 2
                                 and pname in isig and d.key != pname)
                    if collision:
                        why = ("the internal %s ALSO has a %r parameter and the "
                               "wrapper writes %r instead" % (
                                   internal.__name__, pname, d.key))
                    rows.append(dict(base, param=pname, dest=d.key, verdict=verdict,
                                     mode=mode, expr=d.text, line=d.line, note=why,
                                     collision=collision))

                for d in by_guard:
                    why = isig_note
                    verdict, mode = "CONDITIONAL", None
                    if internal is not None and not ivar_kw and d.key not in isig:
                        verdict, mode = "DEST-NOT-A-PARAM", 2
                        why = "the internal %s does not accept %r" % (
                            internal.__name__, d.key)
                    rows.append(dict(base, param=pname, dest=d.key, verdict=verdict,
                                     mode=mode, expr="if %s: -> %s=%s" % (
                                         pname, d.key, d.text),
                                     line=d.line, note=why))

            # mode 3 -- unknown names silently dropped
            if catchall:
                policy = leftover_policy(fwd.terminal or init, fwd.forwards_catchall)
                if policy == "dropped":
                    rows.append(dict(base, param="**%s" % catchall, dest="-",
                                     verdict="LEFTOVERS-DROPPED", mode=3,
                                     note="_split_layout_kwargs() strips the layout "
                                          "keys and nothing reads what is left, so "
                                          "an unknown name is accepted silently"))
                else:
                    rows.append(dict(base, param="**%s" % catchall, dest="-",
                                     verdict="LEFTOVERS-" + policy.upper(),
                                     mode=None, note="unknown-name policy: %s" % policy))

            # mode 5 -- resolved against the internal this class actually builds
            prop, prop_from = find_in_mro(
                cname, classes,
                lambda c: next((_getattr_none_property(f) for f in c.body
                                if isinstance(f, ast.FunctionDef)
                                and _getattr_none_property(f) is not None), None))
            if prop is not None:
                ann, attr, line = prop
                verdict, why = internal_can_be_absent(internal, attr)
                mode5.append({"module": module, "class": cname, "property": "signal",
                              "annotation": ann, "internal_attr": attr, "line": line,
                              "verdict": verdict, "why": why,
                              "defined_on": None if prop_from == cname else prop_from})

    # DIVERGENCE -- the ranking signal that actually separates #458/#461 from a
    # cosmetic rename. `max_value -> maxvalue` is one public name landing on one
    # internal key everywhere it appears; nobody has to look at it. A public
    # name that lands on DIFFERENT internal keys in different wrappers means the
    # family disagrees with itself, and that is where both #458 and #461 lived
    # (`signal` -> `signal` on the boolean controls, `signal` -> `textsignal` on
    # SelectButton). It is also the mechanical form of what #460 and #369
    # describe: a family decision nobody made.
    # Value flows only. A guard-driven write (`if icon_only: kw['compound']=...`)
    # says nothing about where `icon_only` is stored, and counting it made
    # `text`, `image` and `icon` all look divergent because Label guards one
    # `compound` write with several of them.
    VALUE_FLOW = {"FORWARDED", "FORWARDED-TRANSFORMED", "RENAMED",
                  "RENAMED-TRANSFORMED", "DEST-NOT-A-PARAM"}
    div: dict[str, dict[str, list[str]]] = {}
    for r in rows:
        dest = r.get("dest")
        if r["verdict"] not in VALUE_FLOW:
            continue
        if dest and dest != "-" and not r["param"].startswith("**"):
            div.setdefault(r["param"], {}).setdefault(dest, []).append(
                "%s.%s" % (r["module"], r["class"]))
    divergent = {p: m for p, m in div.items() if len(m) > 1}
    for r in rows:
        r["divergent"] = r["param"] in divergent

    return {"rows": rows, "skipped": skipped, "mode5": mode5, "idioms": idioms,
            "divergent": divergent,
            "files_found": found, "files_parsed": len(trees), "failures": failures,
            "src": str(src)}


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def report(res: dict, verbose: bool = False) -> None:
    rows = res["rows"]
    print("=" * 78)
    print("WRAPPER / INTERNAL PARAMETER DELTA -- #463")
    print("=" * 78)
    print("src             : %s" % res["src"])
    print("files found     : %d" % res["files_found"])
    print("files parsed    : %d" % res["files_parsed"])
    if res["failures"]:
        print("PARSE FAILURES  : %d  <-- the scan is INCOMPLETE" % len(res["failures"]))
        for f in res["failures"]:
            print("   %s" % f)
    else:
        print("parse failures  : 0")
    assert res["files_parsed"] + len(res["failures"]) == res["files_found"], (
        "files_parsed + failures != files_found -- files vanished silently")

    classes = sorted({(r["module"], r["class"]) for r in rows})
    params = sorted({(r["module"], r["class"], r["param"]) for r in rows
                     if not r["param"].startswith("**")})
    print("classes analysed: %d" % len(classes))
    print("distinct params : %d" % len(params))
    print()

    print("IDIOMS -- what the tool understands, and therefore what it can speak about")
    print("-" * 78)
    for k, v in sorted(res["idioms"].items(), key=lambda kv: (-kv[1], kv[0])):
        print("  %4d  %s" % (v, k))
    print()

    def line_for(r: dict) -> str:
        inh = ""
        if r.get("via"):
            inh = "  [%s]" % r["via"]
        elif r.get("inherited_init"):
            inh = "  (init from %s)" % r["inherited_init"]
        return "  %-26s %-20s -> %-22s %s%s" % (
            "%s.%s" % (r["module"], r["class"]), r["param"], r.get("dest", "-"),
            r["verdict"], inh)

    for mode in (2, 1, 3):
        hits = [r for r in rows if r.get("mode") == mode]
        print("MODE %d -- %s : %d" % (mode, MODE_NAMES[mode], len(hits)))
        print("-" * 78)
        if mode == 2:
            top = [r for r in hits if r.get("divergent") or r.get("collision")]
            rest = [r for r in hits if not (r.get("divergent") or r.get("collision"))]
            print("  RANK A -- the public name lands on a DIFFERENT internal key in")
            print("            some other wrapper: the family disagrees : %d" % len(top))
            print("            (this is the shape of #458 and #461)")
            for r in sorted(top, key=lambda r: (r["param"], r["module"], r["class"])):
                print(line_for(r))
            print()
            print("  RANK B -- one public name, one internal key everywhere it")
            print("            appears: a consistent rename : %d" % len(rest))
            hits = rest
        for r in sorted(hits, key=lambda r: (r["module"], r["class"], r["param"])):
            print(line_for(r))
            if verbose and r.get("expr"):
                print("        expr: %s   (line %s)" % (r["expr"], r.get("line")))
            if verbose and r.get("note"):
                print("        %s" % r["note"])
        print()

    print("UNKNOWN-NAME POLICY -- what each wrapper does with a keyword it does")
    print("not recognise (cross-checked against real construction by --arm leftovers)")
    print("-" * 78)
    pol: dict[str, list[str]] = {}
    for r in rows:
        if r["param"].startswith("**"):
            pol.setdefault(r["verdict"].replace("LEFTOVERS-", ""), []).append(r["class"])
    for k in sorted(pol, key=lambda k: -len(pol[k])):
        print("  %-10s %3d  %s" % (k, len(pol[k]), ", ".join(sorted(pol[k])[:8])
                                   + ("" if len(pol[k]) <= 8 else " ...")))
    if "REJECTED" in pol:
        print()
        print("  The %d REJECTED wrappers are the precedent #383 gap 3 needs: the"
              % len(pol["REJECTED"]))
        print("  guard already exists in this codebase and is six lines long.")
    print()

    m5 = [f for f in res["mode5"] if f["verdict"] == "DEAD-DEFAULT"]
    other = [f for f in res["mode5"] if f["verdict"] != "DEAD-DEFAULT"]
    print("MODE 5 -- %s : %d" % (MODE_NAMES[5], len(m5)))
    print("-" * 78)
    for f in sorted(m5, key=lambda f: (f["module"], f["class"])):
        where = "" if not f["defined_on"] else "  (property on %s)" % f["defined_on"]
        print("  %-26s .%-8s %-22s line %d%s" % (
            "%s.%s" % (f["module"], f["class"]), f["property"], f["annotation"],
            f["line"], where))
        if verbose:
            print("        %s" % f["why"])
    if other:
        print("  -- checked and CLEARED (the None is reachable):")
        for f in sorted(other, key=lambda f: (f["module"], f["class"])):
            print("     %-26s %-14s %s" % (
                "%s.%s" % (f["module"], f["class"]), f["verdict"], f["why"]))
    print()

    print("DIVERGENCE -- one public name, more than one internal destination : %d"
          % len(res["divergent"]))
    print("-" * 78)
    print("  Read this list first. A name here means the wrapper family does not")
    print("  agree on where the parameter goes; #458 and #461 are both instances.")
    for pname in sorted(res["divergent"]):
        dests = res["divergent"][pname]
        print("  %-20s %d destinations" % (pname, len(dests)))
        for key in sorted(dests):
            who = sorted(set(dests[key]))
            print("      -> %-22s %s%s" % (
                key, ", ".join(w.split(".")[-1] for w in who[:5]),
                "" if len(who) <= 5 else " (+%d more)" % (len(who) - 5)))
    print()

    cond = [r for r in rows if r["verdict"] == "CONDITIONAL"]
    print("CONDITIONAL -- forwarded by a guard, not by value : %d" % len(cond))
    print("-" * 78)
    if verbose:
        for r in sorted(cond, key=lambda r: (r["module"], r["class"], r["param"])):
            print("  %-26s %s" % ("%s.%s" % (r["module"], r["class"]), r["expr"]))
    else:
        seen: dict[str, list[str]] = {}
        for r in cond:
            seen.setdefault("%s -> %s" % (r["param"], r["dest"]), []).append(r["class"])
        for k in sorted(seen):
            print("  %-34s %d class(es): %s" % (
                k, len(seen[k]), ", ".join(sorted(set(seen[k]))[:6])))
    print()

    unan = [r for r in rows if r["verdict"] == "UNANALYZED"]
    if unan:
        byclass: dict[str, int] = {}
        for r in unan:
            key = "%s.%s" % (r["module"], r["class"])
            byclass[key] = byclass.get(key, 0) + 1
        print("UNANALYZED -- the tool CANNOT speak about these; do NOT read as clean")
        print("-" * 78)
        for k, v in sorted(byclass.items()):
            note = next(r["note"] for r in unan
                        if "%s.%s" % (r["module"], r["class"]) == k)
            print("  %-28s %3d params   (%s)" % (k, v, note))
        print()

    triage = [r for r in rows if r["verdict"] == "USED-ELSEWHERE"]
    print("USED-ELSEWHERE -- reaches no internal kwarg; needs a human : %d" % len(triage))
    print("-" * 78)
    for r in sorted(triage, key=lambda r: (r["module"], r["class"], r["param"])):
        print("  %-26s %-20s %s" % (
            "%s.%s" % (r["module"], r["class"]), r["param"], r["note"]))
    print()

    print("MODE 4 -- accepted then ignored : NOT MEASURED BY THIS ARM")
    print("-" * 78)
    print("  Mode 4 is not statically decidable and this probe does not claim to")
    print("  find it. `--arm roundtrip` is a PARTIAL heuristic; read its own")
    print("  honesty note before quoting it.")
    print()

    print("SKIPPED CLASSES : %d" % len(res["skipped"]))
    print("-" * 78)
    if verbose:
        for name, why in res["skipped"]:
            print("  %-38s %s" % (name, why))
    else:
        reasons: dict[str, int] = {}
        for _, why in res["skipped"]:
            reasons[why] = reasons.get(why, 0) + 1
        for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]):
            print("  %4d  %s" % (v, k))


# --------------------------------------------------------------------------
# controls -- a probe that finds nothing must be proven able to find something
# --------------------------------------------------------------------------

def materialize(commit: str, src_rel: str) -> Path:
    """Write `src_rel` at `commit` into a temp dir. Portable: git show only."""
    out = Path(tempfile.mkdtemp(prefix="wrapdelta_"))
    listing = subprocess.check_output(
        ["git", "ls-tree", "--name-only", commit, src_rel.replace("\\", "/") + "/"]
    ).decode("utf-8").split()
    for rel in listing:
        if not rel.endswith(".py"):
            continue
        blob = subprocess.check_output(["git", "show", "%s:%s" % (commit, rel)])
        (out / Path(rel).name).write_bytes(blob)
    return out


PRE_458 = "1f9a62d1^"    # parent of the #458 fix -- the last commit with the defect


def control(src: Path) -> int:
    """The four known positives. Three are OPEN on main and must be FOUND;
    #458 is FIXED and must appear at the pre-fix commit and NOT on main."""
    print("=" * 78)
    print("NON-VACUITY CONTROLS")
    print("=" * 78)
    failures = 0
    res = scan(src)
    rows = res["rows"]

    def has(cls: str, param: str, mode: int, dest: str | None = None) -> bool:
        return any(
            r["class"] == cls and r["param"] == param and r.get("mode") == mode
            and (dest is None or r.get("dest") == dest)
            for r in rows
        )

    dead = [f["class"] for f in res["mode5"] if f["verdict"] == "DEAD-DEFAULT"]
    checks = [
        ("#461   SelectButton signal= -> textsignal= (mode 2, OPEN)",
         has("SelectButton", "signal", 2, "textsignal"), True),
        ("#460   .signal annotated `| None` it cannot return (mode 5, OPEN)",
         len(dead) >= 8, True),
        ("#383g3 TextField accepts an unknown name silently (mode 3, OPEN)",
         has("TextField", "**kwargs", 3), True),
        ("#458   Select signal= -> textsignal= (mode 2, FIXED on main)",
         has("Select", "signal", 2, "textsignal"), False),
    ]
    for label, got, want in checks:
        ok = got == want
        failures += 0 if ok else 1
        print("  [%s] %-58s found=%-5s want=%s" % (
            "PASS" if ok else "FAIL", label, got, want))
    print("         (#460 names EIGHT widgets; this scan finds %d: %s)" % (
        len(dead), ", ".join(sorted(dead))))

    print()
    print("  #458 is the strongest control available -- a real instance of the")
    print("  exact mode the tool exists to catch, with a known before and after.")
    print("  The same scan run against the pre-fix commit MUST find it:")
    print()
    # `1f9a62d1` is the fix ("fix(select): bind signal= to the option's value,
    # not the entry text (#458)"); its parent is the last commit carrying the
    # defect. NOT `main~` -- main~ is two docs commits after the merge, and a
    # first pass used it and got a false PASS-shaped FAIL. The commit that
    # bounds a control has to be the one the defect actually lived in.
    try:
        old = materialize(PRE_458, "src/bootstack/widgets")
        old_res = scan(old)
        found_old = any(
            r["class"] == "Select" and r["param"] == "signal"
            and r.get("mode") == 2 and r.get("dest") == "textsignal"
            for r in old_res["rows"]
        )
        failures += 0 if found_old else 1
        print("  [%s] %-58s found=%-5s want=True" % (
            "PASS" if found_old else "FAIL",
            "#458 at %s (the pre-fix commit)" % PRE_458,
            found_old))
        print("        (%d files parsed there, parse failures: %d)" % (
            old_res["files_parsed"], len(old_res["failures"])))
    except (subprocess.CalledProcessError, OSError) as exc:
        failures += 1
        print("  [FAIL] could not materialize %s: %s" % (PRE_458, exc))

    print()
    print("CONTROLS: %s" % (
        "ALL PASS -- a null result from this tool is meaningful" if failures == 0
        else "%d FAILED -- do NOT trust a null result" % failures))
    return failures


# --------------------------------------------------------------------------
# mode 4 heuristic -- runtime, and honest about what it cannot see
# --------------------------------------------------------------------------

ROUNDTRIP_LIMITS = """
  WHAT THIS ARM DOES: constructs each wrapper with one non-default value for a
  parameter that has a same-named public property, then reads the property back.
  A disagreement is a mode-4 CANDIDATE.

  WHAT IT CANNOT SEE, stated up front so a null result is not over-read:
    * #453 -- the defect this mode is named for -- WOULD NOT BE CAUGHT. The
      wrapper's own `read_only` property answered True for every Select; the
      only honest observable was the inner entry's ttk state. A property that
      echoes the stored setting cannot witness the setting being ignored.
    * A parameter with no same-named property is not tested at all.
    * A widget that will not construct headless is SKIPPED, not cleared.
"""


def roundtrip(src: Path) -> int:
    print("=" * 78)
    print("MODE 4 ROUNDTRIP HEURISTIC")
    print("=" * 78)
    print(ROUNDTRIP_LIMITS)
    try:
        import bootstack as bs
    except ImportError as exc:
        print("  SKIP: bootstack did not import (%s)" % exc)
        return 0

    res = scan(src)
    classes = sorted({r["class"] for r in res["rows"]})
    try:
        app = bs.App(title="probe")
    except Exception as exc:                    # noqa: BLE001 -- reported, not hidden
        print("  SKIP: no display / App would not build (%s: %s)"
              % (type(exc).__name__, exc))
        return 0

    checked = mismatched = skipped = 0
    findings = []
    with app:
        for cname in classes:
            cls = getattr(bs, cname, None)
            if cls is None:
                continue
            try:
                sig = inspect.signature(cls.__init__)
            except (ValueError, TypeError):
                continue
            for pname, p in sig.parameters.items():
                if pname in ("self", "parent") or p.kind in (
                        inspect.Parameter.VAR_KEYWORD,
                        inspect.Parameter.VAR_POSITIONAL):
                    continue
                if not isinstance(inspect.getattr_static(cls, pname, None), property):
                    continue
                default = p.default
                if isinstance(default, bool):
                    probe_val = not default
                elif isinstance(default, str):
                    probe_val = "probe" if default != "probe" else "other"
                elif isinstance(default, int):
                    probe_val = 7 if default != 7 else 9
                else:
                    skipped += 1
                    continue
                try:
                    widget = cls(**{pname: probe_val})
                    got = getattr(widget, pname)
                except Exception:               # noqa: BLE001 -- construction refused
                    skipped += 1
                    continue
                checked += 1
                if got != probe_val:
                    mismatched += 1
                    findings.append((cname, pname, probe_val, got))
    print("  checked=%d  mismatched=%d  skipped=%d" % (checked, mismatched, skipped))
    for cname, pname, sent, got in findings:
        print("    %-20s %-20s sent=%r read back=%r" % (cname, pname, sent, got))
    return 0


BOGUS = "bogus_zzz_probe"


def leftovers(src: Path) -> int:
    """Cross-check the static mode-3 verdict against what actually happens.

    Constructs every wrapper with an unknown keyword and records whether it
    raises. The static pass reads the source; this reads the behaviour. A
    disagreement is a TOOL defect, and the first run of this arm found two --
    `Select` and `DateField` were credited with rejecting unknown names because
    they carry an `if "textsignal" in kwargs: raise` guard, which rejects one
    known name and says nothing about the rest.
    """
    print("=" * 78)
    print("MODE 3 CROSS-CHECK -- static verdict vs actual construction")
    print("=" * 78)
    try:
        import bootstack as bs
    except ImportError as exc:
        print("  SKIP: bootstack did not import (%s)" % exc)
        return 0

    res = scan(src)
    static = {r["class"]: r["verdict"] for r in res["rows"]
              if r["param"].startswith("**")}
    try:
        app = bs.App(title="probe")
    except Exception as exc:                    # noqa: BLE001 -- reported, not hidden
        print("  SKIP: no display / App would not build (%s: %s)"
              % (type(exc).__name__, exc))
        return 0

    agree = disagree = inconclusive = 0
    problems = []
    with app:
        for cname, verdict in sorted(static.items()):
            cls = getattr(bs, cname, None)
            if cls is None:
                continue
            try:
                cls(**{BOGUS: 1})
                actual = "dropped"
            except TypeError as exc:
                actual = "rejected" if BOGUS in str(exc) else "inconclusive"
            except Exception as exc:            # noqa: BLE001 -- classified below
                actual = ("rejected" if BOGUS in str(exc) else "inconclusive")
            expected = verdict.replace("LEFTOVERS-", "").lower()
            if actual == "inconclusive":
                inconclusive += 1
                continue
            if (actual == "dropped") == (expected == "dropped"):
                agree += 1
            else:
                disagree += 1
                problems.append((cname, expected, actual))
    print("  agree=%d  DISAGREE=%d  inconclusive=%d" % (agree, disagree, inconclusive))
    for cname, expected, actual in problems:
        print("    %-22s static says %-10s actually %s" % (cname, expected, actual))
    print()
    print("  A disagreement here is a defect in THIS PROBE, not in the wrapper.")
    return 1 if disagree else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="wrapper/internal parameter delta (#463)")
    ap.add_argument("--arm", choices=("scan", "control", "roundtrip", "leftovers"), default="scan")
    ap.add_argument("--src", default="src/bootstack/widgets")
    ap.add_argument("--from-commit", default=None,
                    help="scan the sources as of this commit instead of the worktree")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.from_commit:
        src = materialize(args.from_commit, args.src)
        print("(scanning %s as of %s -> %s)" % (args.src, args.from_commit, src))
    else:
        src = Path(args.src)
    if not src.is_dir():
        print("no such directory: %s" % src)
        return 2

    if args.arm == "control":
        return 1 if control(src) else 0
    if args.arm == "roundtrip":
        return roundtrip(src)
    if args.arm == "leftovers":
        return leftovers(src)
    report(scan(src), verbose=args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
