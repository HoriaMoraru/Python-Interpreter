from dataclasses import dataclass
from functools import reduce


@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word. return true if the dfa accepts the word, false otherwise
        final_state = reduce(lambda state, symbol: self.d.get((state, symbol), None), word, self.q0)
        return final_state in self.F

    def __repr__(self) -> str:
        states_str = ', '.join(map(str, self.K))
        alphabet_str = ', '.join(self.S)
        transitions_str = ', '.join(f"({from_state} -> {to_state}, '{symbol}')" for (from_state, symbol), to_state in self.d.items())
        accepting_states_str = ', '.join(map(str, self.F))

        return (f"DFA(\n"
                f"  States: {{{states_str}}},\n"
                f"  Alphabet: {{{alphabet_str}}},\n"
                f"  Transitions: {{{transitions_str}}},\n"
                f"  Initial State: {self.q0},\n"
                f"  Accepting States: {{{accepting_states_str}}}\n"
                f")")
