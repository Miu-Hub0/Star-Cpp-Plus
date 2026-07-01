"""CP+* Parser - Extended AST for Advanced Language Features"""
from tokens import Token, TokenType


class ASTNode:
    pass


# ─── Core nodes ──────────────────────────────────────────────────────────────

class Program(ASTNode):
    def __init__(self, stmts): self.statements = stmts

class Literal(ASTNode):
    def __init__(self, value, line=0): self.value = value; self.line = line

class VarRef(ASTNode):
    def __init__(self, name, line=0): self.name = name; self.line = line

class BinaryOp(ASTNode):
    def __init__(self, left, op, right, line=0):
        self.left = left; self.op = op; self.right = right; self.line = line

class UnaryOp(ASTNode):
    def __init__(self, op, operand, line=0): self.op = op; self.operand = operand; self.line = line

class Assign(ASTNode):
    def __init__(self, target, value, op='=', line=0):
        self.target = target; self.value = value; self.op = op; self.line = line

class VarDecl(ASTNode):
    def __init__(self, name, var_type, value, is_mut=False, ownership=None, line=0):
        self.name = name; self.var_type = var_type; self.value = value
        self.is_mutable = is_mut; self.ownership = ownership; self.line = line

class ReturnStmt(ASTNode):
    def __init__(self, value=None, line=0): self.value = value; self.line = line

class BreakStmt(ASTNode):
    def __init__(self, line=0): self.line = line

class ContinueStmt(ASTNode):
    def __init__(self, line=0): self.line = line

class PanicStmt(ASTNode):
    def __init__(self, message, line=0): self.message = message; self.line = line

# ─── Collections ─────────────────────────────────────────────────────────────

class ListLiteral(ASTNode):
    def __init__(self, elements, line=0): self.elements = elements; self.line = line

class MapLiteral(ASTNode):
    def __init__(self, pairs, line=0): self.pairs = pairs; self.line = line  # [(key, val)]

class TupleLiteral(ASTNode):
    def __init__(self, elements, line=0): self.elements = elements; self.line = line

# ─── Function calls ───────────────────────────────────────────────────────────

class FnCall(ASTNode):
    def __init__(self, name, args, type_args=None, line=0):
        self.name = name; self.args = args
        self.type_args = type_args or []; self.line = line

class MethodCall(ASTNode):
    def __init__(self, obj, method, args, type_args=None, line=0):
        self.obj = obj; self.method = method; self.args = args
        self.type_args = type_args or []; self.line = line

class FieldAccess(ASTNode):
    def __init__(self, obj, field, line=0): self.obj = obj; self.field = field; self.line = line

class IndexAccess(ASTNode):
    def __init__(self, obj, index, line=0): self.obj = obj; self.index = index; self.line = line

class SelfRef(ASTNode):
    def __init__(self, line=0): self.line = line

class StaticCall(ASTNode):
    def __init__(self, type_name, method, args, line=0):
        self.type_name = type_name; self.method = method; self.args = args; self.line = line

# ─── Control flow ─────────────────────────────────────────────────────────────

class IfStmt(ASTNode):
    def __init__(self, condition, then_body, elif_clauses, else_body, line=0):
        self.condition = condition; self.then_body = then_body
        self.elif_clauses = elif_clauses; self.else_body = else_body; self.line = line

class ForStmt(ASTNode):
    def __init__(self, var_name, iterable, body, line=0):
        self.var_name = var_name; self.iterable = iterable; self.body = body; self.line = line

class WhileStmt(ASTNode):
    def __init__(self, condition, body, line=0):
        self.condition = condition; self.body = body; self.line = line

class MatchStmt(ASTNode):
    def __init__(self, value, arms, line=0):
        self.value = value; self.arms = arms; self.line = line

class MatchArm(ASTNode):
    def __init__(self, pattern, guard, body, line=0):
        self.pattern = pattern; self.guard = guard; self.body = body; self.line = line

# Pattern nodes
class WildcardPattern(ASTNode): pass
class LiteralPattern(ASTNode):
    def __init__(self, value, line=0): self.value = value; self.line = line
class BindingPattern(ASTNode):
    def __init__(self, name, line=0): self.name = name; self.line = line
class TuplePattern(ASTNode):
    def __init__(self, elements, line=0): self.elements = elements; self.line = line
class RangePattern(ASTNode):
    def __init__(self, lo, hi, inclusive, line=0):
        self.lo = lo; self.hi = hi; self.inclusive = inclusive; self.line = line
