"""CP+* Token Types"""
from enum import Enum, auto

class TokenType(Enum):
    KW_LET = auto()        # :=
    KW_VAR = auto()        # :: mut
    KW_IF = auto()         # ??
    KW_ELSE = auto()       # -- else
    KW_FOR = auto()        # <>
    KW_WHILE = auto()      # <> (while)
    KW_RETURN = auto()     # <-
    KW_CLASS = auto()      # +* class
    KW_STRUCT = auto()     # +* struct
    KW_TRAIT = auto()      # +* trait
    KW_FN = auto()         # ++
    KW_MATCH = auto()      # ?~
    KW_PIPE = auto()       # ~>
    KW_SELF = auto()       # @
    KW_NEW = auto()        # new
    KW_MUT = auto()        # mut
    KW_BREAK = auto()      # !>
    KW_CONTINUE = auto()   # !>>
    KW_PANIC = auto()      # !!
    KW_GO = auto()         # go
    KW_IMPORT = auto()     # +* import
    KW_MODULE = auto()     # +* module
    KW_EXPORT = auto()     # +* export
    
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    COLON = auto()         # :
    DOUBLE_COLON = auto()  # ::
    COMMA = auto()         # ,
    DOT = auto()           # .
    DOTDOT = auto()        # ..
    DOTDOTEQ = auto()      # ..=
    AT = auto()            # @
    ARROW = auto()         # ->
    SEMICOLON = auto()     # ;
    QUESTION = auto()      # ?
    EXCLAMATION = auto()   # !
    
    PLUS = auto()          # +
    MINUS = auto()         # -
    STAR = auto()          # *
    SLASH = auto()         # /
    MOD = auto()           # %
    POW = auto()           # **
    ASSIGN = auto()        # =
    PLUS_EQ = auto()       # +=
    MINUS_EQ = auto()      # -=
    STAR_EQ = auto()       # *=
    SLASH_EQ = auto()      # /=
    EQ = auto()            # ==
    NEQ = auto()           # !=
    LT = auto()            # <
    GT = auto()            # >
    LTE = auto()           # <=
    GTE = auto()           # >=
    AND = auto()           # &&
    OR = auto()            # ||
    NOT = auto()           # !
    
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NONE = auto()
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}' L{self.line})"

KEYWORDS = {
    "true": TokenType.BOOLEAN, "false": TokenType.BOOLEAN,
    "none": TokenType.NONE, "mut": TokenType.KW_MUT,
    "new": TokenType.KW_NEW, "go": TokenType.KW_GO,
}