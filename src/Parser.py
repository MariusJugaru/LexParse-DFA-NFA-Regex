from .DFA import DFA
from .NFA import NFA
from .Regex import Regex, parse_regex
from .Lexer import Lexer
from dataclasses import dataclass

@dataclass
class Expr:
    pass

@dataclass
class Lambda(Expr):
    var: Expr
    expr: Expr

    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def __str__(self):
        return f"Lambda ({self.var}) -> {self.expr}"
    
@dataclass
class PartialLambda(Expr):
    var: Expr

    def __init__(self, var):
        self.var = var

@dataclass
class Plus(Expr):
    left: Expr
    right: Expr

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"Plus ({self.left}) ({self.right})"

@dataclass
class PartialPlus(Expr):
    expr: Expr

    def __init__(self, expr):
        self.expr = expr

@dataclass
class Minus(Expr):
    left: Expr
    right: Expr

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"Minus ({self.left}) ({self.right})"

@dataclass
class PartialMinus(Expr):
    expr: Expr

    def __init__(self, expr):
        self.expr = expr

@dataclass
class Mult(Expr):
    left: Expr
    right: Expr

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"Mult ({self.left}) ({self.right})"
    
@dataclass
class PartialMult(Expr):
    expr: Expr

    def __init__(self, expr):
        self.expr = expr

@dataclass
class Div(Expr):
    left: Expr
    right: Expr

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"Div ({self.left}) ({self.right})"
    
@dataclass
class PartialDiv(Expr):
    expr: Expr

    def __init__(self, expr):
        self.expr = expr

@dataclass
class Var(Expr):
    var: str

    def __init__(self, var):
        self.var = var

    def __str__(self):
        return f"Var \"{self.var}\""
    
@dataclass
class Val(Expr):
    val: int

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f"Val {self.val}"
    
@dataclass
class Parens(Expr):
    expr: Expr

    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"Parant ({self.expr})"
    
@dataclass
class OpenPar(Expr):
    pass

@dataclass
class ClosedPar(Expr):
    pass

@dataclass
class Parser():
    lexer: Lexer

    def __init__(self) -> None:
        spec = [
                ("Lambda", "\\\([a-z]|[A-Z])+."),
                ("Plus", "+"),
                ("Minus", "-"),
                ("Mult", "\\*"),
                ("Divis", "/"),
                ("OpenPar", "\\("),
                ("ClosedPar", "\\)"),
                ("Val", "[0-9]+"),
                ("Var", "([a-z]|[A-Z])+"),
                ("Space", "\\ ")
                ]
        self.lexer = Lexer(spec)
        
    
    def parse(self, input: str) -> None:
        # this method should parse the input string and print the result of the parsing process
        
        # get tokens in text
        tokens_aux = self.lexer.lex(input)

        # remove the space tokens, we don't need them
        tokens = [token for token in tokens_aux if token != ("Space", " ")]
        tokens.reverse()

        stack = []
        cool = False

        while True:
            if not cool:
                if len(tokens) == 0:
                    break

                token = tokens.pop()

                match token:
                    case ("Plus", "+"):
                        stack.append(PartialPlus(stack.pop()))
                    case ("Minus", "-"):
                        stack.append(PartialMinus(stack.pop()))
                    case ("Mult", "*"):
                        stack.append(PartialMult(stack.pop()))
                    case ("Divis", "/"):
                        stack.append(PartialDiv(stack.pop()))
                    case ("OpenPar", "("):
                        stack.append(OpenPar())
                    case ("ClosedPar", ")"):
                        stack.append(ClosedPar())
                        cool = True
                    case ("Lambda", var):
                        stack.append(PartialLambda(Var(var[1:-1])))
                    case ("Val", val):
                        stack.append(Val(val))
                        cool = True
                    case ("Var", var):
                        stack.append(Var(var))
                        cool = True
            else:
                if len(stack) < 2:
                    cool = False
                    continue

                elem1 = stack.pop()
                elem2 = stack.pop()

                if isinstance(elem2, PartialPlus):
                    stack.append(Plus(elem2.expr, elem1))
                elif isinstance(elem2, PartialMinus):
                    stack.append(Minus(elem2.expr, elem1))
                elif isinstance(elem2, PartialMult):
                    stack.append(Mult(elem2.expr, elem1))
                elif isinstance(elem2, PartialDiv):
                    stack.append(Div(elem2.expr, elem1))
                elif isinstance(elem1, ClosedPar):
                    stack.pop() # OpenPar
                    stack.append(Parens(elem2))
                elif isinstance(elem2, PartialLambda):
                    stack.append(Lambda(elem2.var, elem1))
                else:
                    stack.append(elem2)
                    stack.append(elem1)
                    cool = False

        return stack.pop()
                

            
parser = Parser()

print(parser.parse("\\x.\\y.(x + y)"))

# print(Lambda(Var("x"), (Mult(Var("x"), Parens(Plus(Var("x"), Val(2)))))))