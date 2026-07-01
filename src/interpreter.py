"""CP+* Interpreter - Full-featured AST Execution Engine"""
import sys
import os
import re
import math
import random
import time as time_module
import threading
import queue
from typing import Any, Dict, List, Tuple, Optional

from parser import (
    Program, VarDecl, FnDef, ClassDef, TraitDef, ImplBlock, StructDef,
    ReturnStmt, IfStmt, ForStmt, WhileStmt, MatchStmt, MatchArm,
    BreakStmt, ContinueStmt, PanicStmt, GoStmt, AwaitExpr,
    FnCall, MethodCall, FieldAccess, IndexAccess, StaticCall,
    VarRef, Literal, BinaryOp, UnaryOp, Assign,
    ListLiteral, MapLiteral, TupleLiteral,
    SelfRef, OwnershipExpr,
    ResultOk, ResultErr,
    TryCatch, MacroInvoke, ReflectExpr,
    PipeStmt, PipeExpr, OverrideDecl,
    ModuleDecl, ImportStmt, ExportStmt,
    WildcardPattern, LiteralPattern, BindingPattern,
    TuplePattern, RangePattern, OrPattern,
)


# ─── Runtime exceptions ──────────────────────────────────────────────────────

class ReturnException(Exception):
    def __init__(self, value): self.value = value

class BreakException(Exception): pass
class ContinueException(Exception): pass

class CPPSPanic(Exception):
    def __init__(self, msg): self.msg = msg; super().__init__(msg)

class CPPSError(Exception):
    """Runtime error with message"""
    def __init__(self, msg): self.msg = msg; super().__init__(msg)


# ─── Runtime value types ─────────────────────────────────────────────────────

class CPPSResult:
    """Result<T, E>"""
    def __init__(self, ok: bool, value):
        self.ok = ok
        self.value = value

    def __repr__(self):
        if self.ok:
            return f"Ok({self.value!r})"
        return f"Err({self.value!r})"

    def is_ok(self): return self.ok
    def is_err(self): return not self.ok
    def unwrap(self):
        if self.ok: return self.value
        raise CPPSPanic(f"Called unwrap() on Err: {self.value}")
    def unwrap_or(self, default): return self.value if self.ok else default


class CPPSChannel:
    """Channel<T> for concurrency"""
    def __init__(self, capacity=0):
        self.q = queue.Queue(maxsize=capacity)

    def send(self, val): self.q.put(val)
    def recv(self): return self.q.get()
    def try_recv(self):
        try: return CPPSResult(True, self.q.get_nowait())
        except queue.Empty: return CPPSResult(False, "empty")
    def len(self): return self.q.qsize()


class CPPSInstance:
    """Runtime instance of a class"""
    def __init__(self, class_name, fields=None):
        self.class_name = class_name
        self.fields: Dict[str, Any] = fields or {}

    def get(self, name): return self.fields.get(name)
    def set(self, name, val): self.fields[name] = val

    def __repr__(self):
        fields_str = ', '.join(f"{k}={v!r}" for k, v in self.fields.items())
        return f"{self.class_name}{{{fields_str}}}"


class CPPSOwned:
    """Ownership wrapper"""
    def __init__(self, kind, value, lifetime=None):
        self.kind = kind        # own | share | borrow
        self.value = value
        self.lifetime = lifetime
        self._moved = False

    def borrow(self):
        return self.value

    def move(self):
        if self._moved:
            raise CPPSError(f"Value already moved (use-after-move)")
        self._moved = True
        return self.value

    def __repr__(self):
        return f"{self.kind}<{self.value!r}>"


class CPPSClosure:
    """Function value (first-class functions)"""
    def __init__(self, fn_def, captured_env):
        self.fn_def = fn_def
        self.captured_env = captured_env


# ─── Environment (scope chain) ───────────────────────────────────────────────

class Env:
    def __init__(self, parent=None):
        self.vars: Dict[str, Any] = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def set(self, name, val):
        self.vars[name] = val

    def assign(self, name, val):
        """Assign to existing binding, walking scope chain."""
        if name in self.vars:
            self.vars[name] = val
            return True
        if self.parent:
            return self.parent.assign(name, val)
        self.vars[name] = val
        return True

    def child(self):
        return Env(parent=self)


# ─── Standard library ────────────────────────────────────────────────────────

class StdLib:
    """CP+* standard library implementation"""

    @staticmethod
    def io_println(template, *args):
        s = str(template)
        for a in args:
            s = s.replace('{}', _display(a), 1)
        print(s)

    @staticmethod
    def io_print(template, *args):
        s = str(template)
        for a in args:
            s = s.replace('{}', _display(a), 1)
        print(s, end='')

    @staticmethod
    def io_input(prompt=''):
        return input(str(prompt) if prompt else '')

    @staticmethod
    def io_eprintln(msg):
        print(str(msg), file=sys.stderr)


def _display(v) -> str:
    if v is None: return "none"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, float) and v == int(v): return str(int(v))
    if isinstance(v, list): return "[" + ", ".join(_display(x) for x in v) + "]"
    if isinstance(v, dict): return "{" + ", ".join(f"{k}: {_display(w)}" for k, w in v.items()) + "}"
    if isinstance(v, tuple): return "(" + ", ".join(_display(x) for x in v) + ")"
    if isinstance(v, CPPSResult): return repr(v)
    if isinstance(v, CPPSInstance): return repr(v)
    if isinstance(v, CPPSOwned): return repr(v)
    if isinstance(v, CPPSChannel): return f"Channel(len={v.len()})"
    return str(v)


