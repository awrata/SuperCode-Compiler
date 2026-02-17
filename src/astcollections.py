class Node:
  pass

class Program(Node):
  def __init__(self, stmts):
    self.statements = stmts

class Statement(Node):
  pass
class Expression(Node):
  pass

class VariableDeclaration(Statement):
  def __init__(self, identifier, value):
    self.name = identifier
    self.value = value
  def __repr__(self):
    return f"{self.name}={self.value}"