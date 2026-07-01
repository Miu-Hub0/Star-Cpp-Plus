"""CP+* Parser - Tokens → AST"""
from tokens import Token, TokenType

class ASTNode: pass

class Program(ASTNode):
    def __init__(self, stmts): self.statements = stmts

class VarDecl(ASTNode):
    def __init__(self, name, var_type, value, is_mut, line):
        self.name=name; self.var_type=var_type; self.value=value
        self.is_mutable=is_mut; self.line=line

class FnDef(ASTNode):
    def __init__(self, name, params, ret_type, body, line):
        self.name=name; self.params=params; self.return_type=ret_type
        self.body=body; self.line=line

class ClassDef(ASTNode):
    def __init__(self, name, parent, body, line):
        self.name=name; self.parent=parent; self.body=body; self.line=line

class ReturnStmt(ASTNode):
    def __init__(self, value, line): self.value=value; self.line=line

class IfStmt(ASTNode):
    def __init__(self, cond, then_body, else_body, line):
        self.condition=cond; self.then_body=then_body
        self.else_body=else_body; self.line=line

class ForStmt(ASTNode):
    def __init__(self, var, iterable, body, line):
        self.var_name=var; self.iterable=iterable; self.body=body; self.line=line

class WhileStmt(ASTNode):
    def __init__(self, cond, body, line):
        self.condition=cond; self.body=body; self.line=line

class FnCall(ASTNode):
    def __init__(self, name, args, line):
        self.name=name; self.args=args; self.line=line

class MethodCall(ASTNode):
    def __init__(self, obj, method, args, line):
        self.obj=obj; self.method=method; self.args=args; self.line=line

class VarRef(ASTNode):
    def __init__(self, name, line): self.name=name; self.line=line

class Literal(ASTNode):
    def __init__(self, value, line): self.value=value; self.line=line

class BinaryOp(ASTNode):
    def __init__(self, left, op, right, line):
        self.left=left; self.op=op; self.right=right; self.line=line

class UnaryOp(ASTNode):
    def __init__(self, op, operand, line): self.op=op; self.operand=operand; self.line=line

class Assign(ASTNode):
    def __init__(self, target, value, line): self.target=target; self.value=value; self.line=line

class SelfRef(ASTNode):
    def __init__(self, line): self.line=line

class FieldAccess(ASTNode):
    def __init__(self, obj, field, line): self.obj=obj; self.field=field; self.line=line

