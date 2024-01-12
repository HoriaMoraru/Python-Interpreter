from .NFA import NFA, EPSILON
from dataclasses import dataclass


@dataclass
class Regex:
    # abstract method for regex subclasses
    def thompson(self) -> NFA[int]:
        raise NotImplementedError("The thompson method of the Regex class should never be called")


def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string
    def prepare(regex: str) -> str:
        escape_next = False
        new = ''
        for char in regex:
            if char == '\\':
                escape_next = True
                new += char
            elif char != ' ' or escape_next:
                new += char
                escape_next = False
        return new
    return RegexParser(prepare(regex)).parse()


@dataclass
class Epsilon(Regex):
    def __init__(self):
        self.level = 0

    def __repr__(self):
        return EPSILON

    def thompson(self) -> NFA[int]:
        return NFA(S=set(),
                   K={0},
                   q0=0,
                   d={},
                   F={0})


@dataclass
class Character(Regex):
    def __init__(self, char):
        self.char = char
        self.level = 0

    def __repr__(self):
        return self.char

    def thompson(self) -> NFA[int]:
        return NFA(S={self.char},
                   K={0, 1}, q0=0,
                   d={(0, self.char): {1}},
                   F={1})


@dataclass
class Concat(Regex):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.level = 2

    def __repr__(self):
        def format_side(side):
            if side.level > self.level:
                return f'({side})'
            else:
                return f'{side}'

        return format_side(self.left) + format_side(self.right)

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()
        right_nfa.remap_states(lambda x: x + len(left_nfa.K))
        update_d = {**left_nfa.d, **right_nfa.d}
        update_d.update({(state, EPSILON): {right_nfa.q0} for state in left_nfa.F})
        return NFA(S=left_nfa.S.union(right_nfa.S),
                   K=left_nfa.K.union(right_nfa.K),
                   q0=left_nfa.q0,
                   d=update_d,
                   F=right_nfa.F)


@dataclass
class Union(Regex):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.level = 3

    def __repr__(self):
        return f'({self.left})' + '|' + f'({self.right})'

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()
        left_nfa.remap_states(lambda x: x + 1)
        right_nfa.remap_states(lambda x: x + len(left_nfa.K) + 1)
        update_d = {**left_nfa.d, **right_nfa.d}
        update_d.update({(0, EPSILON): {left_nfa.q0, right_nfa.q0}})
        return NFA(S=left_nfa.S.union(right_nfa.S),
                   K=left_nfa.K.union(right_nfa.K).union({0}),
                   q0=0,
                   d=update_d,
                   F=left_nfa.F.union(right_nfa.F))


@dataclass
class Star(Regex):
    def __init__(self, sub: Regex):
        self.sub = sub
        self.level = 1

    def __repr__(self):
        if self.sub.level > self.level:
            return f'({self.sub})*'
        else:
            return f'{self.sub}*'

    def thompson(self) -> NFA[int]:
        sub_nfa = self.sub.thompson()
        sub_nfa.remap_states(lambda x: x + 1)
        maximum = max(sub_nfa.K) + 1
        sub_nfa.d.update({(0, EPSILON): {sub_nfa.q0, maximum}})
        sub_nfa.d.update({(state, EPSILON): {sub_nfa.q0, maximum} for state in sub_nfa.F})
        return NFA(S=sub_nfa.S,
                   K=sub_nfa.K.union({0, maximum}),
                   q0=0,
                   d=sub_nfa.d,
                   F={maximum})


@dataclass
class QuestionMark(Regex):
    def __init__(self, sub):
        self.sub = sub
        self.level = 1

    def __repr__(self):
        if self.sub.level > self.level:
            return f'({self.sub})?'
        else:
            return f'{self.sub}?'

    def thompson(self) -> NFA[int]:
        return Union(self.sub, Epsilon()).thompson()


@dataclass
class Plus(Regex):
    def __init__(self, sub):
        self.sub = sub
        self.level = 1

    def __repr__(self):
        if self.sub.level > self.level:
            return f'({self.sub})+'
        else:
            return f'{self.sub}+'

    def thompson(self) -> NFA[int]:
        return Concat(self.sub, Star(self.sub)).thompson()


@dataclass
class RegexParser:
    def __init__(self, pattern):
        self.pattern = pattern
        self.current_index = 0

    def parse(self) -> Regex:
        return self.parse_expression()

    def parse_expression(self) -> Regex:
        expression = self.parse_term()
        while self.match('|'):
            expression = Union(expression, self.parse_term())
        return expression

    def parse_syntactic_sugar(self) -> Regex:
        expression = self.parse_atom()
        start = expression.char
        self.expect('-')
        end = self.consume()
        for ascii_code in range(ord(start) + 1, ord(end) + 1):
            expression = Union(expression, Character(chr(ascii_code)))
        return expression

    def parse_term(self) -> Regex:
        term = self.parse_factor()
        while self.current_index < len(self.pattern) and self.pattern[self.current_index] not in (')', '|'):
            term = Concat(term, self.parse_factor())
        return term

    def parse_factor(self) -> Regex:
        factor = self.parse_atom()
        if self.match('*'):
            factor = Star(factor)
        elif self.match('?'):
            factor = QuestionMark(factor)
        elif self.match('+'):
            factor = Plus(factor)
        return factor

    def parse_atom(self) -> Regex:
        if self.match('('):
            subexpression = self.parse_expression()
            self.expect(')')
            return subexpression
        elif self.match('['):
            subexpression = self.parse_syntactic_sugar()
            self.expect(']')
            return subexpression
        else:
            if self.pattern == EPSILON:
                return Epsilon()
            atom = Character(self.consume())
            return atom

    def match(self, char: str) -> bool:
        if self.current_index < len(self.pattern) and self.pattern[self.current_index] == char:
            self.current_index += 1
            return True
        return False

    def consume(self) -> str:
        if self.pattern[self.current_index] == '\\':
            self.current_index += 1
        result = self.pattern[self.current_index]
        self.current_index += 1
        return result

    def expect(self, char: str) -> None:
        if not self.match(char):
            raise ValueError(f'Expected {char} but found {self.pattern[self.current_index]}')
