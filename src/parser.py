# src/parser.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
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

# ===== Lexer config =====
keyword_map = {'function', 'done'}
operator_map = {'='}
delimiter_map = {';', ':', '(', ')'}
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

    eof = Token(TokenType.EOF, "EOF")
    eof.position = Position(column,row)
    tokens.append(eof)
    return tokens

# ===== Error helper =====
def get_error_message(msg, position):
    return f"{msg} on line {position.row}, column {position.coloums}"

# ===== Parser =====
def parse_sc(tokens: List[Token]) -> asts.Program:
    i = 0
    result_ast: List[asts.Statement] = []

    def look_ahead(step, condition):
        return i+step < len(tokens) and condition(tokens[i+step])

    def consume(step=1):
        nonlocal i
        i += step

    # ===== Expression Parser =====
    def parse_expression():
        nonlocal i
        token = tokens[i]
        match token.token_type:
            case TokenType.Number:
                consume()
                return asts.NumberLiteral(token.value)
            case TokenType.StringLiteral:
                consume()
                return asts.StringLiteral(token.value)
            case TokenType.Identifier:
                consume()
                return asts.Identifier(token.value)
            case _:
                raise Exception(get_error_message(f"Unexpected token '{token.value}'", token.position))

    # ===== Variable Parser =====
    def parse_variable():
        nonlocal i
        if tokens[i].token_type != TokenType.DataType:
            raise Exception(get_error_message("Expected data type for variable", tokens[i].position))
        dtype = tokens[i].value
        consume()

        if tokens[i].token_type != TokenType.Identifier:
            raise Exception(get_error_message("Expected variable name", tokens[i].position))
        name_token = tokens[i]
        consume()

        if tokens[i].value == '=':
            consume()
            expr = parse_expression()
        else:
            expr = None  # default value nanti runtime

        if tokens[i].value != ';':
            raise Exception(get_error_message(f"Expected ';' after variable '{name_token.value}'", tokens[i].position))
        consume()
        return asts.VariableDeclaration(name_token.value, asts.DataType(dtype), expr)

    # ===== Block Parser =====
    def parse_block():
        nonlocal i
        statements = []
        if tokens[i].value != ':':
            raise Exception(get_error_message("Expected ':' to start block", tokens[i].position))
        consume()
        while tokens[i].value != 'done':
            t = tokens[i]
            if t.token_type == TokenType.DataType:
                statements.append(parse_variable())
            else:
                statements.append(parse_expression())
        consume()  # consume done
        return statements

    # ===== Function Parser =====
    def parse_function():
        nonlocal i
        consume()  # consume 'function'

        if tokens[i].token_type != TokenType.DataType:
            raise Exception(get_error_message("Expected return type for function", tokens[i].position))
        ret_type = tokens[i].value
        consume()

        if tokens[i].token_type != TokenType.Identifier:
            raise Exception(get_error_message("Expected function name", tokens[i].position))
        name = tokens[i].value
        consume()

        if tokens[i].value != '(':
            raise Exception(get_error_message("Expected '(' after function name", tokens[i].position))
        consume()
        if tokens[i].value != ')':
            raise Exception(get_error_message("Expected ')' after function parameters", tokens[i].position))
        consume()

        body = parse_block()
        return asts.FunctionDeclaration(name, asts.DataType(ret_type), [], body)

    # ===== Main parse loop =====
    while tokens[i].token_type != TokenType.EOF:
        t = tokens[i]
        match t.token_type:
            case TokenType.DataType:
                var = parse_variable()
                result_ast.append(var)
                continue
            case TokenType.Keyword:
                if t.value == 'function':
                    func = parse_function()
                    result_ast.append(func)
                    continue
        consume()

    return asts.Program(result_ast)