# ─── Interpreter ─────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.global_env = Env()
        self.classes: Dict[str, ClassDef] = {}
        self.structs: Dict[str, StructDef] = {}
        self.traits: Dict[str, TraitDef] = {}
        self.impls: Dict[str, Dict] = {}  # class_name -> {method_name: FnDef}
        self.modules: Dict[str, Dict] = {}
        self.current_module = None
        self._setup_stdlib()
        self._go_threads: List[threading.Thread] = []

    # ── Standard library bootstrap ───────────────────────────────────────────

    def _setup_stdlib(self):
        env = self.global_env

        # io namespace
        env.set('io', {
            'println': lambda *a: StdLib.io_println(*a),
            'print': lambda *a: StdLib.io_print(*a),
            'input': lambda p='': StdLib.io_input(p),
            'eprintln': lambda m: StdLib.io_eprintln(m),
        })

        # math namespace
        env.set('math', {
            'sqrt': math.sqrt, 'pow': math.pow, 'abs': abs,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log2': math.log2, 'log10': math.log10,
            'exp': math.exp, 'floor': math.floor, 'ceil': math.ceil,
            'round': round, 'min': min, 'max': max,
            'PI': math.pi, 'E': math.e, 'INF': math.inf,
            'random': random.random,
            'randint': random.randint,
        })

        # string namespace
        env.set('string', {
            'len': len,
            'to_upper': lambda s: str(s).upper(),
            'to_lower': lambda s: str(s).lower(),
            'trim': lambda s: str(s).strip(),
            'split': lambda s, d=None: str(s).split(d),
            'replace': lambda s, a, b: str(s).replace(a, b),
            'contains': lambda s, sub: sub in str(s),
            'starts_with': lambda s, p: str(s).startswith(p),
            'ends_with': lambda s, p: str(s).endswith(p),
            'format': lambda tmpl, *a: _format_str(tmpl, list(a)),
            'parse_int': lambda s: int(s) if str(s).lstrip('-').isdigit() else CPPSResult(False, f"cannot parse '{s}'"),
            'parse_float': lambda s: _try_parse_float(s),
            'repeat': lambda s, n: str(s) * int(n),
            'chars': lambda s: list(str(s)),
        })

        # collections namespace
        env.set('collections', {
            'List': {'new': lambda: []},
            'Map': {'new': lambda: {}},
            'Set': {'new': lambda: set()},
        })

        # time namespace
        env.set('time', {
            'now': time_module.time,
            'sleep': time_module.sleep,
            'format': lambda t: time_module.strftime('%Y-%m-%d %H:%M:%S', time_module.localtime(t)),
        })

        # Direct global functions
        env.set('println',  lambda *a: StdLib.io_println(*a))
        env.set('print',    lambda *a: StdLib.io_print(*a))
        env.set('input',    lambda p='': StdLib.io_input(p))
        env.set('len',      lambda x: len(x) if hasattr(x, '__len__') else 0)
        env.set('type_of',  lambda x: _type_of(x))
        env.set('str',      lambda x: _display(x))
        env.set('int',      lambda x: int(x) if x is not None else 0)
        env.set('float',    lambda x: float(x) if x is not None else 0.0)
        env.set('bool',     lambda x: bool(x))
        env.set('abs',      abs)
        env.set('sqrt',     math.sqrt)
        env.set('max',      lambda *a: max(*a))
        env.set('min',      lambda *a: min(*a))
        env.set('range',    lambda *a: list(range(*[int(x) for x in a])))
        env.set('assert',   lambda cond, msg='assertion failed': _assert(cond, msg))

        # Result constructors
        env.set('Ok',  lambda v=None: CPPSResult(True, v))
        env.set('Err', lambda v="error": CPPSResult(False, v))

        # Channel constructor
        env.set('Channel', lambda cap=0: CPPSChannel(int(cap)))

        # List utilities
        env.set('List', {'new': lambda: []})
        env.set('Map',  {'new': lambda: {}})
        env.set('Set',  {'new': lambda: set()})

    # ── Evaluation ───────────────────────────────────────────────────────────

    def eval(self, node, env: Env):
        if node is None:
            return None

        # --- Literals ---
        if isinstance(node, Literal):
            return node.value

        if isinstance(node, VarRef):
            val = env.get(node.name)
            if val is not None:
                return val
            # Try as plain string fallback
            return None

        # --- Ownership ---
        if isinstance(node, OwnershipExpr):
            inner = self.eval(node.inner, env)
            return CPPSOwned(node.kind, inner, node.lifetime)

        # --- Collections ---
        if isinstance(node, ListLiteral):
            return [self.eval(e, env) for e in node.elements]

        if isinstance(node, MapLiteral):
            d = {}
            for k, v in node.pairs:
                d[k] = self.eval(v, env)
            return d

        if isinstance(node, TupleLiteral):
            return tuple(self.eval(e, env) for e in node.elements)

        # --- Self reference ---
        if isinstance(node, SelfRef):
            return env.get('self')

        # --- Field access ---
        if isinstance(node, FieldAccess):
            obj = self.eval(node.obj, env)
            return self._get_field(obj, node.field)

        # --- Index access ---
        if isinstance(node, IndexAccess):
            obj = self.eval(node.obj, env)
            idx = self.eval(node.index, env)
            if isinstance(obj, (list, tuple)):
                return obj[int(idx)]
            if isinstance(obj, dict):
                return obj.get(idx)
            if isinstance(obj, str):
                return obj[int(idx)]
            return None

        # --- Result constructors ---
        if isinstance(node, ResultOk):
            return CPPSResult(True, self.eval(node.value, env))
        if isinstance(node, ResultErr):
            return CPPSResult(False, self.eval(node.value, env))

        # --- Binary operations ---
        if isinstance(node, BinaryOp):
            return self._eval_binary(node, env)

        # --- Unary operations ---
        if isinstance(node, UnaryOp):
            val = self.eval(node.operand, env)
            if node.op == '-': return -val
            if node.op == '!': return not bool(val)
            return val

        # --- Assignment ---
        if isinstance(node, Assign):
            return self._exec_assign(node, env)

        # --- Function calls ---
        if isinstance(node, FnCall):
            return self._exec_fn_call(node.name, node.args, env)

        # --- Method calls ---
        if isinstance(node, MethodCall):
            obj = self.eval(node.obj, env)
            args = [self.eval(a, env) for a in node.args]
            return self._exec_method(obj, node.method, args, env)

        # --- Await ---
        if isinstance(node, AwaitExpr):
            val = self.eval(node.expr, env)
            # For channels: receive
            if isinstance(val, CPPSChannel):
                return val.recv()
            return val

        # --- Reflect ---
        if isinstance(node, ReflectExpr):
            target = self.eval(node.target, env)
            return self._reflect(target)

        # --- Pipe expr ---
        if isinstance(node, PipeExpr):
            left = self.eval(node.left, env)
            right = node.right
            if isinstance(right, FnCall):
                args = [left] + [self.eval(a, env) for a in right.args]
                return self._exec_fn_call(right.name, [], env, pre_args=args)
            return left

        return None

    def _get_field(self, obj, field):
        if isinstance(obj, CPPSInstance):
            return obj.get(field)
        if isinstance(obj, dict):
            return obj.get(field)
        if isinstance(obj, CPPSOwned):
            return self._get_field(obj.value, field)
        if isinstance(obj, CPPSResult):
            if field == 'ok': return obj.ok
            if field == 'value': return obj.value
        return None

    def _eval_binary(self, node: BinaryOp, env: Env):
        op = node.op

        # Short-circuit
        if op == '&&':
            left = self.eval(node.left, env)
            return bool(left) and bool(self.eval(node.right, env))
        if op == '||':
            left = self.eval(node.left, env)
            return bool(left) or bool(self.eval(node.right, env))

        left = self.eval(node.left, env)
        right = self.eval(node.right, env)

        # Unwrap ownership for operations
        if isinstance(left, CPPSOwned): left = left.value
        if isinstance(right, CPPSOwned): right = right.value

        try:
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return _display(left) + _display(right)
                return left + right
            if op == '-': return left - right
            if op == '*':
                if isinstance(left, str) and isinstance(right, int):
                    return left * right
                return left * right
            if op == '/':
                if right == 0:
                    raise CPPSPanic("division by zero")
                return left / right
            if op == '%': return left % right
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == '<': return left < right
            if op == '>': return left > right
            if op == '<=': return left <= right
            if op == '>=': return left >= right
        except CPPSPanic:
            raise
        except Exception:
            return None
        return None

    def _exec_assign(self, node: Assign, env: Env):
        val = self.eval(node.value, env)
        target = node.target
        op = node.op

        if isinstance(target, VarRef):
            if op != '=':
                old = env.get(target.name) or 0
                val = self._apply_aug(old, op, val)
            env.assign(target.name, val)
            return val

        if isinstance(target, FieldAccess):
            obj = self.eval(target.obj, env)
            if isinstance(obj, CPPSInstance):
                if op != '=':
                    old = obj.get(target.field) or 0
                    val = self._apply_aug(old, op, val)
                obj.set(target.field, val)
            elif isinstance(obj, dict):
                if op != '=':
                    old = obj.get(target.field, 0)
                    val = self._apply_aug(old, op, val)
                obj[target.field] = val
            return val

        if isinstance(target, IndexAccess):
            obj = self.eval(target.obj, env)
            idx = self.eval(target.index, env)
            if isinstance(obj, list):
                if op != '=':
                    old = obj[int(idx)]
                    val = self._apply_aug(old, op, val)
                obj[int(idx)] = val
            elif isinstance(obj, dict):
                if op != '=':
                    old = obj.get(idx, 0)
                    val = self._apply_aug(old, op, val)
                obj[idx] = val
            return val

        return val

    def _apply_aug(self, old, op, val):
        if op == '+=': return old + val
        if op == '-=': return old - val
        if op == '*=': return old * val
        if op == '/=': return old / val if val != 0 else 0
        return val

    # ── Execution ─────────────────────────────────────────────────────────────

    def exec(self, node, env: Env):
        if node is None:
            return None

        # Top-level program
        if isinstance(node, Program):
            for stmt in node.statements:
                self.exec(stmt, env)
            # Auto-call main() if defined
            if env.get('main'):
                self._exec_fn_call('main', [], env)
            return None

        # Module
        if isinstance(node, ModuleDecl):
            self.current_module = node.name
            return None

        if isinstance(node, ImportStmt):
            self._exec_import(node, env)
            return None

        if isinstance(node, ExportStmt):
            # Mark as exported (stored in module)
            return None

        # Variable declaration
        if isinstance(node, VarDecl):
            val = self.eval(node.value, env) if node.value else None
            if node.ownership:
                val = CPPSOwned(node.ownership, val)
            env.set(node.name, val)
            return None

        # Function definition
        if isinstance(node, FnDef):
            env.set(node.name, node)
            return None

        # Override
        if isinstance(node, OverrideDecl):
            env.set(node.fn_def.name, node.fn_def)
            return None

        # Class definition
        if isinstance(node, ClassDef):
            self.classes[node.name] = node
            env.set(node.name, node)
            # Register static methods
            for stmt in node.body:
                if isinstance(stmt, FnDef) and stmt.is_static:
                    sname = f"{node.name}::{stmt.name}"
                    env.set(sname, stmt)
            return None

        # Struct definition
        if isinstance(node, StructDef):
            self.structs[node.name] = node
            env.set(node.name, node)
            return None

        # Trait definition
        if isinstance(node, TraitDef):
            self.traits[node.name] = node
            env.set(node.name, node)
            return None

        # Impl block
        if isinstance(node, ImplBlock):
            if node.type_name not in self.impls:
                self.impls[node.type_name] = {}
            for method in node.methods:
                if isinstance(method, FnDef):
                    self.impls[node.type_name][method.name] = method
            return None

        # Return
        if isinstance(node, ReturnStmt):
            val = self.eval(node.value, env) if node.value else None
            raise ReturnException(val)

        # Break / Continue
        if isinstance(node, BreakStmt):
            raise BreakException()
        if isinstance(node, ContinueStmt):
            raise ContinueException()

        # Panic
        if isinstance(node, PanicStmt):
            msg = self.eval(node.message, env)
            raise CPPSPanic(str(msg) if msg is not None else "explicit panic")

        # Pipe statement  ~> expr
        if isinstance(node, PipeStmt):
            self.eval(node.expr, env)
            return None

        # If
        if isinstance(node, IfStmt):
            cond = self.eval(node.condition, env)
            if bool(cond):
                child = env.child()
                for s in node.then_body:
                    self.exec(s, child)
            else:
                executed = False
                for elif_cond, elif_body in node.elif_clauses:
                    if bool(self.eval(elif_cond, env)):
                        child = env.child()
                        for s in elif_body:
                            self.exec(s, child)
                        executed = True
                        break
                if not executed:
                    child = env.child()
                    for s in node.else_body:
                        self.exec(s, child)
            return None

        # For
        if isinstance(node, ForStmt):
            iterable = self.eval(node.iterable, env)
            if iterable is None:
                return None
            if isinstance(iterable, CPPSOwned):
                iterable = iterable.value
            if not hasattr(iterable, '__iter__'):
                return None
            for item in iterable:
                child = env.child()
                child.set(node.var_name, item)
                try:
                    for s in node.body:
                        self.exec(s, child)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None

        # While
        if isinstance(node, WhileStmt):
            while bool(self.eval(node.condition, env)):
                child = env.child()
                try:
                    for s in node.body:
                        self.exec(s, child)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None

        # Pattern match
        if isinstance(node, MatchStmt):
            return self._exec_match(node, env)

        # Try/catch
        if isinstance(node, TryCatch):
            return self._exec_try_catch(node, env)

        # Go coroutine
        if isinstance(node, GoStmt):
            def run():
                try:
                    self.eval(node.call, env.child())
                except Exception:
                    pass
            t = threading.Thread(target=run, daemon=True)
            t.start()
            self._go_threads.append(t)
            return None

        # Macro invocation
        if isinstance(node, MacroInvoke):
            return self._exec_macro(node, env)

        # Reflect
        if isinstance(node, ReflectExpr):
            return self._reflect(self.eval(node.target, env))

        # Expression node used as statement
        return self.eval(node, env)

    # ── Function call ─────────────────────────────────────────────────────────

    def _exec_fn_call(self, name: str, arg_nodes, env: Env, pre_args=None):
        args = list(pre_args or []) + [self.eval(a, env) for a in arg_nodes]

        # Built-in io
        if name in ('println', 'io::println'):
            template = _display(args[0]) if args else ''
            for a in args[1:]:
                template = template.replace('{}', _display(a), 1)
            print(template)
            return None

        if name in ('print', 'io::print'):
            template = _display(args[0]) if args else ''
            for a in args[1:]:
                template = template.replace('{}', _display(a), 1)
            print(template, end='')
            return None

        if name in ('input', 'io::input'):
            prompt = _display(args[0]) if args else ''
            return input(prompt)

        if name in ('io::eprintln', 'eprintln'):
            print(_display(args[0]) if args else '', file=sys.stderr)
            return None

        # Math
        math_map = {
            'abs': lambda a: abs(a[0]),
            'sqrt': lambda a: math.sqrt(a[0]),
            'pow': lambda a: math.pow(a[0], a[1]),
            'sin': lambda a: math.sin(a[0]),
            'cos': lambda a: math.cos(a[0]),
            'tan': lambda a: math.tan(a[0]),
            'log': lambda a: math.log(a[0]) if len(a)==1 else math.log(a[0],a[1]),
            'log2': lambda a: math.log2(a[0]),
            'log10': lambda a: math.log10(a[0]),
            'exp': lambda a: math.exp(a[0]),
            'floor': lambda a: int(math.floor(a[0])),
            'ceil': lambda a: int(math.ceil(a[0])),
            'round': lambda a: round(a[0], int(a[1]) if len(a)>1 else 0),
            'random': lambda a: random.random(),
            'randint': lambda a: random.randint(int(a[0]), int(a[1])),
            'math::sqrt': lambda a: math.sqrt(a[0]),
            'math::pow': lambda a: math.pow(a[0], a[1]),
            'math::abs': lambda a: abs(a[0]),
            'math::sin': lambda a: math.sin(a[0]),
            'math::cos': lambda a: math.cos(a[0]),
            'math::floor': lambda a: int(math.floor(a[0])),
            'math::ceil': lambda a: int(math.ceil(a[0])),
            'math::log': lambda a: math.log(a[0]),
            'math::random': lambda a: random.random(),
            'math::randint': lambda a: random.randint(int(a[0]), int(a[1])),
        }
        if name in math_map:
            try: return math_map[name](args)
            except Exception as e: raise CPPSError(f"math error: {e}")

        # Type utilities
        if name == 'len':
            if args and hasattr(args[0], '__len__'): return len(args[0])
            return 0
        if name == 'type_of': return _type_of(args[0]) if args else 'none'
        if name == 'str': return _display(args[0]) if args else ''
        if name == 'int':
            try: return int(args[0]) if args else 0
            except: return 0
        if name == 'float':
            try: return float(args[0]) if args else 0.0
            except: return 0.0
        if name == 'bool': return bool(args[0]) if args else False
        if name == 'range': return list(range(*[int(a) for a in args]))
        if name == 'assert':
            cond = bool(args[0]) if args else False
            msg = str(args[1]) if len(args) > 1 else 'assertion failed'
            if not cond: raise CPPSPanic(msg)
            return None

        # Result
        if name == 'Ok': return CPPSResult(True, args[0] if args else None)
        if name == 'Err': return CPPSResult(False, args[0] if args else 'error')

        # Channel
        if name in ('Channel', 'Channel::new'):
            cap = int(args[0]) if args else 0
            return CPPSChannel(cap)

        # Time
        if name == 'time::now': return time_module.time()
        if name == 'time::sleep': time_module.sleep(float(args[0]) if args else 0); return None

        # String utilities
        if name == 'string::format':
            tmpl = str(args[0]) if args else ''
            for a in args[1:]:
                tmpl = tmpl.replace('{}', _display(a), 1)
            return tmpl
        if name == 'string::parse_int':
            try: return int(args[0])
            except: return CPPSResult(False, f"cannot parse")

        # List / Map / Set constructors
        if name in ('List', 'List::new'): return []
        if name in ('Map', 'Map::new'): return {}
        if name in ('Set', 'Set::new'): return set()

        # Class instantiation / static method call  MyClass::new(...) / MyClass::method(...)
        if '::' in name:
            parts = name.split('::')
            class_name = parts[0]
            method_name = parts[-1]
            if class_name in self.classes:
                cls = self.classes[class_name]
                # Check if method_name is a static method (not a constructor)
                if method_name not in ('new', 'init', 'create'):
                    for stmt in cls.body:
                        fn_def = stmt.fn if isinstance(stmt, OverrideDecl) else stmt
                        if isinstance(fn_def, FnDef) and fn_def.name == method_name:
                            # Found a static/class method — call it directly
                            child = self.global_env.child()
                            for i, param in enumerate(fn_def.params):
                                child.set(param[0], args[i] if i < len(args) else None)
                            try:
                                for s in fn_def.body:
                                    self.exec(s, child)
                            except ReturnException as e:
                                return e.value
                            return None
                return self._instantiate(class_name, method_name, args, env)
            # Namespace static method call
            fn = env.get(name)
            if fn:
                return self._call_fn(fn, args, env)

        # Namespace function call  ns.method / ns::method
        ns_map = {
            'io': ['println', 'print', 'input', 'eprintln'],
            'math': list(math_map.keys()),
        }
        for ns, methods in ns_map.items():
            ns_obj = env.get(ns)
            if isinstance(ns_obj, dict):
                for method in methods:
                    if name == f"{ns}::{method}" or name == f"{ns}.{method}":
                        fn = ns_obj.get(method)
                        if callable(fn):
                            return fn(*args)

        # User-defined function
        fn = env.get(name)
        if fn is not None:
            if isinstance(fn, FnDef):
                return self._call_fn(fn, args, env)
            if isinstance(fn, CPPSClosure):
                return self._call_closure(fn, args, env)
            if callable(fn):
                return fn(*args)

        # Unknown — return None silently
        return None

    def _call_fn(self, fn: FnDef, args: List, caller_env: Env):
        child = self.global_env.child()
        for i, param in enumerate(fn.params):
            pname = param[0]
            default = param[3] if len(param) > 3 else None
            val = args[i] if i < len(args) else (self.eval(default, caller_env) if default else None)
            child.set(pname, val)
        try:
            for stmt in fn.body:
                self.exec(stmt, child)
        except ReturnException as e:
            return e.value
        return None

    def _call_closure(self, closure: CPPSClosure, args: List, caller_env: Env):
        child = Env(parent=closure.captured_env)
        for i, param in enumerate(closure.fn_def.params):
            pname = param[0]
            child.set(pname, args[i] if i < len(args) else None)
        try:
            for stmt in closure.fn_def.body:
                self.exec(stmt, child)
        except ReturnException as e:
            return e.value
        return None

    # ── Class instantiation ───────────────────────────────────────────────────

    def _instantiate(self, class_name: str, method: str, args: List, env: Env) -> CPPSInstance:
        cls = self.classes.get(class_name)
        instance = CPPSInstance(class_name)

        # Inherit from parents
        if cls and cls.parents:
            for parent_name in cls.parents:
                parent_cls = self.classes.get(parent_name)
                if parent_cls:
                    parent_inst = self._instantiate(parent_name, 'new', [], env)
                    instance.fields.update(parent_inst.fields)

        # Register methods from impl blocks
        impls = self.impls.get(class_name, {})

        # Register class body methods
        if cls:
            for stmt in cls.body:
                if isinstance(stmt, FnDef):
                    instance.fields[f"__method_{stmt.name}"] = stmt
                elif isinstance(stmt, OverrideDecl):
                    # @@override wraps a FnDef — register the inner fn
                    instance.fields[f"__method_{stmt.fn.name}"] = stmt.fn
                elif isinstance(stmt, VarDecl):
                    instance.fields[stmt.name] = self.eval(stmt.value, env) if stmt.value else None

        for method_name, fn in impls.items():
            instance.fields[f"__method_{method_name}"] = fn

        # Call constructor (new / init)
        ctor_name = f"__method_{method}" if method != 'new' else '__method_new'
        # Try 'new' or 'init'
        for ctor in (ctor_name, '__method_new', '__method_init'):
            ctor_fn = instance.fields.get(ctor)
            if isinstance(ctor_fn, FnDef):
                child = self.global_env.child()
                child.set('self', instance)
                for i, param in enumerate(ctor_fn.params):
                    pname = param[0]
                    child.set(pname, args[i] if i < len(args) else None)
                try:
                    for stmt in ctor_fn.body:
                        self.exec(stmt, child)
                except ReturnException:
                    pass
                break

        return instance

    # ── Method dispatch ───────────────────────────────────────────────────────

    def _exec_method(self, obj, method: str, args: List, env: Env):
        # Ownership wrapper
        if isinstance(obj, CPPSOwned):
            obj = obj.value

        # CPPSInstance method call
        if isinstance(obj, CPPSInstance):
            fn = obj.fields.get(f"__method_{method}")
            if isinstance(fn, FnDef):
                child = self.global_env.child()
                child.set('self', obj)
                for i, param in enumerate(fn.params):
                    pname = param[0]
                    child.set(pname, args[i] if i < len(args) else None)
                try:
                    for stmt in fn.body:
                        self.exec(stmt, child)
                except ReturnException as e:
                    return e.value
                return None
            # Try impl block
            impl_fn = self.impls.get(obj.class_name, {}).get(method)
            if impl_fn:
                child = self.global_env.child()
                child.set('self', obj)
                for i, param in enumerate(impl_fn.params):
                    child.set(param[0], args[i] if i < len(args) else None)
                try:
                    for stmt in impl_fn.body:
                        self.exec(stmt, child)
                except ReturnException as e:
                    return e.value
                return None
            # Field access as method
            field_val = obj.get(method)
            if callable(field_val):
                return field_val(*args)
            return field_val

        # List methods
        if isinstance(obj, list):
            return self._list_method(obj, method, args)

        # Dict / Map methods
        if isinstance(obj, dict):
            return self._map_method(obj, method, args)

        # Set methods
        if isinstance(obj, set):
            return self._set_method(obj, method, args)

        # String methods
        if isinstance(obj, str):
            return self._string_method(obj, method, args)

        # Result methods
        if isinstance(obj, CPPSResult):
            return self._result_method(obj, method, args)

        # Channel methods
        if isinstance(obj, CPPSChannel):
            if method == 'send': obj.send(args[0] if args else None); return None
            if method == 'recv': return obj.recv()
            if method == 'try_recv': return obj.try_recv()
            if method == 'len': return obj.len()

        # Callable field
        if callable(obj):
            return obj(*args)

        return None

    def _list_method(self, lst, method, args):
        if method == 'push': lst.append(args[0] if args else None); return lst
        if method == 'append': lst.append(args[0] if args else None); return lst
        if method == 'pop': return lst.pop() if lst else None
        if method == 'pop_front': return lst.pop(0) if lst else None
        if method == 'len': return len(lst)
        if method == 'is_empty': return len(lst) == 0
        if method == 'contains': return (args[0] in lst) if args else False
        if method == 'index_of': return lst.index(args[0]) if args and args[0] in lst else -1
        if method == 'remove':
            if args and args[0] in lst: lst.remove(args[0])
            return lst
        if method == 'remove_at':
            if args: lst.pop(int(args[0]))
            return lst
        if method == 'insert':
            if len(args) >= 2: lst.insert(int(args[0]), args[1])
            return lst
        if method == 'clear': lst.clear(); return lst
        if method == 'reverse': lst.reverse(); return lst
        if method == 'sort':
            try: lst.sort()
            except: pass
            return lst
        if method == 'slice':
            start = int(args[0]) if args else 0
            end = int(args[1]) if len(args) > 1 else len(lst)
            return lst[start:end]
        if method == 'get':
            idx = int(args[0]) if args else 0
            return lst[idx] if 0 <= idx < len(lst) else None
        if method == 'set':
            if len(args) >= 2: lst[int(args[0])] = args[1]
            return lst
        if method == 'join':
            sep = str(args[0]) if args else ''
            return sep.join(_display(x) for x in lst)
        if method == 'map':
            fn = args[0] if args else None
            if isinstance(fn, FnDef):
                return [self._call_fn(fn, [x], Env()) for x in lst]
            if callable(fn): return [fn(x) for x in lst]
            return lst
        if method == 'filter':
            fn = args[0] if args else None
            if isinstance(fn, FnDef):
                return [x for x in lst if bool(self._call_fn(fn, [x], Env()))]
            if callable(fn): return [x for x in lst if bool(fn(x))]
            return lst
        if method == 'reduce':
            fn = args[0] if args else None
            if not lst: return None
            acc = lst[0]
            for x in lst[1:]:
                if isinstance(fn, FnDef): acc = self._call_fn(fn, [acc, x], Env())
                elif callable(fn): acc = fn(acc, x)
            return acc
        if method == 'first': return lst[0] if lst else None
        if method == 'last': return lst[-1] if lst else None
        if method == 'sum': return sum(lst)
        if method == 'max': return max(lst) if lst else None
        if method == 'min': return min(lst) if lst else None
        return None

    def _map_method(self, d, method, args):
        if method == 'insert':
            if len(args) >= 2: d[args[0]] = args[1]
            return d
        if method == 'set':
            if len(args) >= 2: d[args[0]] = args[1]
            return d
        if method == 'get':
            default = args[1] if len(args) > 1 else None
            return d.get(args[0], default) if args else None
        if method == 'remove':
            if args: d.pop(args[0], None)
            return d
        if method == 'contains' or method == 'has':
            return args[0] in d if args else False
        if method == 'keys': return list(d.keys())
        if method == 'values': return list(d.values())
        if method == 'entries': return list(d.items())
        if method == 'len': return len(d)
        if method == 'is_empty': return len(d) == 0
        if method == 'clear': d.clear(); return d
        return None

    def _set_method(self, s, method, args):
        if method == 'add': s.add(args[0] if args else None); return s
        if method == 'remove':
            if args: s.discard(args[0])
            return s
        if method == 'contains': return (args[0] in s) if args else False
        if method == 'len': return len(s)
        if method == 'is_empty': return len(s) == 0
        if method == 'union': return s | (args[0] if args else set())
        if method == 'intersect': return s & (args[0] if args else set())
        if method == 'diff': return s - (args[0] if args else set())
        if method == 'to_list': return list(s)
        return None

    def _string_method(self, s, method, args):
        if method == 'len': return len(s)
        if method == 'to_upper': return s.upper()
        if method == 'to_lower': return s.lower()
        if method == 'trim': return s.strip()
        if method == 'trim_start': return s.lstrip()
        if method == 'trim_end': return s.rstrip()
        if method == 'split': return s.split(str(args[0]) if args else None)
        if method == 'replace': return s.replace(str(args[0]), str(args[1])) if len(args)>=2 else s
        if method == 'contains': return (str(args[0]) in s) if args else False
        if method == 'starts_with': return s.startswith(str(args[0])) if args else False
        if method == 'ends_with': return s.endswith(str(args[0])) if args else False
        if method == 'index_of':
            idx = s.find(str(args[0])) if args else -1
            return idx
        if method == 'slice':
            start = int(args[0]) if args else 0
            end = int(args[1]) if len(args) > 1 else len(s)
            return s[start:end]
        if method == 'chars': return list(s)
        if method == 'parse_int':
            try: return int(s)
            except: return CPPSResult(False, f"cannot parse '{s}' as int")
        if method == 'parse_float':
            try: return float(s)
            except: return CPPSResult(False, f"cannot parse '{s}' as float")
        if method == 'repeat': return s * (int(args[0]) if args else 1)
        if method == 'is_empty': return len(s) == 0
        if method == 'format':
            tmpl = s
            for a in args:
                tmpl = tmpl.replace('{}', _display(a), 1)
            return tmpl
        if method == 'to_bytes': return list(s.encode('utf-8'))
        return None

    def _result_method(self, r, method, args):
        if method == 'is_ok': return r.ok
        if method == 'is_err': return not r.ok
        if method == 'unwrap': return r.unwrap()
        if method == 'unwrap_or': return r.unwrap_or(args[0] if args else None)
        if method == 'ok': return r.value if r.ok else None
        if method == 'err': return r.value if not r.ok else None
        if method == 'map':
            if r.ok and args:
                fn = args[0]
                if isinstance(fn, FnDef):
                    return CPPSResult(True, self._call_fn(fn, [r.value], Env()))
                if callable(fn):
                    return CPPSResult(True, fn(r.value))
            return r
        return None

    # ── Pattern matching ─────────────────────────────────────────────────────

    def _exec_match(self, node: MatchStmt, env: Env):
        val = self.eval(node.value, env)
        for arm in node.arms:
            bindings = {}
            if self._match_pattern(arm.pattern, val, bindings):
                if arm.guard:
                    child = env.child()
                    for k, v in bindings.items():
                        child.set(k, v)
                    if not bool(self.eval(arm.guard, child)):
                        continue
                child = env.child()
                for k, v in bindings.items():
                    child.set(k, v)
                try:
                    for s in arm.body:
                        self.exec(s, child)
                except ReturnException as e:
                    raise
                return None
        return None

    def _match_pattern(self, pattern, value, bindings: dict) -> bool:
        if isinstance(pattern, WildcardPattern):
            return True
        if isinstance(pattern, LiteralPattern):
            return value == pattern.value
        if isinstance(pattern, BindingPattern):
            bindings[pattern.name] = value
            return True
        if isinstance(pattern, TuplePattern):
            if not isinstance(value, tuple) or len(value) != len(pattern.elements):
                return False
            for p, v in zip(pattern.elements, value):
                if not self._match_pattern(p, v, bindings):
                    return False
            return True
        if isinstance(pattern, RangePattern):
            try:
                if pattern.inclusive:
                    return pattern.lo <= value <= pattern.hi
                return pattern.lo <= value < pattern.hi
            except:
                return False
        if isinstance(pattern, OrPattern):
            for p in pattern.patterns:
                b = {}
                if self._match_pattern(p, value, b):
                    bindings.update(b)
                    return True
            return False
        return False

    # ── Try / catch ──────────────────────────────────────────────────────────

    def _exec_try_catch(self, node: TryCatch, env: Env):
        try:
            child = env.child()
            for s in node.try_body:
                self.exec(s, child)
        except (CPPSPanic, CPPSError) as e:
            child = env.child()
            child.set(node.catch_var, str(e))
            for s in node.catch_body:
                self.exec(s, child)
        except Exception as e:
            child = env.child()
            child.set(node.catch_var, str(e))
            for s in node.catch_body:
                self.exec(s, child)

    # ── Macros ───────────────────────────────────────────────────────────────

    def _exec_macro(self, node: MacroInvoke, env: Env):
        if node.kind == 'macro_tok':
            # Token macro: compile-time token inspection
            args = [self.eval(a, env) for a in node.args]
            print(f"[MACRO_TOK] {node.name}({', '.join(_display(a) for a in args)})")
            return None
        if node.kind == 'macro_ast':
            # AST macro: produce code from args
            args = [self.eval(a, env) for a in node.args]
            print(f"[MACRO_AST] {node.name}({', '.join(_display(a) for a in args)})")
            return None
        return None

    # ── Reflection ───────────────────────────────────────────────────────────

    def _reflect(self, target):
        if isinstance(target, CPPSInstance):
            return {
                'type': target.class_name,
                'fields': {k: v for k, v in target.fields.items() if not k.startswith('__method_')},
                'methods': [k[9:] for k in target.fields if k.startswith('__method_')],
            }
        if isinstance(target, FnDef):
            return {
                'type': 'function',
                'name': target.name,
                'params': [p[0] for p in target.params],
                'return_type': target.return_type,
            }
        if isinstance(target, list):
            return {'type': 'List', 'len': len(target)}
        if isinstance(target, dict):
            return {'type': 'Map', 'len': len(target)}
        return {'type': _type_of(target), 'value': _display(target)}

    # ── Import ───────────────────────────────────────────────────────────────

    def _exec_import(self, node: ImportStmt, env: Env):
        for mod_path in node.module:
            # Built-in modules are pre-registered, nothing to do
            # Could load external .cpps modules here
            pass

    # ── Main entry ───────────────────────────────────────────────────────────

    def execute(self, ast):
        try:
            self.exec(ast, self.global_env)
            # Wait for go goroutines
            for t in self._go_threads:
                t.join(timeout=5.0)
        except CPPSPanic as e:
            print(f"\n💥 PANIC: {e.msg}", file=sys.stderr)
            sys.exit(1)
        except ReturnException:
            pass


# ── Helpers ───────────────────────────────────────────────────────────────────

def _type_of(v):
    if v is None: return 'none'
    if isinstance(v, bool): return 'bool'
    if isinstance(v, int): return 'int'
    if isinstance(v, float): return 'float'
    if isinstance(v, str): return 'string'
    if isinstance(v, list): return 'List'
    if isinstance(v, dict): return 'Map'
    if isinstance(v, set): return 'Set'
    if isinstance(v, tuple): return 'Tuple'
    if isinstance(v, CPPSResult): return 'Result'
    if isinstance(v, CPPSInstance): return v.class_name
    if isinstance(v, CPPSOwned): return f"{v.kind}<{_type_of(v.value)}>"
    if isinstance(v, CPPSChannel): return 'Channel'
    if isinstance(v, FnDef): return 'function'
    return 'unknown'


def _format_str(template, args):
    s = str(template)
    for a in args:
        s = s.replace('{}', _display(a), 1)
    return s


def _try_parse_float(s):
    try:
        return float(s)
    except:
        return CPPSResult(False, f"cannot parse '{s}' as float")


def _assert(cond, msg):
    if not bool(cond):
        raise CPPSPanic(str(msg))
