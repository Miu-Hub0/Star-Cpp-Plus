"""CP+* Lexer - Extended Tokenizer with Advanced Feature Support"""
from tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str, filename: str = "<unknown>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def peek(self, offset=0):
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else '\0'

    def advance(self):
        ch = self.peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def add(self, typ, value=None):
        self.tokens.append(Token(typ, value, self.line, self.column))

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.peek() in ' \t\r\n':
            self.advance()

    def skip_comment(self):
        # -- [[ multi-line ]]
        if self.peek() == '-' and self.peek(1) == '-':
            # Check if this is -- else / -- elif / -- default (control flow, NOT a comment)
            look = self.pos + 2
            while look < len(self.source) and self.source[look] in ' \t':
                look += 1
            rest = self.source[look:look + 7]
            if (rest.startswith('else') or rest.startswith('elif') or
                    rest.startswith('default')):
                return False  # Treat as two MINUS tokens so the parser can see them

            if self.peek(2) == '[' and self.peek(3) == '[':
                for _ in range(4):
                    self.advance()
                while self.pos < len(self.source):
                    if (self.peek() == '-' and self.peek(1) == '-' and
                            self.peek(2) == ']' and self.peek(3) == ']'):
                        for _ in range(4):
                            self.advance()
                        return True
                    self.advance()
                raise LexerError(f"Unclosed multi-line comment at L{self.line}")
            # single line --
            while self.peek() not in ('\n', '\0'):
                self.advance()
            return True
        return False

    def skip_directive_comment(self):
        # +* ... *+ file headers / block comments
        if self.peek() == '+' and self.peek(1) == '*':
            self.advance(); self.advance()
            while self.pos < len(self.source):
                if self.peek() == '*' and self.peek(1) == '+':
                    self.advance(); self.advance()
                    return True
                self.advance()
            return True
        return False

    def read_string(self):
        self.advance()  # consume opening "
        result = []
        while self.pos < len(self.source) and self.peek() != '"':
            if self.peek() == '\\':
                self.advance()
                esc = self.advance()
                result.append({'n': '\n', 't': '\t', 'r': '\r', '"': '"',
                                '\\': '\\', '0': '\0', '{': '{', '}': '}'}.get(esc, esc))
            else:
                result.append(self.advance())
        if self.peek() == '"':
            self.advance()
        else:
            raise LexerError(f"Unclosed string literal at L{self.line}")
        return ''.join(result)

    def read_char_literal(self):
        self.advance()  # consume '
        ch = self.advance()
        if ch == '\\':
            ch = self.advance()
            ch = {'n': '\n', 't': '\t', 'r': '\r', '\'': '\'', '\\': '\\'}.get(ch, ch)
        if self.peek() == '\'':
            self.advance()
        return ch

    def read_number(self):
        result = []
        is_float = False
        if self.peek() == '0' and self.peek(1) in ('x', 'X'):
            result.append(self.advance())
            result.append(self.advance())
            while self.peek() in '0123456789abcdefABCDEF_':
                ch = self.advance()
                if ch != '_':
                    result.append(ch)
            return int(''.join(result), 16)
        while self.peek().isdigit() or self.peek() == '_':
            ch = self.advance()
            if ch != '_':
                result.append(ch)
        if self.peek() == '.' and self.peek(1).isdigit():
            is_float = True
            result.append(self.advance())
            while self.peek().isdigit():
                result.append(self.advance())
        if self.peek() in ('e', 'E'):
            is_float = True
            result.append(self.advance())
            if self.peek() in ('+', '-'):
                result.append(self.advance())
            while self.peek().isdigit():
                result.append(self.advance())
        s = ''.join(result)
        return float(s) if is_float else int(s)

    def read_ident(self):
        result = []
        while self.peek().isalnum() or self.peek() in ('_',):
            result.append(self.advance())
        return ''.join(result)

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.pos >= len(self.source):
                break

            # +* import / +* export / +* module — keyword blocks, NOT comments.
            # Skip the +* sigil and whitespace so the keyword is tokenized normally.
            if self.peek() == '+' and self.peek(1) == '*':
                look = self.pos + 2
                while look < len(self.source) and self.source[look] in ' \t':
                    look += 1
                rest = self.source[look:look + 10]
                if (rest.startswith('import') or rest.startswith('export') or
                        rest.startswith('module')):
                    self.advance(); self.advance()  # skip +*
                    continue

            if self.skip_directive_comment():
                continue
            if self.skip_comment():
                continue

            ch = self.peek()
            line = self.line
            col = self.column

            # Lifetime annotation  'a
            if ch == '\'' and (self.peek(1).isalpha() or self.peek(1) == '_'):
                self.advance()
                ident = self.read_ident()
                self.tokens.append(Token(TokenType.LIFETIME, ident, line, col))
                continue

            # @@override  @@
            if ch == '@' and self.peek(1) == '@':
                self.advance(); self.advance()
                ident = self.read_ident() if (self.peek().isalpha() or self.peek() == '_') else ''
                self.tokens.append(Token(TokenType.DOUBLE_AT, '@@' + ident, line, col))
                continue

            # @macro_tok  @macro_ast  @reflect  @system  @.field
            if ch == '@':
                self.advance()
                if self.peek() == '.':
                    self.advance()
                    field = self.read_ident()
                    self.tokens.append(Token(TokenType.AT, '@', line, col))
                    self.tokens.append(Token(TokenType.DOT, '.', line, col))
                    self.tokens.append(Token(TokenType.IDENTIFIER, field, line, col))
                elif self.peek().isalpha() or self.peek() == '_':
                    ident = self.read_ident()
                    if ident in ('macro_tok', 'macro_ast'):
                        self.tokens.append(Token(TokenType.KW_MACRO, ident, line, col))
                    elif ident == 'reflect':
                        self.tokens.append(Token(TokenType.KW_REFLECT, ident, line, col))
                    elif ident == 'system':
                        self.tokens.append(Token(TokenType.KW_SYSTEM, ident, line, col))
                    else:
                        self.tokens.append(Token(TokenType.AT, '@', line, col))
                        self.tokens.append(Token(TokenType.IDENTIFIER, ident, line, col))
                else:
                    self.tokens.append(Token(TokenType.AT, '@', line, col))
                continue

            # Three-char tokens
            three = ch + self.peek(1) + self.peek(2)
            three_map = {
                '!>>': TokenType.KW_CONTINUE,
                '..=': TokenType.DOTDOTEQ,
            }
            if three in three_map:
                for _ in range(3):
                    self.advance()
                self.tokens.append(Token(three_map[three], three, line, col))
                continue

            # Two-char tokens
            two = ch + self.peek(1)
            two_map = {
                ':=': TokenType.KW_LET,
                '::': TokenType.DOUBLE_COLON,
                '->': TokenType.ARROW,
                '=>': TokenType.FAT_ARROW,
                '<-': TokenType.KW_RETURN,
                '<~': TokenType.KW_PARAM_ARROW,
                '??': TokenType.KW_IF,
                '?~': TokenType.KW_MATCH,
                '~>': TokenType.KW_PIPE,
                '<>': TokenType.KW_FOR,
                '!>': TokenType.KW_BREAK,
                '!!': TokenType.KW_PANIC,
                '++': TokenType.KW_FN,
                '==': TokenType.EQ,
                '!=': TokenType.NEQ,
                '<=': TokenType.LTE,
                '>=': TokenType.GTE,
                '&&': TokenType.AND,
                '||': TokenType.OR,
                '+=': TokenType.PLUS_EQ,
                '-=': TokenType.MINUS_EQ,
                '*=': TokenType.STAR_EQ,
                '/=': TokenType.SLASH_EQ,
                '**': TokenType.POW,
                '..': TokenType.DOTDOT,
            }
            if two in two_map:
                self.advance(); self.advance()
                self.tokens.append(Token(two_map[two], two, line, col))
                continue

            # Single-char tokens
            single_map = {
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ':': TokenType.COLON,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                ';': TokenType.SEMICOLON,
                '?': TokenType.QUESTION,
                '|': TokenType.PIPE,
                '&': TokenType.AMP,
                '~': TokenType.TILDE,
                '#': TokenType.HASH,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.STAR,
                '/': TokenType.SLASH,
                '%': TokenType.MOD,
                '=': TokenType.ASSIGN,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '!': TokenType.NOT,
            }
            if ch in single_map:
                self.advance()
                self.tokens.append(Token(single_map[ch], ch, line, col))
                continue

            # String literal
            if ch == '"':
                s = self.read_string()
                self.tokens.append(Token(TokenType.STRING, s, line, col))
                continue

            # Char literal
            if ch == '\'':
                c = self.read_char_literal()
                self.tokens.append(Token(TokenType.STRING, c, line, col))
                continue

            # Number
            if ch.isdigit():
                num = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, num, line, col))
                continue

            # Identifier / keyword
            if ch.isalpha() or ch == '_':
                ident = self.read_ident()
                if ident in KEYWORDS:
                    tt = KEYWORDS[ident]
                    val = (True if ident == 'true' else False) if tt == TokenType.BOOLEAN else ident
                    self.tokens.append(Token(tt, val, line, col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, ident, line, col))
                continue

            # Unknown character — skip
            self.advance()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
