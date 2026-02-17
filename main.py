from enum import Enum
import sys
import pathlib as pl
import src.astcollections as asts
from dataclasses import dataclass

class TokenType(Enum):
  Keyword = 0
  Identifier = 1
  Number = 2
  EOF = 3
  Operator = 4
  Delimiter = 5

@dataclass
class Position:
  coloums: int
  row: int
  
class Token:
  def __init__(self, token_type, value):
    self.token_type = token_type
    self.value = value
    self.position = Position(0, 0)
  
  def __repr__(self):
    return f"{self.token_type.name}(value:{self.value}, position:{self.position})"

keyword_map = {
  'function',
  'void',
  'done'
}

operator_map = {
  '='
}

delimiter_map = {
  ';'
}

def tokenize(source: str):
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

        # WHITESPACE (termasuk newline)
        if c.isspace():
            advance()
            continue

        # IDENTIFIER / KEYWORD
        if c.isalpha() or c == '_':
            start_row = row
            start_column = column

            word = []
            while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                word.append(source[i])
                advance()

            word = "".join(word)

            token = Token(
                TokenType.Keyword if word in keyword_map else TokenType.Identifier,
                word
            )
            token.position = Position(start_column, start_row)
            tokens.append(token)
            continue

        # NUMBER
        if c.isnumeric():
            start_row = row
            start_column = column

            number = []
            while i < len(source) and source[i].isnumeric():
                number.append(source[i])
                advance()

            token = Token(TokenType.Number, "".join(number))
            token.position = Position(start_column, start_row)
            tokens.append(token)
            continue

        # OPERATOR
        if c in operator_map:
            start_row = row
            start_column = column

            token = Token(TokenType.Operator, c)
            token.position = Position(start_column, start_row)
            tokens.append(token)

            advance()
            continue
        if c in delimiter_map:
          start_column = column
          start_row = row
          
          token = Token(TokenType.Delimiter, c)
          token.position = Position(start_column, start_row)
          tokens.append(token)

        # UNKNOWN CHARACTER
        advance()

    eof = Token(TokenType.EOF, "EOF")
    eof.position = Position(column, row)
    tokens.append(eof)

    return tokens

def parse_sc(tokens):
  resultAst = []
  
  i = 0
  def look_ahead(step, condition):
    nonlocal i
    return i + step < len(tokens) and condition(tokens[i + step])
  def consume(step=1):
    nonlocal i
    i += step
  def consume_until(condition):
    nonlocal i
    while i < len(tokens) and not condition():
      i += 1
  
  def parse_variable():
    nonlocal i
    variableDec = asts.VariableDeclaration(tokens[i].value, tokens[i+2].value)
    resultAst.append(variableDec)
    consume_until(lambda: tokens[i].value == ';')
  
  while tokens[i].token_type != TokenType.EOF:
    token = tokens[i]
    match token.token_type:
      case TokenType.Identifier:
        #parse Variables
        if look_ahead(1, lambda t: t.value == '=') and look_ahead(2, lambda t: t.token_type == TokenType.Number):
          parse_variable()
          continue
    
    i += 1
  return asts.Program(resultAst)

def main(args):
  if len(args) == 1:
    print("the program need a .sc files on arguments")
    return
  if not pl.Path(args[1]).exists():
    print(f"the path '{pl.Path(args[1])}' was not found")
    return
  if not args[1].endswith('.sc'):
    print(f"file '{args[1]}' was not .sc file")
    return
  with open(args[1], 'r') as s:
    source = s.read()
    
  tokens = tokenize(source)
  ast = parse_sc(tokens)
  print(ast.statements)

if __name__ == '__main__':
  main(sys.argv)