class OrPattern(ASTNode):
    def __init__(self, patterns, line=0): self.patterns = patterns; self.line = line

# ─── Definitions ─────────────────────────────────────────────────────────────

class FnDef(ASTNode):
    def __init__(self, name, type_params, params, ret_type, body, is_static=False, is_export=False, line=0):
        self.name = name; self.type_params = type_params; self.params = params
        self.return_type = ret_type; self.body = body
        self.is_static = is_static; self.is_export = is_export; self.line = line

class ClassDef(ASTNode):
    def __init__(self, name, type_params, parents, traits, body, line=0):
        self.name = name; self.type_params = type_params; self.parents = parents
        self.traits = traits; self.body = body; self.line = line

class TraitDef(ASTNode):
    def __init__(self, name, type_params, methods, line=0):
        self.name = name; self.type_params = type_params; self.methods = methods; self.line = line

class ImplBlock(ASTNode):
    def __init__(self, type_name, trait_name, methods, line=0):
        self.type_name = type_name; self.trait_name = trait_name
        self.methods = methods; self.line = line

class StructDef(ASTNode):
    def __init__(self, name, type_params, fields, line=0):
        self.name = name; self.type_params = type_params; self.fields = fields; self.line = line

# ─── Module system ────────────────────────────────────────────────────────────

class ModuleDecl(ASTNode):
    def __init__(self, name, line=0): self.name = name; self.line = line

class ImportStmt(ASTNode):
    def __init__(self, module, names, alias=None, line=0):
        self.module = module; self.names = names; self.alias = alias; self.line = line

class ExportStmt(ASTNode):
    def __init__(self, name, line=0): self.name = name; self.line = line

# ─── Ownership / memory ───────────────────────────────────────────────────────

class OwnershipExpr(ASTNode):
    def __init__(self, kind, inner, lifetime=None, line=0):
        self.kind = kind; self.inner = inner; self.lifetime = lifetime; self.line = line

# ─── Error handling ───────────────────────────────────────────────────────────

class TryCatch(ASTNode):
    def __init__(self, try_body, catch_var, catch_body, line=0):
        self.try_body = try_body; self.catch_var = catch_var
        self.catch_body = catch_body; self.line = line

class ResultOk(ASTNode):
    def __init__(self, value, line=0): self.value = value; self.line = line

class ResultErr(ASTNode):
    def __init__(self, value, line=0): self.value = value; self.line = line

# ─── Concurrency ─────────────────────────────────────────────────────────────

class GoStmt(ASTNode):
    def __init__(self, call, line=0): self.call = call; self.line = line

class AwaitExpr(ASTNode):
    def __init__(self, expr, line=0): self.expr = expr; self.line = line

# ─── Macros / reflection ─────────────────────────────────────────────────────

class MacroInvoke(ASTNode):
    def __init__(self, kind, name, args, line=0):
        self.kind = kind; self.name = name; self.args = args; self.line = line

class ReflectExpr(ASTNode):
    def __init__(self, target, line=0): self.target = target; self.line = line

class OverrideDecl(ASTNode):
    def __init__(self, fn_def, line=0): self.fn_def = fn_def; self.line = line

# ─── Statement pipe ~> ────────────────────────────────────────────────────────

class PipeStmt(ASTNode):
    """~> expr   —  statement form (print / call)"""
    def __init__(self, expr, line=0): self.expr = expr; self.line = line

class PipeExpr(ASTNode):
    """left ~> right  —  pipe operator"""
    def __init__(self, left, right, line=0): self.left = left; self.right = right; self.line = line


