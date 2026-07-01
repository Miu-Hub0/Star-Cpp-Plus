"""CP+* Lexer - Tokenizer"""
from tokens import Token, TokenType, KEYWORDS

class Lexer:
    def __init__(self, source: str, filename: str = "<unknown>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def peek(self, offset=0):
        return self.source[self.pos+offset] if self.pos+offset < len(self.source) else '\0'
    
    def advance(self):
        ch = self.peek()
        self.pos += 1
        self.column += 1
        return ch
    
    def add(self, type, value=None):
        self.tokens.append(Token(type, value, self.line, self.column))
    
    def skip_ws(self):
        while self.peek() in ' \t\r': self.advance()
        while self.peek() == '\n': self.advance(); self.line += 1; self.column = 1
    
    def skip_comment(self):
        if self.peek() == '-' and self.peek(1) == '-':
            if self.peek(2) == '[' and self.peek(3) == '[':
                for _ in range(4): self.advance()
                while not (self.peek()=='-' and self.peek(1)=='-' and self.peek(2)==']' and self.peek(3)==']'):
                    if self.peek()=='\0': raise Exception("Unclosed multi-line comment")
                    if self.peek()=='\n': self.line+=1; self.column=0
                    self.advance()
                for _ in range(4): self.advance()
                return True
            while self.peek() not in ('\n','\0'): self.advance()
            return True
        return False
    
    def skip_directive(self):
        if self.peek() in '+@':
            while self.peek() not in ('\n','\0'): self.advance()
            return True
        return False
    
    def read_string(self):
        self.advance()
        result = []
        while self.peek() not in ('"','\0'):
            if self.peek()=='\\':
                self.advance()
                ch = self.advance()
                result.append({'n':'\n','t':'\t','r':'\r','"':'"','\\':'\\'}.get(ch,ch))
            else:
                if self.peek()=='\n': self.line+=1; self.column=0
                result.append(self.advance())
        if self.peek()=='"': self.advance()
        else: raise Exception(f"Unclosed string at L{self.line}")
        return ''.join(result)
    
    def read_number(self):
        result = []
        while self.peek().isdigit(): result.append(self.advance())
        if self.peek()=='.' and self.peek(1).isdigit():
            result.append(self.advance())
            while self.peek().isdigit(): result.append(self.advance())
        return ''.join(result)
    
    def read_ident(self):
        result = []
        while self.peek().isalnum() or self.peek()=='_': result.append(self.advance())
        return ''.join(result)
    
    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_ws()
            if self.pos >= len(self.source): break
            if self.skip_comment(): continue
            if self.skip_directive(): continue
            
            ch = self.peek()
            
            # Two-char tokens
            two_char_map = {
                ':=': TokenType.KW_LET, '::': TokenType.DOUBLE_COLON,
                '->': TokenType.ARROW, '<-': TokenType.KW_RETURN,
                '??': TokenType.KW_IF, '~>': TokenType.KW_PIPE,
                '<>': TokenType.KW_FOR, '!>': TokenType.KW_BREAK,
                '!!': TokenType.KW_PANIC, '==': TokenType.EQ,
                '!=': TokenType.NEQ, '<=': TokenType.LTE, '>=': TokenType.GTE,
                '&&': TokenType.AND, '||': TokenType.OR,
                '+=': TokenType.PLUS_EQ, '-=': TokenType.MINUS_EQ,
                '*=': TokenType.STAR_EQ, '/=': TokenType.SLASH_EQ,
                '**': TokenType.POW, '..': TokenType.DOTDOT,
                '++': TokenType.KW_FN, '!<': TokenType.KW_RETURN,
            }
            
            two_ch = ch + self.peek(1)
            if two_ch in two_char_map:
                self.advance(); self.advance()
                if two_ch == '!>' and self.peek() == '>':
                    self.advance()
                    self.add(TokenType.KW_CONTINUE, '!>>')
                elif two_ch == '..' and self.peek() == '=':
                    self.advance()
                    self.add(TokenType.DOTDOTEQ, '..=')
                elif two_ch == '+' and self.peek(1) == '*':
                    while self.peek() not in ('\n','\0'): self.advance()
                else:
                    self.add(two_char_map[two_ch], two_ch)
                continue
            
            # Single-char tokens
            single_map = {
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                ':': TokenType.COLON, ',': TokenType.COMMA,
                '.': TokenType.DOT, '@': TokenType.AT,
                ';': TokenType.SEMICOLON, '?': TokenType.QUESTION,
                '+': TokenType.PLUS, '-': TokenType.MINUS,
                '*': TokenType.STAR, '/': TokenType.SLASH,
                '%': TokenType.MOD, '=': TokenType.ASSIGN,
                '<': TokenType.LT, '>': TokenType.GT,
                '!': TokenType.NOT,
            }
            if ch in single_map:
                self.advance()
                self.add(single_map[ch], ch)
                continue
            
            # String
            if ch == '"':
                self.add(TokenType.STRING, self.read_string())
                continue
            
            # Number
            if ch.isdigit():
                num = self.read_number()
                self.add(TokenType.NUMBER, float(num) if '.' in num else int(num))
                continue
            
            # Identifier
            if ch.isalpha() or ch == '_':
                ident = self.read_ident()
                if ident in KEYWORDS:
                    tt = KEYWORDS[ident]
                    self.add(tt, ident == 'true' if tt == TokenType.BOOLEAN else ident)
                else:
                    self.add(TokenType.IDENTIFIER, ident)
                continue
            
            self.advance()  # Skip unknown
        
        self.add(TokenType.EOF, None)
        return self.tokens