from typing import Any

from .DFA import DFA
from dataclasses import dataclass
from collections.abc import Callable
from collections import deque

EPSILON = ''  # this is how epsilon is represented
SINK_STATE = frozenset() # this is how a sink state is represented in the DFA

@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # Compute the epsilon closure of a state (you will need this for subset construction)
        # See the EPSILON definition at the top of this file
        states = {state}
        visited = {state}
        queue = deque([state])
        while queue:
            current = queue.popleft()
            visited.add(current)
            next_epsilon_transitions = self.d.get((current, EPSILON), set())
            for epsilon_transition in next_epsilon_transitions:
                if epsilon_transition not in visited:
                    queue.append(epsilon_transition)
                states.add(epsilon_transition)
        return states

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # convert this nfa to a dfa using the subset construction algorithm
        initial = self.epsilon_closure(self.q0)
        transition_table: dict[tuple[frozenset[STATE], str], frozenset[Any]] = {}
        states: set[frozenset[STATE]] = {frozenset(initial)}
        process_states: deque[frozenset[STATE]] = deque([frozenset(initial)])
        while process_states:
            current_subset = process_states.popleft()
            for symbol in self.S:
                new_state = set()
                for state in current_subset:
                    next_state = self.d.get((state, symbol), set())
                    for s in next_state:
                        new_state = new_state.union(self.epsilon_closure(s))
                new_state = frozenset(new_state) if new_state else SINK_STATE
                if new_state not in states:
                    process_states.append(new_state)
                    states.add(new_state)
                transition_table[(frozenset(current_subset), symbol)] = new_state
        final_states = {state for state in states if state.intersection(self.F)}
        return DFA(S=self.S, K=states, q0=frozenset(initial), d=transition_table, F=final_states)

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> None:
        self.K = {f(state) for state in self.K}
        self.q0 = f(self.q0)
        self.F = {f(state) for state in self.F}
        self.d = {(f(state), symbol): {f(next_state) for next_state in next_states} for (state, symbol), next_states in self.d.items()}

    def __repr__(self) -> str:
        states_str = ', '.join(map(str, self.K))
        alphabet_str = ', '.join(self.S)
        transitions_str = ', '.join(f"({from_state} -> {to_state}, '{symbol}')" for (from_state, symbol), to_state in self.d.items())
        accepting_states_str = ', '.join(map(str, self.F))

        return (f"NFA(\n"
                f"  States: {{{states_str}}},\n"
                f"  Alphabet: {{{alphabet_str}}},\n"
                f"  Transitions: {{{transitions_str}}},\n"
                f"  Initial State: {self.q0},\n"
                f"  Accepting States: {{{accepting_states_str}}}\n"
                f")")