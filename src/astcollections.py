class Program:
  def __init__(self, stmts):
    self.statements = stmts

class Statement:
  pass
class Expression:
  pass

class VariableDeclaration(Statement):
  def __init__(self, identifier, value):
    self.name = identifier
    self.value = value