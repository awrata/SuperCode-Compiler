from enum import Enum
import sys
import pathlib as pl
import src.astcollections as ast
from dataclasses import dataclass

class TokenType(Enum):
  Keyword = 0
  Identifier = 1
  Number = 2
  EOF = 3
  Operator = 4

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
    return f"{str(self.token_type)}(value:{self.value}, position:{self.position})"

keyword_map = {
  'function',
  'void',
  'done'
}

operator_map = {
  '='
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

        # UNKNOWN CHARACTER
        advance()

    eof = Token(TokenType.EOF, "EOF")
    eof.position = Position(column, row)
    tokens.append(eof)

    return tokens

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
  print(tokens)

if __name__ == '__main__':
  main(sys.argv)