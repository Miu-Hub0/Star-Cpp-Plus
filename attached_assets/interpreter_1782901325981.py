"""CP+* Interpreter - Chạy trực tiếp AST"""
import sys, os, re, math, random, time as time_module
from typing import Any, List, Dict, Tuple
from parser import *

class ReturnExc(Exception):
    def __init__(self, val): self.value = val

class BreakExc(Exception): pass
class ContinueExc(Exception): pass

class Interpreter:
    def __init__(self):
        self.vars: Dict[str, Any] = {}
        self.lists: Dict[str, list] = {}
        self.maps: Dict[str, dict] = {}
        self.funcs: Dict[str, Tuple[list, list]] = {}  # name -> (params, body)
        self.classes: Dict[str, ClassDef] = {}
        self.in_class = None
    
    def get(self, name):
        if name in self.vars: return self.vars[name]
        if name in self.lists: return self.lists[name]
        if name in self.maps: return self.maps[name]
        return None
    
    def set(self, name, val):
        if name in self.lists: self.lists[name] = val
        elif name in self.maps: self.maps[name] = val
        else: self.vars[name] = val
    
    def eval_node(self, node):
        if node is None: return None
        
        if isinstance(node, Literal): return node.value
        
        if isinstance(node, VarRef):
            val = self.get(node.name)
            return val if val is not None else node.name
        
        if isinstance(node, BinaryOp):
            left = self.eval_node(node.left)
            right = self.eval_node(node.right)
            op = node.op
            try:
                if op == '+': return left + right
                if op == '-': return left - right
                if op == '*': return left * right
                if op == '/': return left / right if right != 0 else 0
                if op == '%': return left % right
                if op == '==': return left == right
                if op == '!=': return left != right
                if op == '<': return left < right
                if op == '>': return left > right
                if op == '<=': return left <= right
                if op == '>=': return left >= right
                if op == '&&': return bool(left) and bool(right)
                if op == '||': return bool(left) or bool(right)
            except: return None
        
        if isinstance(node, UnaryOp):
            val = self.eval_node(node.operand)
            if node.op == '-': return -val
            if node.op == '!': return not bool(val)
        
        if isinstance(node, FnCall): return self.exec_fn_call(node.name, node.args)
        
        if isinstance(node, MethodCall):
            obj = self.eval_node(node.obj)
            args = [self.eval_node(a) for a in node.args]
            return self.exec_method(obj, node.method, args)
        
        if isinstance(node, FieldAccess):
            obj = self.eval_node(node.obj)
            if isinstance(obj, dict):
                return obj.get(node.field)
        
        if isinstance(node, ListLiteral):
            return [self.eval_node(e) for e in node.elements]
        
        return None
    
    def exec_fn_call(self, name, args):
        ev_args = [self.eval_node(a) for a in args]
        
        # Built-in: println
        if name in ('println', 'io::println'):
            template = str(ev_args[0]) if ev_args else ''
            for a in ev_args[1:]:
                template = template.replace('{}', str(a), 1)
            print(template)
            return None
        
        # Built-in: print
        if name in ('print', 'io::print'):
            print(*ev_args, sep='', end='')
            return None
        
        # Built-in: input
        if name in ('input', 'io::input'):
            return input(str(ev_args[0]) if ev_args else '')
        
        # Built-in: len
        if name == 'len':
            return len(ev_args[0]) if ev_args else 0
        
        # Built-in: type_of
        if name == 'type_of':
            v = ev_args[0] if ev_args else None
            if isinstance(v, bool): return 'bool'
            if isinstance(v, int): return 'int'
            if isinstance(v, float): return 'float'
            if isinstance(v, str): return 'string'
            if isinstance(v, list): return 'List'
            if isinstance(v, dict): return 'Map'
            return 'unknown'
        
        # Math functions
        math_funcs = {
            'abs': abs, 'sqrt': math.sqrt, 'pow': math.pow,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'exp': math.exp,
            'floor': math.floor, 'ceil': math.ceil,
            'round': round, 'random': random.random,
            'max': max, 'min': min,
        }
        if name in math_funcs:
            try: return math_funcs[name](*ev_args)
            except: return 0
        
        # User function
        if name in self.funcs:
            params, body = self.funcs[name]
            old_vars = dict(self.vars)
            for i, (pname, _) in enumerate(params):
                self.vars[pname] = ev_args[i] if i < len(ev_args) else None
            try:
                for stmt in body:
                    self.exec_stmt(stmt)
            except ReturnExc as e:
                return e.value
            finally:
                self.vars = old_vars
        
        return None
    
    def exec_method(self, obj, method, args):
        if isinstance(obj, list):
            if method == 'push':
                obj.append(args[0] if args else None)
                return obj
            if method == 'len': return len(obj)
            if method == 'pop': return obj.pop()
            if method == 'is_empty': return len(obj) == 0
            if method == 'contains': return args[0] in obj if args else False
            if method == 'index_of': return obj.index(args[0]) if args and args[0] in obj else -1
            if method == 'remove':
                if args: obj.remove(args[0])
                return obj
        if isinstance(obj, str):
            if method == 'len': return len(obj)
            if method == 'to_upper': return obj.upper()
            if method == 'to_lower': return obj.lower()
            if method == 'trim': return obj.strip()
            if method == 'split': return obj.split(args[0]) if args else [obj]
            if method == 'replace': return obj.replace(args[0], args[1]) if len(args)>=2 else obj
            if method == 'contains': return args[0] in obj if args else False
        if isinstance(obj, dict):
            if method == 'insert': obj[args[0]] = args[1] if len(args)>=2 else None
            if method == 'remove': obj.pop(args[0], None)
            if method == 'keys': return list(obj.keys())
            if method == 'values': return list(obj.values())
            if method == 'len': return len(obj)
        return None
    
    def exec_stmt(self, stmt):
        if stmt is None: return
        
        if isinstance(stmt, Program):
            for s in stmt.statements: self.exec_stmt(s)
        
        elif isinstance(stmt, VarDecl):
            val = self.eval_node(stmt.value)
            self.set(stmt.name, val)
        
        elif isinstance(stmt, FnDef):
            self.funcs[stmt.name] = (stmt.params, stmt.body)
        
        elif isinstance(stmt, ClassDef):
            self.classes[stmt.name] = stmt
        
        elif isinstance(stmt, ReturnStmt):
            val = self.eval_node(stmt.value) if stmt.value else None
            raise ReturnExc(val)
        
        elif isinstance(stmt, IfStmt):
            cond = self.eval_node(stmt.condition)
            if cond:
                for s in stmt.then_body: self.exec_stmt(s)
            else:
                for s in stmt.else_body: self.exec_stmt(s)
        
        elif isinstance(stmt, ForStmt):
            iterable = self.eval_node(stmt.iterable)
            if iterable and hasattr(iterable, '__iter__'):
                for item in iterable:
                    self.set(stmt.var_name, item)
                    try:
                        for s in stmt.body: self.exec_stmt(s)
                    except BreakExc: break
                    except ContinueExc: continue
        
        elif isinstance(stmt, WhileStmt):
            while self.eval_node(stmt.condition):
                try:
                    for s in stmt.body: self.exec_stmt(s)
                except BreakExc: break
                except ContinueExc: continue
        
        elif isinstance(stmt, BreakStmt): raise BreakExc()
        elif isinstance(stmt, ContinueStmt): raise ContinueExc()
        
        elif isinstance(stmt, FnCall): self.exec_fn_call(stmt.name, stmt.args)
        elif isinstance(stmt, MethodCall): self.exec_method(self.eval_node(stmt.obj), stmt.method, [self.eval_node(a) for a in stmt.args])
        elif isinstance(stmt, Assign):
            val = self.eval_node(stmt.value)
            if isinstance(stmt.target, VarRef): self.set(stmt.target.name, val)
        
        elif isinstance(stmt, (BinaryOp, UnaryOp, Literal, VarRef)):
            self.eval_node(stmt)  # Expression statement
    
    def execute(self, ast):
        try:
            self.exec_stmt(ast)
        except ReturnExc: pass