# src/parser.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Callable
import src.astcollections as asts

# ===== Token Types =====
class TokenType(Enum):
    Keyword = auto()
    Identifier = auto()
    Number = auto()
    EOF = auto()
    Operator = auto()
    Delimiter = auto()
    StringLiteral = auto()
    DataType = auto()

# ===== Position =====
@dataclass
class Position:
    coloums: int
    row: int

# ===== Token =====
class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value
        self.position = Position(0,0)
    def __repr__(self):
        return f"{self.token_type.name}(value:{self.value}, position:{self.position})"

# ===== Parser Constants =====
FUNCTION_KEYWORD = 'function'
DONE_KEYWORD = 'done'
ASSIGN_OP = '='
COLON = ':'
LPAREN = '('
RPAREN = ')'
COMMA = ','
SEMICOLON = ';'
EOF_VALUE = 'EOF'
RETURN_KEYWORD = 'return'

# ===== Lexer config =====
keyword_map = {FUNCTION_KEYWORD, DONE_KEYWORD, RETURN_KEYWORD}
operator_map = {ASSIGN_OP}
delimiter_map = {SEMICOLON, COLON, LPAREN, RPAREN, COMMA}
data_type_map = {'int', 'string', 'bool', 'void'}

# ===== Default values (runtime) =====
default_values = {'int':'0', 'string':'""', 'bool':'false'}


# ===== Lexer =====
def tokenize(source: str) -> List[Token]:
    tokens = []
    i = 0
    row = 1
    column = 1

    def advance():
        nonlocal i, column, row
        if source[i] == '\n':
            row += 1
            column = 1
        else:
            column += 1
        i += 1

    while i < len(source):
        c = source[i]

        #comments
        if c == '#':
            while i < len(source) and c != '\n':
                advance()

        if c.isspace():
            advance()
            continue

        # Identifier / Keyword / DataType
        if c.isalpha() or c == '_':
            start_row, start_column = row, column
            word = []
            while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                word.append(source[i])
                advance()
            word = ''.join(word)
            if word in keyword_map:
                token_type = TokenType.Keyword
            elif word in data_type_map:
                token_type = TokenType.DataType
            else:
                token_type = TokenType.Identifier
            t = Token(token_type, word)
            t.position = Position(start_column, start_row)
            tokens.append(t)
            continue

        # Number
        if c.isnumeric():
            start_row, start_column = row, column
            num = []
            while i < len(source) and source[i].isnumeric():
                num.append(source[i])
                advance()
            t = Token(TokenType.Number, ''.join(num))
            t.position = Position(start_column, start_row)
            tokens.append(t)
            continue

        # Operator
        if c in operator_map:
            t = Token(TokenType.Operator, c)
            t.position = Position(column, row)
            tokens.append(t)
            advance()
            continue

        # Delimiter
        if c in delimiter_map:
            t = Token(TokenType.Delimiter, c)
            t.position = Position(column, row)
            tokens.append(t)
            advance()
            continue

        # String literal
        if c == '"':
            start_row, start_column = row, column
            word = []
            advance()
            while i < len(source) and source[i] != '"':
                word.append(source[i])
                advance()
            advance()
            t = Token(TokenType.StringLiteral, ''.join(word))
            t.position = Position(start_column, start_row)
            tokens.append(t)
            continue

        # unknown char → skip
        advance()

    eof = Token(TokenType.EOF, EOF_VALUE)
    eof.position = Position(column,row)
    tokens.append(eof)

    return tokens

# ===== Error helper =====
def get_error_message(msg, position):
    return f"{msg} on line {position.row}, column {position.coloums}"

