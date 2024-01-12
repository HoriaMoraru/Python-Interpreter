from src.DFA import DFA
from src.NFA import NFA, EPSILON, SINK_STATE
from src.Regex import parse_regex


class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        self.map_lexemes: dict[frozenset[int], str] = {}
        self.dfa = self._generate_dfa(spec)

    def _generate_dfa(self, spec: list[tuple[str, str]]) -> DFA[frozenset[int]]:
        # Generate the DFA from the specification
        S, K, d, F = set(), {0}, {}, set()
        current_states_size = 1
        for lexeme, regex in spec:
            nfa = parse_regex(regex).thompson()
            nfa.remap_states(lambda x: x + current_states_size)
            current_states_size += len(nfa.K)
            S.update(nfa.S)
            K.update(nfa.K)
            d.update(nfa.d)
            if (0, EPSILON) in d:
                d[(0, EPSILON)].add(nfa.q0)
            else:
                d.update({(0, EPSILON): {nfa.q0}})
            F.update(nfa.F)
            self.map_lexemes.update({final_state: lexeme for final_state in nfa.F})
        return NFA(S, K, 0, d, F).subset_construction()

    def lex(self, word: str) -> list[tuple[str, str]]:
        # this method splits the lexer into tokens based on the specification
        lexer_output = []
        position, line = [0], 0
        EOF = len(word) - 1 if word else 0

        def dfs(state: frozenset[int], current_word: str, current_str: str, matched_str: str, lexeme: str) -> tuple[str, str]:
            nfa_final_state = list(set(self.map_lexemes.keys()).intersection(state))
            if nfa_final_state:
                # if multiple elements in the intersection, the longest substring satisfies multiple regexes, get the min.
                lexeme = self.map_lexemes[min(nfa_final_state)]
                matched_str = current_str
            if state == SINK_STATE:
                position[0] += len(matched_str) if matched_str else len(current_str) - 1
                return matched_str, lexeme
            if current_word:
                next_state = self.dfa.d.get((state, current_word[0]), frozenset())
                matched_str, lexeme = dfs(next_state, current_word[1:], current_str + current_word[0], matched_str, lexeme)
            return matched_str, lexeme

        while word:
            matched_str, lexeme = dfs(self.dfa.q0, word, '', '', '')
            if matched_str == '\n':
                line += 1
                position[0] = 0
            EOF -= len(matched_str)
            if not matched_str:
                if EOF == 0 and word[-1] in self.dfa.S:
                    return [(matched_str, f'No viable alternative at character EOF, line {line}')]
                return [(matched_str, f'No viable alternative at character {position[0]}, line {line}')]
            lexer_output.append((lexeme, matched_str))
            word = word.replace(matched_str, '', 1)
        return lexer_output