class BreakStmt(ASTNode): pass
class ContinueStmt(ASTNode): pass
class ListLiteral(ASTNode):
    def __init__(self, elems, line): self.elements=elems; self.line=line

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def advance(self): t = self.peek(); self.pos += 1; return t
    def expect(self, tt, msg=""):
        t = self.peek()
        if not t or t.type != tt:
            raise Exception(f"Parser Error L{t.line if t else '?'}: Expected {tt.name}, got {t.type.name if t else 'EOF'}. {msg}")
        return self.advance()
    
    def parse(self):
        stmts = []
        while self.peek() and self.peek().type != TokenType.EOF:
            s = self.parse_stmt()
            if s: stmts.append(s)
        return Program(stmts)
    
    def parse_stmt(self):
        t = self.peek()
        if not t: return None
        
        # Function: ++
        if t.type == TokenType.KW_FN:
            return self.parse_fn()
        
        # Class: +* (đã bị lexer skip, nhưng nếu có IDENTIFIER class/struct/trait)
        if t.type == TokenType.IDENTIFIER and t.value in ('class','struct','trait'):
            return self.parse_class()
        
        # Variable declaration
        if t.type == TokenType.IDENTIFIER:
            nxt = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None
            if nxt and nxt.type == TokenType.KW_LET:
                return self.parse_var_decl()
            if nxt and nxt.type == TokenType.DOUBLE_COLON:
                return self.parse_var_decl()
        
        # Return
        if t.type == TokenType.KW_RETURN:
            self.advance()
            val = self.parse_expr() if self.peek() and self.peek().type not in (TokenType.RBRACE, TokenType.EOF) else None
            return ReturnStmt(val, t.line)
        
        # If
        if t.type == TokenType.KW_IF:
            return self.parse_if()
        
        # For/While
        if t.type == TokenType.KW_FOR:
            return self.parse_for()
        
        # Break/Continue
        if t.type == TokenType.KW_BREAK:
            self.advance(); return BreakStmt()
        if t.type == TokenType.KW_CONTINUE:
            self.advance(); return ContinueStmt()
        
        # Expression statement
        expr = self.parse_expr()
        return expr
    
    def parse_var_decl(self):
        name = self.advance().value
        is_mut = False
        var_type = "auto"
        
        if self.peek().type == TokenType.KW_LET:
            self.advance()  # :=
        elif self.peek().type == TokenType.DOUBLE_COLON:
            self.advance()  # ::
            if self.peek().value == 'mut':
                self.advance()
                is_mut = True
            if self.peek().type == TokenType.IDENTIFIER:
                var_type = self.advance().value
            if self.peek().type == TokenType.ASSIGN:
                self.advance()
        
        value = self.parse_expr()
        return VarDecl(name, var_type, value, is_mut, 0)
    
    def parse_fn(self):
        self.advance()  # ++
        name = self.expect(TokenType.IDENTIFIER).value
        
        # <~ (params) ->
        params = []
        if self.peek().value == '<~':
            self.advance()
            self.expect(TokenType.LPAREN)
            if self.peek().type != TokenType.RPAREN:
                while True:
                    pname = self.expect(TokenType.IDENTIFIER).value
                    self.expect(TokenType.COLON)
                    ptype = self.expect(TokenType.IDENTIFIER).value
                    params.append((pname, ptype))
                    if self.peek().type == TokenType.COMMA:
                        self.advance()
                    else:
                        break
            self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.ARROW)
        ret_type = self.expect(TokenType.IDENTIFIER).value
        
        # ** {
        if self.peek().type == TokenType.POW:
            self.advance()
        self.expect(TokenType.LBRACE)
        
        body = self.parse_block()
        return FnDef(name, params, ret_type, body, 0)
    
    def parse_class(self):
        kw = self.advance().value  # class/struct/trait
        name = self.expect(TokenType.IDENTIFIER).value
        parent = None
        if self.peek().type == TokenType.COLON:
            self.advance()
            parent = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.ARROW)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        return ClassDef(name, parent, body, 0)
    
    def parse_if(self):
        self.advance()  # ??
        cond = self.parse_expr()
        
        if self.peek().type == TokenType.POW: self.advance()
        self.expect(TokenType.LBRACE)
        then_body = self.parse_block()
        
        else_body = []
        if self.peek() and self.peek().type == TokenType.MINUS:
            # Check for -- else
            if self.tokens[self.pos+1] and self.tokens[self.pos+1].type == TokenType.MINUS:
                self.advance(); self.advance()
                if self.peek().value == 'else':
                    self.advance()
                    if self.peek().type == TokenType.POW: self.advance()
                    self.expect(TokenType.LBRACE)
                    else_body = self.parse_block()
        
        return IfStmt(cond, then_body, else_body, 0)
    
    def parse_for(self):
        self.advance()  # <>
        var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.DOUBLE_COLON)
        iterable = self.parse_expr()
        
        if self.peek().type == TokenType.POW: self.advance()
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        return ForStmt(var_name, iterable, body, 0)
    
    def parse_block(self):
        stmts = []
        while self.peek() and self.peek().type != TokenType.RBRACE and self.peek().type != TokenType.EOF:
            s = self.parse_stmt()
            if s: stmts.append(s)
        if self.peek() and self.peek().type == TokenType.RBRACE:
            self.advance()
        return stmts
    
    def parse_expr(self):
        return self.parse_binary()
    
    def parse_binary(self, min_prec=0):
        prec = {'||':1,'&&':2,'==':3,'!=':3,'<':4,'>':4,'<=':4,'>=':4,'+':5,'-':5,'*':6,'/':6,'%':6}
        left = self.parse_unary()
        
        while self.peek() and self.peek().type in (TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
                TokenType.SLASH, TokenType.MOD, TokenType.EQ, TokenType.NEQ, TokenType.LT,
                TokenType.GT, TokenType.LTE, TokenType.GTE, TokenType.AND, TokenType.OR):
            op_token = self.peek()
            op_prec = prec.get(op_token.value, 0)
            if op_prec < min_prec: break
            self.advance()
            right = self.parse_binary(op_prec + 1)
            left = BinaryOp(left, op_token.value, right, op_token.line)
        
        return left
    
    def parse_unary(self):
        t = self.peek()
        if t and t.type in (TokenType.MINUS, TokenType.NOT):
            self.advance()
            return UnaryOp(t.value, self.parse_unary(), t.line)
        return self.parse_primary()
    
    def parse_primary(self):
        t = self.peek()
        if not t: return None
        
        # Number
        if t.type == TokenType.NUMBER:
            self.advance()
            return Literal(t.value, t.line)
        
        # String
        if t.type == TokenType.STRING:
            self.advance()
            return Literal(t.value, t.line)
        
        # Boolean
        if t.type == TokenType.BOOLEAN:
            self.advance()
            return Literal(t.value, t.line)
        
        # None
        if t.type == TokenType.NONE:
            self.advance()
            return Literal(None, t.line)
        
        # Self
        if t.type == TokenType.AT:
            self.advance()
            if self.peek() and self.peek().type == TokenType.DOT:
                self.advance()
                field = self.expect(TokenType.IDENTIFIER).value
                return FieldAccess(SelfRef(t.line), field, t.line)
            return SelfRef(t.line)
        
        # Identifier
        if t.type == TokenType.IDENTIFIER:
            name = self.advance().value
            
            # Method call: obj:method(args)
            if self.peek() and self.peek().type == TokenType.COLON:
                self.advance()
                method = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.LPAREN)
                args = self.parse_args()
                return MethodCall(VarRef(name, t.line), method, args, t.line)
            
            # Function call: func(args)
            if self.peek() and self.peek().type == TokenType.LPAREN:
                self.advance()
                args = self.parse_args()
                return FnCall(name, args, t.line)
            
            return VarRef(name, t.line)
        
        # List literal: [ ... ]
        if t.type == TokenType.LBRACKET:
            self.advance()
            elems = []
            if self.peek() and self.peek().type != TokenType.RBRACKET:
                while True:
                    elems.append(self.parse_expr())
                    if self.peek() and self.peek().type == TokenType.COMMA:
                        self.advance()
                    else:
                        break
            self.expect(TokenType.RBRACKET)
            return ListLiteral(elems, t.line)
        
        # Parenthesized
        if t.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr
        
        return None
    
    def parse_args(self):
        args = []
        if self.peek() and self.peek().type != TokenType.RPAREN:
            while True:
                args.append(self.parse_expr())
                if self.peek() and self.peek().type == TokenType.COMMA:
                    self.advance()
                else:
                    break
        if self.peek() and self.peek().type == TokenType.RPAREN:
            self.advance()
        return args