# ─────────────────────────────────────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t is not None]
        self.pos = 0

    # ── Helpers ──────────────────────────────────────────────────────────────

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else None

    def advance(self):
        t = self.peek()
        self.pos += 1
        return t

    def check(self, *types):
        t = self.peek()
        return t is not None and t.type in types

    def match(self, *types):
        if self.check(*types):
            return self.advance()
        return None

    def expect(self, typ, msg=""):
        t = self.peek()
        if t is None or t.type != typ:
            loc = f"L{t.line}" if t else "EOF"
            got = t.type.name if t else "EOF"
            raise ParseError(f"[{loc}] Expected {typ.name}, got {got}. {msg}")
        return self.advance()

    def expect_name(self):
        """Accept any token whose value is alphanumeric as a name (identifier OR keyword)."""
        t = self.peek()
        if t is None:
            raise ParseError("Unexpected EOF, expected a name")
        if t.type == TokenType.IDENTIFIER or (t.value and str(t.value).replace('_', '').isalnum()):
            return self.advance()
        raise ParseError(f"[L{t.line}] Expected a name, got {t.type.name} ({t.value!r})")

    def at_end(self):
        t = self.peek()
        return t is None or t.type == TokenType.EOF

    # ── Type param list  [T, U: Constraint] ──────────────────────────────────

    def parse_type_params(self):
        params = []
        if self.check(TokenType.LBRACKET):
            self.advance()
            while not self.check(TokenType.RBRACKET) and not self.at_end():
                name = self.expect(TokenType.IDENTIFIER).value
                constraint = None
                if self.check(TokenType.COLON):
                    self.advance()
                    constraint = self.expect(TokenType.IDENTIFIER).value
                params.append((name, constraint))
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RBRACKET)
        return params

    # ── Parse type annotation (may include generics) ──────────────────────────

    def parse_type_ann(self):
        if not self.check(TokenType.IDENTIFIER):
            return "auto"
        name = self.advance().value
        if self.check(TokenType.LT):
            self.advance()
            inner = self.parse_type_ann()
            extras = []
            while self.match(TokenType.COMMA):
                extras.append(self.parse_type_ann())
            self.match(TokenType.GT)
            args = [inner] + extras
            return f"{name}<{','.join(args)}>"
        return name

    # ── Program entry ─────────────────────────────────────────────────────────

    def parse(self):
        stmts = []
        while not self.at_end():
            s = self.parse_top_level()
            if s:
                stmts.append(s)
        return Program(stmts)

    def parse_top_level(self):
        t = self.peek()
        if t is None:
            return None

        # Module declaration
        if t.type == TokenType.KW_MODULE:
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            return ModuleDecl(name, t.line)

        # Import statement
        if t.type == TokenType.KW_IMPORT:
            return self.parse_import()

        # Export
        if t.type == TokenType.KW_EXPORT:
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            return ExportStmt(name, t.line)

        return self.parse_stmt()

    def parse_import(self):
        line = self.peek().line
        self.advance()  # import
        # import -> { std::io, std::collections::{List,Map} }
        if self.check(TokenType.ARROW):
            self.advance()
            self.expect(TokenType.LBRACE)
            modules = []
            while not self.check(TokenType.RBRACE) and not self.at_end():
                mod = self._read_module_path()
                modules.append(mod)
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RBRACE)
            return ImportStmt(modules, [], line=line)
        # import module_name
        mod = self._read_module_path()
        return ImportStmt([mod], [], line=line)

    def _read_module_path(self):
        parts = [self.expect(TokenType.IDENTIFIER).value]
        while self.check(TokenType.DOUBLE_COLON):
            self.advance()
            if self.check(TokenType.LBRACE):
                # destructuring: {List, Map}
                self.advance()
                items = []
                while not self.check(TokenType.RBRACE) and not self.at_end():
                    items.append(self.expect(TokenType.IDENTIFIER).value)
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RBRACE)
                return '::'.join(parts) + '::{' + ','.join(items) + '}'
            parts.append(self.expect(TokenType.IDENTIFIER).value)
        return '::'.join(parts)

    # ── Statement dispatch ────────────────────────────────────────────────────

    def parse_stmt(self):
        t = self.peek()
        if t is None:
            return None

        # Function definition  ++
        if t.type == TokenType.KW_FN:
            return self.parse_fn(is_static=False, is_export=False)

        # @@override  fn
        if t.type == TokenType.DOUBLE_AT:
            self.advance()
            fn = self.parse_fn()
            return OverrideDecl(fn, t.line)

        # class / struct / trait / impl
        if t.type == TokenType.KW_CLASS:
            return self.parse_class()
        if t.type == TokenType.KW_STRUCT:
            return self.parse_struct()
        if t.type == TokenType.KW_TRAIT:
            return self.parse_trait()
        if t.type == TokenType.KW_IMPL:
            return self.parse_impl()

        # export ++ fn
        if t.type == TokenType.KW_EXPORT:
            self.advance()
            fn = self.parse_fn(is_export=True)
            return fn

        # Return  <-
        if t.type == TokenType.KW_RETURN:
            self.advance()
            val = None
            if not self.check(TokenType.RBRACE, TokenType.EOF):
                val = self.parse_expr()
            return ReturnStmt(val, t.line)

        # If  ??
        if t.type == TokenType.KW_IF:
            return self.parse_if()

        # For  <>
        if t.type == TokenType.KW_FOR:
            return self.parse_for()

        # While  (when lexer gives KW_WHILE via identifier 'while')
        if t.type == TokenType.KW_WHILE:
            return self.parse_while()

        # Pattern match  ?~
        if t.type == TokenType.KW_MATCH:
            return self.parse_match()

        # Break / Continue
        if t.type == TokenType.KW_BREAK:
            self.advance(); return BreakStmt(t.line)
        if t.type == TokenType.KW_CONTINUE:
            self.advance(); return ContinueStmt(t.line)

        # Panic  !!
        if t.type == TokenType.KW_PANIC:
            self.advance()
            msg = self.parse_expr() if not self.check(TokenType.RBRACE, TokenType.EOF) else Literal("panic", t.line)
            return PanicStmt(msg, t.line)

        # Pipe statement  ~> expr
        if t.type == TokenType.KW_PIPE:
            return self.parse_pipe_stmt()

        # Go coroutine
        if t.type == TokenType.KW_GO:
            self.advance()
            call = self.parse_expr()
            return GoStmt(call, t.line)

        # Try / catch
        if t.type == TokenType.KW_TRY:
            return self.parse_try_catch()

        # Variable declaration: name := ...  or  name :: mut Type = ...
        if t.type == TokenType.IDENTIFIER:
            nxt = self.peek(1)
            if nxt and nxt.type == TokenType.KW_LET:
                return self.parse_var_decl()
            if nxt and nxt.type == TokenType.DOUBLE_COLON:
                return self.parse_var_decl()

        # Ownership declarations  own<T> x := ...  share<T> x := ...  borrow<T> x := ...
        if t.type in (TokenType.KW_OWN, TokenType.KW_SHARE, TokenType.KW_BORROW):
            return self.parse_ownership_decl()

        # Macro invocation  @macro_tok  @macro_ast
        if t.type == TokenType.KW_MACRO:
            return self.parse_macro()

        # Reflect  @reflect
        if t.type == TokenType.KW_REFLECT:
            self.advance()
            target = self.parse_expr()
            return ReflectExpr(target, t.line)

        # Module / import inside body
        if t.type == TokenType.KW_MODULE:
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            return ModuleDecl(name, t.line)
        if t.type == TokenType.KW_IMPORT:
            return self.parse_import()
        if t.type == TokenType.KW_EXPORT:
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            return ExportStmt(name, t.line)

        # Expression statement
        expr = self.parse_expr()
        return expr

    # ── ~> statement ─────────────────────────────────────────────────────────

    def parse_pipe_stmt(self):
        line = self.peek().line
        self.advance()  # ~>
        expr = self.parse_expr()
        return PipeStmt(expr, line)

    # ── Variable declaration ──────────────────────────────────────────────────

    def parse_var_decl(self):
        name = self.advance().value
        is_mut = False
        var_type = "auto"

        if self.check(TokenType.KW_LET):
            self.advance()  # :=
        elif self.check(TokenType.DOUBLE_COLON):
            self.advance()  # ::
            if self.check(TokenType.KW_MUT):
                self.advance(); is_mut = True
            var_type = self.parse_type_ann()
            if self.check(TokenType.ASSIGN):
                self.advance()
            elif not self.check(TokenType.RBRACE, TokenType.EOF):
                pass

        value = self.parse_expr()
        return VarDecl(name, var_type, value, is_mut, None, 0)

    # ── Ownership declaration ─────────────────────────────────────────────────

    def parse_ownership_decl(self):
        kind_tok = self.advance()  # own / share / borrow
        kind = kind_tok.value
        lifetime = None
        inner_type = "auto"
        # own<T>  or  own<'a, T>
        if self.check(TokenType.LT):
            self.advance()
            if self.check(TokenType.LIFETIME):
                lifetime = self.advance().value
                self.match(TokenType.COMMA)
            inner_type = self.parse_type_ann()
            self.match(TokenType.GT)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.KW_LET)  # :=
        value = self.parse_expr()
        node = VarDecl(name, inner_type, value, True, kind, kind_tok.line)
        return node

    # ── Function definition ───────────────────────────────────────────────────

    def parse_fn(self, is_static=False, is_export=False):
        line = self.peek().line
        self.advance()  # ++
        name = self.expect_name().value
        type_params = self.parse_type_params()

        params = []
        # <~  param list  (now a proper token KW_PARAM_ARROW)
        if self.check(TokenType.KW_PARAM_ARROW):
            self.advance()  # consume <~
            self.expect(TokenType.LPAREN)
            params = self.parse_param_list()
            self.expect(TokenType.RPAREN)
        elif self.check(TokenType.LPAREN):
            self.advance()
            params = self.parse_param_list()
            self.expect(TokenType.RPAREN)

        ret_type = "void"
        if self.check(TokenType.ARROW):
            self.advance()
            ret_type = self.parse_type_ann()

        # ** {
        self.match(TokenType.POW)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        return FnDef(name, type_params, params, ret_type, body, is_static, is_export, line)

    def parse_param_list(self):
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                ownership = None
                if self.check(TokenType.KW_OWN, TokenType.KW_SHARE, TokenType.KW_BORROW):
                    ownership = self.advance().value
                pname = self.expect(TokenType.IDENTIFIER).value
                ptype = "auto"
                if self.check(TokenType.COLON):
                    self.advance()
                    ptype = self.parse_type_ann()
                default = None
                if self.check(TokenType.ASSIGN):
                    self.advance()
                    default = self.parse_expr()
                params.append((pname, ptype, ownership, default))
                if not self.match(TokenType.COMMA):
                    break
        return params

    # ── Class ─────────────────────────────────────────────────────────────────

    def parse_class(self):
        line = self.peek().line
        self.advance()  # class
        name = self.expect(TokenType.IDENTIFIER).value
        type_params = self.parse_type_params()
        parents = []
        traits = []
        # : Parent1, Parent2
        if self.check(TokenType.COLON):
            self.advance()
            parents.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                parents.append(self.expect(TokenType.IDENTIFIER).value)
        # impl Trait1, Trait2
        if self.peek() and self.peek().type == TokenType.KW_IMPL:
            self.advance()
            traits.append(self.expect(TokenType.IDENTIFIER).value)
            while self.match(TokenType.COMMA):
                traits.append(self.expect(TokenType.IDENTIFIER).value)
        self.match(TokenType.ARROW)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        return ClassDef(name, type_params, parents, traits, body, line)

    # ── Struct ────────────────────────────────────────────────────────────────

    def parse_struct(self):
        line = self.peek().line
        self.advance()  # struct
        name = self.expect(TokenType.IDENTIFIER).value
        type_params = self.parse_type_params()
        self.match(TokenType.ARROW)
        self.expect(TokenType.LBRACE)
        fields = []
        while not self.check(TokenType.RBRACE) and not self.at_end():
            fname = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            ftype = self.parse_type_ann()
            fields.append((fname, ftype))
            self.match(TokenType.COMMA)
        self.expect(TokenType.RBRACE)
        return StructDef(name, type_params, fields, line)

    # ── Trait ─────────────────────────────────────────────────────────────────

    def parse_trait(self):
        line = self.peek().line
        self.advance()  # trait
        name = self.expect(TokenType.IDENTIFIER).value
        type_params = self.parse_type_params()
        self.match(TokenType.ARROW)
        self.expect(TokenType.LBRACE)
        methods = self.parse_block()
        return TraitDef(name, type_params, methods, line)

    # ── Impl ─────────────────────────────────────────────────────────────────

    def parse_impl(self):
        line = self.peek().line
        self.advance()  # impl
        trait_name = None
        type_name = self.expect(TokenType.IDENTIFIER).value
        # impl Trait for Type
        if self.peek() and self.peek().value == 'for':
            self.advance()
            trait_name = type_name
            type_name = self.expect(TokenType.IDENTIFIER).value
        self.match(TokenType.ARROW)
        self.expect(TokenType.LBRACE)
        methods = self.parse_block()
        return ImplBlock(type_name, trait_name, methods, line)

    # ── If ────────────────────────────────────────────────────────────────────

    def parse_if(self):
        line = self.peek().line
        self.advance()  # ??
        cond = self.parse_expr()
        self.match(TokenType.POW)
        self.expect(TokenType.LBRACE)
        then_body = self.parse_block()

        elif_clauses = []
        else_body = []

        # Look for -- elif / -- else
        while self.check(TokenType.MINUS):
            saved = self.pos
            self.advance()  # first -
            if not self.check(TokenType.MINUS):
                self.pos = saved; break
            self.advance()  # second -
            kw = self.peek()
            if kw and kw.value == 'elif':
                self.advance()
                elif_cond = self.parse_expr()
                self.match(TokenType.POW)
                self.expect(TokenType.LBRACE)
                elif_body = self.parse_block()
                elif_clauses.append((elif_cond, elif_body))
            elif kw and kw.value in ('else', 'default'):
                self.advance()
                self.match(TokenType.POW)
                self.expect(TokenType.LBRACE)
                else_body = self.parse_block()
                break
            else:
                self.pos = saved; break

        return IfStmt(cond, then_body, elif_clauses, else_body, line)

    # ── For ───────────────────────────────────────────────────────────────────

    def parse_for(self):
        line = self.peek().line
        self.advance()  # <>
        var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.DOUBLE_COLON)
        iterable = self.parse_expr()
        self.match(TokenType.POW)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        return ForStmt(var_name, iterable, body, line)

    # ── While ─────────────────────────────────────────────────────────────────

    def parse_while(self):
        line = self.peek().line
        self.advance()  # while keyword
        cond = self.parse_expr()
        self.match(TokenType.POW)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        return WhileStmt(cond, body, line)

    # ── Pattern match  ?~ ─────────────────────────────────────────────────────

    def parse_match(self):
        line = self.peek().line
        self.advance()  # ?~
        value = self.parse_expr()
        self.expect(TokenType.LBRACE)
        arms = []
        while not self.check(TokenType.RBRACE) and not self.at_end():
            pattern = self.parse_pattern()
            guard = None
            if self.peek() and self.peek().value == 'if':
                self.advance()
                guard = self.parse_expr()
            self.expect(TokenType.FAT_ARROW)
            # Single expr or block
            if self.check(TokenType.LBRACE):
                self.advance()
                body = self.parse_block()
            else:
                body = [self.parse_stmt()]
            arms.append(MatchArm(pattern, guard, body, line))
            self.match(TokenType.COMMA)
        self.expect(TokenType.RBRACE)
        return MatchStmt(value, arms, line)

    def parse_pattern(self):
        t = self.peek()
        # Wildcard _
        if t and t.type == TokenType.IDENTIFIER and t.value == '_':
            self.advance()
            return WildcardPattern()
        # Literal numbers / strings / booleans
        if t and t.type in (TokenType.NUMBER, TokenType.STRING, TokenType.BOOLEAN, TokenType.NONE):
            self.advance()
            return LiteralPattern(t.value, t.line)
        # Range  lo..hi  or  lo..=hi
        if t and t.type == TokenType.NUMBER:
            lo = self.advance().value
            if self.check(TokenType.DOTDOT):
                self.advance()
                inclusive = False
                if self.check(TokenType.ASSIGN):
                    self.advance(); inclusive = True
                hi = self.expect(TokenType.NUMBER).value
                return RangePattern(lo, hi, inclusive, t.line)
            return LiteralPattern(lo, t.line)
        # Tuple pattern  (a, b)
        if t and t.type == TokenType.LPAREN:
            self.advance()
            elems = []
            while not self.check(TokenType.RPAREN) and not self.at_end():
                elems.append(self.parse_pattern())
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN)
            return TuplePattern(elems, t.line)
        # Binding (variable capture)
        if t and t.type == TokenType.IDENTIFIER:
            name = self.advance().value
            return BindingPattern(name, t.line)
        return WildcardPattern()

    # ── Try / catch ───────────────────────────────────────────────────────────

    def parse_try_catch(self):
        line = self.peek().line
        self.advance()  # try
        self.match(TokenType.POW)
        self.expect(TokenType.LBRACE)
        try_body = self.parse_block()
        catch_var = "err"
        catch_body = []
        if self.check(TokenType.KW_CATCH):
            self.advance()
            if self.check(TokenType.LPAREN):
                self.advance()
                catch_var = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.RPAREN)
            self.match(TokenType.POW)
            self.expect(TokenType.LBRACE)
            catch_body = self.parse_block()
        return TryCatch(try_body, catch_var, catch_body, line)

    # ── Macro ─────────────────────────────────────────────────────────────────

    def parse_macro(self):
        line = self.peek().line
        kind = self.advance().value  # macro_tok / macro_ast
        name = self.expect(TokenType.IDENTIFIER).value
        args = []
        if self.check(TokenType.LPAREN):
            self.advance()
            while not self.check(TokenType.RPAREN) and not self.at_end():
                args.append(self.parse_expr())
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN)
        return MacroInvoke(kind, name, args, line)

    # ── Block ─────────────────────────────────────────────────────────────────

    def parse_block(self):
        stmts = []
        while not self.check(TokenType.RBRACE) and not self.at_end():
            s = self.parse_stmt()
            if s is not None:
                stmts.append(s)
        self.match(TokenType.RBRACE)
        return stmts

    # ── Expressions ───────────────────────────────────────────────────────────

    def parse_expr(self):
        return self.parse_assign()

    def parse_assign(self):
        left = self.parse_or()
        if self.check(TokenType.ASSIGN, TokenType.PLUS_EQ, TokenType.MINUS_EQ,
                      TokenType.STAR_EQ, TokenType.SLASH_EQ):
            op = self.advance()
            right = self.parse_assign()
            return Assign(left, right, op.value, op.line)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.check(TokenType.OR):
            op = self.advance()
            right = self.parse_and()
            left = BinaryOp(left, '||', right, op.line)
        return left

    def parse_and(self):
        left = self.parse_compare()
        while self.check(TokenType.AND):
            op = self.advance()
            right = self.parse_compare()
            left = BinaryOp(left, '&&', right, op.line)
        return left

    def parse_compare(self):
        left = self.parse_add()
        while self.check(TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT,
                         TokenType.LTE, TokenType.GTE):
            op = self.advance()
            right = self.parse_add()
            left = BinaryOp(left, op.value, right, op.line)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_mul()
            left = BinaryOp(left, op.value, right, op.line)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.check(TokenType.STAR, TokenType.SLASH, TokenType.MOD):
            op = self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op.value, right, op.line)
        return left

    def parse_unary(self):
        if self.check(TokenType.MINUS, TokenType.NOT):
            op = self.advance()
            return UnaryOp(op.value, self.parse_unary(), op.line)
        if self.check(TokenType.KW_AWAIT):
            op = self.advance()
            return AwaitExpr(self.parse_unary(), op.line)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.check(TokenType.COLON):
                # obj:method(...)
                line = self.peek().line
                self.advance()
                method = self.expect_name().value
                type_args = []
                if self.check(TokenType.LT):
                    self.advance()
                    type_args.append(self.parse_type_ann())
                    while self.match(TokenType.COMMA):
                        type_args.append(self.parse_type_ann())
                    self.match(TokenType.GT)
                self.expect(TokenType.LPAREN)
                args = self.parse_arg_list()
                expr = MethodCall(expr, method, args, type_args, line)
            elif self.check(TokenType.DOT):
                line = self.peek().line
                self.advance()
                field = self.expect_name().value
                if self.check(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arg_list()
                    expr = MethodCall(expr, field, args, [], line)
                else:
                    expr = FieldAccess(expr, field, line)
            elif self.check(TokenType.LBRACKET):
                line = self.peek().line
                self.advance()
                idx = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                expr = IndexAccess(expr, idx, line)
            elif self.check(TokenType.LPAREN):
                # Call expression: e.g. @.method() or expr()
                line = self.peek().line
                self.advance()
                args = self.parse_arg_list()
                if isinstance(expr, FieldAccess):
                    expr = MethodCall(expr.obj, expr.field, args, [], line)
                elif isinstance(expr, VarRef):
                    expr = FnCall(expr.name, args, [], line)
                else:
                    expr = MethodCall(expr, '__call__', args, [], line)
            elif self.check(TokenType.DOUBLE_COLON):
                line = self.peek().line
                self.advance()
                nxt = self.peek()
                if nxt and (nxt.type == TokenType.IDENTIFIER or
                            (nxt.value and str(nxt.value).replace('_', '').isalnum())):
                    method = self.advance().value
                    if isinstance(expr, VarRef):
                        full = expr.name + '::' + method
                    else:
                        full = '::' + method
                    if self.check(TokenType.LPAREN):
                        self.advance()
                        args = self.parse_arg_list()
                        expr = FnCall(full, args, [], line)
                    else:
                        expr = VarRef(full, line)
                else:
                    break
            else:
                break
        return expr

    def parse_primary(self):
        t = self.peek()
        if t is None:
            return None

        if t.type == TokenType.NUMBER:
            self.advance(); return Literal(t.value, t.line)
        if t.type == TokenType.STRING:
            self.advance(); return Literal(t.value, t.line)
        if t.type == TokenType.BOOLEAN:
            self.advance(); return Literal(t.value, t.line)
        if t.type == TokenType.NONE:
            self.advance(); return Literal(None, t.line)

        # Self reference @.field  or  @
        if t.type == TokenType.AT:
            self.advance()
            if self.check(TokenType.DOT):
                self.advance()
                field = self.expect(TokenType.IDENTIFIER).value
                return FieldAccess(SelfRef(t.line), field, t.line)
            return SelfRef(t.line)

        # Parenthesized or tuple
        if t.type == TokenType.LPAREN:
            self.advance()
            first = self.parse_expr()
            if self.check(TokenType.COMMA):
                elems = [first]
                while self.match(TokenType.COMMA):
                    if self.check(TokenType.RPAREN):
                        break
                    elems.append(self.parse_expr())
                self.expect(TokenType.RPAREN)
                return TupleLiteral(elems, t.line)
            self.expect(TokenType.RPAREN)
            return first

        # List literal
        if t.type == TokenType.LBRACKET:
            self.advance()
            elems = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elems.append(self.parse_expr())
                    if not self.match(TokenType.COMMA):
                        break
            self.expect(TokenType.RBRACKET)
            return ListLiteral(elems, t.line)

        # Map literal  { key: val, ... }  (only if first token after { is IDENTIFIER : )
        if t.type == TokenType.LBRACE:
            saved = self.pos
            self.advance()
            if self.check(TokenType.RBRACE):
                self.advance()
                return MapLiteral([], t.line)
            if self.check(TokenType.IDENTIFIER) and self.peek(1) and self.peek(1).type == TokenType.COLON:
                pairs = []
                while not self.check(TokenType.RBRACE) and not self.at_end():
                    key = self.expect(TokenType.IDENTIFIER).value
                    self.expect(TokenType.COLON)
                    val = self.parse_expr()
                    pairs.append((key, val))
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RBRACE)
                return MapLiteral(pairs, t.line)
            self.pos = saved

        # Ownership expression  own<T> expr
        if t.type in (TokenType.KW_OWN, TokenType.KW_SHARE, TokenType.KW_BORROW):
            kind = self.advance().value
            inner_type = "auto"
            if self.check(TokenType.LT):
                self.advance()
                inner_type = self.parse_type_ann()
                self.match(TokenType.GT)
            inner = self.parse_primary()
            return OwnershipExpr(kind, inner, None, t.line)

        # Result::Ok / Result::Err
        if t.type == TokenType.IDENTIFIER and t.value in ('Ok', 'Err'):
            self.advance()
            if self.check(TokenType.LPAREN):
                self.advance()
                val = self.parse_expr()
                self.expect(TokenType.RPAREN)
                if t.value == 'Ok':
                    return ResultOk(val, t.line)
                return ResultErr(val, t.line)
            return VarRef(t.value, t.line)

        # Identifier: fn call, static call, or var ref
        if t.type == TokenType.IDENTIFIER:
            name = self.advance().value

            # Static call  TypeName::method(...)  or  std::io::println(...)
            if self.check(TokenType.DOUBLE_COLON):
                parts = [name]
                while self.check(TokenType.DOUBLE_COLON):
                    self.advance()
                    nxt = self.peek()
                    if nxt and (nxt.type == TokenType.IDENTIFIER or
                                (nxt.value and str(nxt.value).replace('_', '').isalnum())):
                        parts.append(self.advance().value)
                full = '::'.join(parts)
                if self.check(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arg_list()
                    return FnCall(full, args, [], t.line)
                return VarRef(full, t.line)

            # Generic fn call  name<T>(args)
            type_args = []
            if self.check(TokenType.LT) and self._looks_like_type_arg():
                self.advance()
                type_args.append(self.parse_type_ann())
                while self.match(TokenType.COMMA):
                    type_args.append(self.parse_type_ann())
                self.match(TokenType.GT)

            # Function call
            if self.check(TokenType.LPAREN):
                self.advance()
                args = self.parse_arg_list()
                return FnCall(name, args, type_args, t.line)

            return VarRef(name, t.line)

        # Macro invocation inside expression
        if t.type == TokenType.KW_MACRO:
            return self.parse_macro()

        # Reflect inside expression
        if t.type == TokenType.KW_REFLECT:
            self.advance()
            target = self.parse_expr()
            return ReflectExpr(target, t.line)

        # Skip unknown token
        self.advance()
        return None

    def _looks_like_type_arg(self):
        """Heuristic: peek past < to see if it looks like a type param list."""
        i = self.pos + 1
        depth = 1
        while i < len(self.tokens) and depth > 0:
            tt = self.tokens[i].type
            if tt == TokenType.LT:
                depth += 1
            elif tt == TokenType.GT:
                depth -= 1
            elif tt in (TokenType.EOF, TokenType.SEMICOLON, TokenType.LBRACE):
                return False
            i += 1
        return depth == 0

    def parse_arg_list(self):
        args = []
        if not self.check(TokenType.RPAREN):
            while True:
                args.append(self.parse_expr())
                if not self.match(TokenType.COMMA):
                    break
        self.match(TokenType.RPAREN)
        return args
