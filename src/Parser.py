from dataclasses import dataclass
from typing import List, Tuple, Union, Dict


@dataclass
class Atom:
    def interpret(self, env: Dict) -> Union[int, List]:
        raise NotImplementedError("The interpret function for this class should never be called!")


@dataclass
class LambdaEx(Atom):
    variable: str
    body: Atom

    def interpret(self, env: Dict) -> callable:
        return lambda arg: self.body.interpret({**env, self.variable: arg})


@dataclass
class ExList(Atom):
    children: List[Atom]

    def recursive_sum(self, lst: List) -> int:
        return sum(self.recursive_sum(item) if isinstance(item, list) else item for item in lst)

    def concat(self, lst: List, depth=0, max_depth=2) -> List:
        if depth == max_depth:
            return lst
        return [item for sublist in
                (self.concat(item, depth + 1, max_depth) if isinstance(item, list) else [item] for item in lst) for item
                in sublist]

    def apply_lambda(self, func, arg):
        return func.interpret({func.variable: arg}) if isinstance(func, LambdaEx) else func(arg)

    def interpret(self, env: Dict) -> Union[int, List]:
        expression = self.children[0]
        if isinstance(expression, Sum):
            return self.recursive_sum([c.interpret(env) for c in self.children[1:]])
        elif isinstance(expression, Concat):
            return self.concat([c.interpret(env) for c in self.children[1:]])
        elif isinstance(expression, (Literal, EmptyList, ExList, LambdaEx)):
            first_child = self.children[0].interpret(env)
            second_child = self.children[1].interpret(env) if len(self.children) >= 2 else None
            if isinstance(first_child, LambdaEx) or callable(first_child):
                return self.apply_lambda(first_child, second_child)
            return [c.interpret(env) for c in self.children]


@dataclass
class Literal(Atom):
    val: str

    def interpret(self, env: Dict) -> Union[int, str, LambdaEx]:
        return int(self.val) if self.val.isdigit() else env.get(self.val, self.val)


@dataclass
class EmptyList(Atom):
    def interpret(self, env: Dict) -> List:
        return []


@dataclass
class Sum(Atom):
    def interpret(self, env: Dict):
        raise NotImplementedError("The interpret function for this class should never be called!")


@dataclass
class Concat(Atom):
    def interpret(self, env: Dict):
        raise NotImplementedError("The interpret function for this class should never be called!")


class Parser:
    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = self.remove_white_spaces(tokens)
        self.current_index = 0

    def remove_white_spaces(self, tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return [(x, y) for (x, y) in tokens if x not in {'WHITE_SPACE', 'NEW_LINE', 'TAB'}]

    def parse(self) -> Atom:
        return self.parse_atom()

    def parse_atom(self) -> Atom:
        token_type, token_value = self.tokens[self.current_index]
        if self.match('OPEN_PARENTHESIS'):
            return self.parse_list()
        elif self.match('LITERAL'):
            return Literal(token_value)
        elif self.match('LITERAL_NUMBER'):
            return Literal(token_value)
        elif self.match('LAMBDA'):
            return self.parse_lambda()
        elif self.match('SUM'):
            return Sum()
        elif self.match('CONCAT'):
            return Concat()
        elif self.match('EMPTY_LIST'):
            return EmptyList()
        else:
            raise ValueError(f"Unsupported token type: {token_type}")

    def parse_list(self) -> ExList:
        children = [self.parse_atom()]
        while not self.peek('CLOSED_PARENTHESIS'):
            children.append(self.parse_atom())
        self.expect('CLOSED_PARENTHESIS')
        return ExList(children)

    def parse_lambda(self) -> LambdaEx:
        _, token_value = self.tokens[self.current_index]
        self.current_index += 1
        variable = token_value
        self.current_index += 1  # skip the ':' token
        body = self.parse_atom()
        return LambdaEx(variable, body)

    def expect(self, token: str) -> None:
        token_type, _ = self.tokens[self.current_index]
        if not self.match(token):
            raise ValueError(f"Expected token {token}, but got {token_type}")

    def match(self, token: str) -> bool:
        token_type, _ = self.tokens[self.current_index]
        if self.current_index < len(self.tokens) and token_type == token:
            self.current_index += 1
            return True
        return False

    def peek(self, token: str) -> bool:
        token_type, _ = self.tokens[self.current_index]
        if token_type == token:
            return True
        return False
