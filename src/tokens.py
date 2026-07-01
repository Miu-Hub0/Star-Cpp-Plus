"""CP+* Token Types - Extended for Advanced Features"""
from enum import Enum, auto


class TokenType(Enum):
    # Variable declaration
    KW_LET = auto()        # :=
    KW_VAR = auto()        # :: mut
    KW_MUT = auto()        # mut

    # Control flow
    KW_IF = auto()         # ??
    KW_ELSE = auto()       # -- else
    KW_FOR = auto()        # <>
    KW_WHILE = auto()      # <> while
    KW_BREAK = auto()      # !>
    KW_CONTINUE = auto()   # !>>
    KW_RETURN = auto()     # <-
    KW_MATCH = auto()      # ?~  (pattern match)
    KW_PIPE = auto()       # ~>  (statement / pipe / match arm)

    # Functions & types
    KW_FN = auto()         # ++
    KW_PARAM_ARROW = auto() # <~
    KW_CLASS = auto()      # class
    KW_STRUCT = auto()     # struct
    KW_TRAIT = auto()      # trait
    KW_IMPL = auto()       # impl
    KW_SELF = auto()       # @
    KW_NEW = auto()        # new
    KW_STATIC = auto()     # static
    KW_OVERRIDE = auto()   # @@override

    # Ownership & memory
    KW_OWN = auto()        # own
    KW_SHARE = auto()      # share
    KW_BORROW = auto()     # borrow
    KW_MOVE = auto()       # move
    KW_SYSTEM = auto()     # @system

    # Error handling
    KW_PANIC = auto()      # !!
    KW_TRY = auto()        # try
    KW_CATCH = auto()      # catch

    # Module system
    KW_MODULE = auto()     # module
    KW_IMPORT = auto()     # import
    KW_EXPORT = auto()     # export
    KW_FROM = auto()       # from

    # Concurrency
    KW_GO = auto()         # go
    KW_AWAIT = auto()      # await
    KW_ASYNC = auto()      # async
    KW_CHANNEL = auto()    # chan

    # Generics / macros / reflection
    KW_WHERE = auto()      # where
    KW_MACRO = auto()      # @macro_tok / @macro_ast
    KW_REFLECT = auto()    # @reflect

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NONE = auto()

    # Brackets
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    LANGLE = auto()        # <  (generic open)
    RANGLE = auto()        # >  (generic close)

    # Punctuation
    COLON = auto()         # :
    DOUBLE_COLON = auto()  # ::
    COMMA = auto()         # ,
    DOT = auto()           # .
    DOTDOT = auto()        # ..
    DOTDOTEQ = auto()      # ..=
    AT = auto()            # @
    DOUBLE_AT = auto()     # @@
    ARROW = auto()         # ->
    FAT_ARROW = auto()     # =>
    SEMICOLON = auto()     # ;
    QUESTION = auto()      # ?
    EXCLAMATION = auto()   # !
    HASH = auto()          # #
    PIPE = auto()          # |
    AMP = auto()           # &
    TILDE = auto()         # ~
    LIFETIME = auto()      # 'a  lifetime annotation

    # Arithmetic operators
    PLUS = auto()          # +
    MINUS = auto()         # -
    STAR = auto()          # *
    SLASH = auto()         # /
    MOD = auto()           # %
    POW = auto()           # **

    # Assignment operators
    ASSIGN = auto()        # =
    PLUS_EQ = auto()       # +=
    MINUS_EQ = auto()      # -=
    STAR_EQ = auto()       # *=
    SLASH_EQ = auto()      # /=

    # Comparison operators
    EQ = auto()            # ==
    NEQ = auto()           # !=
    LT = auto()            # <
    GT = auto()            # >
    LTE = auto()           # <=
    GTE = auto()           # >=

    # Logical operators
    AND = auto()           # &&
    OR = auto()            # ||
    NOT = auto()           # !

    # Special
    EOF = auto()


class Token:
    def __init__(self, type: TokenType, value, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r} L{self.line}:{self.column})"


KEYWORDS = {
    "true":   TokenType.BOOLEAN,
    "false":  TokenType.BOOLEAN,
    "none":   TokenType.NONE,
    "mut":    TokenType.KW_MUT,
    "new":    TokenType.KW_NEW,
    "go":     TokenType.KW_GO,
    "await":  TokenType.KW_AWAIT,
    "async":  TokenType.KW_ASYNC,
    "own":    TokenType.KW_OWN,
    "share":  TokenType.KW_SHARE,
    "borrow": TokenType.KW_BORROW,
    "move":   TokenType.KW_MOVE,
    "static": TokenType.KW_STATIC,
    "impl":   TokenType.KW_IMPL,
    "class":  TokenType.KW_CLASS,
    "struct": TokenType.KW_STRUCT,
    "trait":  TokenType.KW_TRAIT,
    "where":  TokenType.KW_WHERE,
    "try":    TokenType.KW_TRY,
    "catch":  TokenType.KW_CATCH,
    "module": TokenType.KW_MODULE,
    "import": TokenType.KW_IMPORT,
    "export": TokenType.KW_EXPORT,
    "from":   TokenType.KW_FROM,
    "else":   TokenType.KW_ELSE,
}
