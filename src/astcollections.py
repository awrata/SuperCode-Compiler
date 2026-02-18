# src/astcollections.py
from dataclasses import dataclass, field
from typing import List, Optional

# ===== AST Nodes =====
class Node:
  pass

class Statement(Node):
  pass
class Expression(Node):
  pass

@dataclass
class DataType(Node):
    name: str

@dataclass
class Undefined(Expression):
    def __repr__(self):
        return "undefined"

@dataclass
class NumberLiteral(Expression):
    value: str

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class VariableDeclaration(Statement):
    name: str
    type: DataType
    value: Optional[Expression] = None

@dataclass
class FunctionDeclaration(Statement):
    name: str
    return_type: DataType
    parameters: List[str] = field(default_factory=list)
    block: List[Statement] = field(default_factory=list)

@dataclass
class Program(Node):
    statements: List[Statement]