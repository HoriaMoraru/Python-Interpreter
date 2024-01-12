from src.Lexer import Lexer
from src.Parser import Parser
from src.Spec import SPEC


class Interpreter:
    def __init__(self, input):
        self.input = input
        tokens = Lexer(SPEC).lex(input)
        self.ast = Parser(tokens).parse()

    def display(self, lst):
        if not isinstance(lst, list):
            return str(lst)
        items = ' '.join(self.display(item) for item in lst)
        return f"( {items} )" if items else "()"

    def interpret(self):
        env = {}
        output = self.ast.interpret(env)
        print(self.display(output)) if isinstance(output, list) else print(output)