# ===== Parser Class =====
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0

    def consume(self, step: int = 1) -> None:
        """Advance the token pointer by step positions."""
        self.i += step

    def look_ahead(self, step: int, condition:Callable[[Token], bool]) -> bool:
        """Check if a token ahead satisfies the condition."""
        return self.i + step < len(self.tokens) and condition(self.tokens[self.i + step])

    def current_token(self) -> Token:
        """Get the current token."""
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        return self.tokens[-1]  # Return EOF if out of bounds

    def parse_expression(self):
        """Parse an expression (number, string, or identifier)."""
        token = self.current_token()
        match token.token_type:
            case TokenType.Number:
                self.consume()
                return asts.NumberLiteral(token.value)
            case TokenType.StringLiteral:
                self.consume()
                return asts.StringLiteral(token.value)
            case TokenType.Identifier:
                self.consume()
                return asts.Identifier(token.value)
            case _:
                raise Exception(get_error_message(f"Unexpected token '{token.value}'", token.position))

    def parse_variable(self):
        """Parse a variable declaration."""
        if self.current_token().token_type != TokenType.DataType:
            raise Exception(get_error_message("Expected data type for variable", self.current_token().position))
        dtype = self.current_token().value
        self.consume()

        if self.current_token().token_type != TokenType.Identifier:
            raise Exception(get_error_message("Expected variable name", self.current_token().position))
        name_token = self.current_token()
        self.consume()

        if self.current_token().value == ASSIGN_OP:
            self.consume()
            expr = self.parse_expression()
        else:
            expr = None  # default value nanti runtime

        if self.current_token().value != SEMICOLON:
            raise Exception(get_error_message(f"Expected '{SEMICOLON}' after variable '{name_token.value}'", self.current_token().position))
        self.consume()
        return asts.VariableDeclaration(name_token.value, asts.DataType(dtype), expr)

    def parse_block(self):
        """Parse a block of statements between ':' and 'done'."""
        statements = []
        if self.current_token().value != COLON:
            raise Exception(get_error_message(f"Expected '{COLON}' to start block", self.current_token().position))
        self.consume()
        while self.current_token().value != DONE_KEYWORD:
            t = self.current_token()
            match t.token_type:
                case TokenType.DataType:
                    var = self.parse_variable()
                    statements.append(var)
                case TokenType.Keyword:
                    if t.value == FUNCTION_KEYWORD:
                        statements.append(self.parse_function())
                        continue
                    if t.value == RETURN_KEYWORD:
                        statements.append(self.parse_return())
                case _:
                    statements.append(self.parse_expression())
                        
        self.consume()  # consume done
        return statements

    def parse_parameter(self):
        """Parse a function parameter."""
        if self.current_token().token_type != TokenType.DataType:
            raise Exception(get_error_message("Expected parameter type", self.current_token().position))
        dtype = self.current_token().value
        self.consume()

        if self.current_token().token_type != TokenType.Identifier:
            raise Exception(get_error_message("Expected parameter name", self.current_token().position))
        name = self.current_token().value
        self.consume()

        return asts.Parameter(asts.Identifier(name), asts.DataType(dtype))

    def parse_function(self):
        """Parse a function declaration."""
        self.consume()  # consume FUNCTION_KEYWORD

        if self.current_token().token_type != TokenType.DataType:
            raise Exception(get_error_message("Expected return type for function", self.current_token().position))
        ret_type = self.current_token().value
        self.consume()

        if self.current_token().token_type != TokenType.Identifier:
            raise Exception(get_error_message("Expected function name", self.current_token().position))
        name = self.current_token().value
        self.consume()

        if self.current_token().value != LPAREN:
            raise Exception(get_error_message(f"Expected '{LPAREN}' after function name", self.current_token().position))
        self.consume()
        param = []

        if self.current_token().value != RPAREN:
            while True:
                param.append(self.parse_parameter())
        
                if self.current_token().value == COMMA:
                    self.consume()
                    continue
                break
      
        if self.current_token().value != RPAREN:
            raise Exception(get_error_message(f"Expected '{RPAREN}' after function parameters", self.current_token().position))
        self.consume()

        body = self.parse_block()
        return asts.FunctionDeclaration(name, asts.DataType(ret_type), param, body)
    
    def parse_return(self):
        self.consume()  # consume 'return'
        if self.current_token().value != SEMICOLON:
            expr = self.parse_expression()
            if self.current_token().value != SEMICOLON:
                raise Exception(get_error_message(f"Expected '{SEMICOLON}' after return expression", self.current_token().position))
            self.consume()  # consume semicolon
            return asts.Return(expr)
        else:
            self.consume()  # consume semicolon for return without value
            return asts.Return()

    def parse(self) -> asts.Program:
        """Parse the tokens and return the AST."""
        result_ast: List[asts.Statement] = []

        while self.current_token().token_type != TokenType.EOF:
            t = self.current_token()
            match t.token_type:
                case TokenType.DataType:
                    var = self.parse_variable()
                    result_ast.append(var)
                    continue
                case TokenType.Keyword:
                    if t.value == FUNCTION_KEYWORD:
                        func = self.parse_function()
                        result_ast.append(func)
                        continue
            self.consume()

        return asts.Program(result_ast)


# ===== Parser function wrapper =====
def parse_sc(tokens: List[Token]) -> asts.Program:
    """Parse a list of tokens and return the AST."""
    parser = Parser(tokens)
    return parser.parse()
