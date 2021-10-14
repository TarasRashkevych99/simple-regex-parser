from __future__ import annotations
from typing import Dict, List, Set, Tuple


TransFunc = Dict[Tuple[int, str], List[int]]


class NFA:

    _REGEX_EMPTY_STR = "ε"
    _next_state_id = 0

    def __init__(self) -> None:
        self._states: List[int] = []
        self._alphabet: Set[str] = set()
        self._initial_state: int = -1
        self._final_state: int = -1
        self._trans_func: TransFunc = {}

    def __str__(self) -> str:
        nfa_repr = "Generated NFA:\n"
        nfa_repr += f"\tInitial State: ({self._initial_state})\n"
        nfa_repr += f"\tFinal State: (({self._final_state}))\n"
        nfa_repr += f"\tStates({len(self._states)}): {self._states}\n"
        nfa_repr += f"\tAlphabet({len(self._alphabet)}): {self._alphabet}\n"
        nfa_repr += f"\tTransition Function({sum((len(self._trans_func[key]) for key in self._trans_func))}): "
        for key in self._trans_func:
            nfa_repr += f"\n{str(key).rjust(40)} --> {self._trans_func[key]}"

        return nfa_repr

    def join_on_operand(self, character: str) -> None:
        self._initial_state = NFA._next_state_id
        self._final_state = NFA._next_state_id + 1
        NFA._next_state_id += 2
        self._states.extend((self._initial_state, self._final_state))
        self._alphabet.add(character)
        self._trans_func = {(self._initial_state, character): [self._final_state]}

    def join_on_kleene_star_operator(self, left_nfa: NFA) -> None:
        self._states = left_nfa._states
        self._alphabet = left_nfa._alphabet
        self._trans_func = left_nfa._trans_func
        old_initil_state = left_nfa._initial_state
        old_final_state = left_nfa._final_state

        new_initial_state = NFA._next_state_id
        new_final_state = NFA._next_state_id + 1
        NFA._next_state_id += 2
        self._states.extend((new_initial_state, new_final_state))

        self._update_trans_func(old_final_state, old_initil_state)
        self._update_trans_func(old_final_state, new_final_state)
        self._update_trans_func(new_initial_state, old_initil_state)
        self._update_trans_func(new_initial_state, new_final_state)

        self._initial_state = new_initial_state
        self._final_state = new_final_state

    def join_on_alternation_operator(self, left_nfa: NFA, right_nfa: NFA) -> None:
        self._states = left_nfa._states + right_nfa._states
        self._alphabet = left_nfa._alphabet | right_nfa._alphabet
        self._trans_func.update(left_nfa._trans_func)
        self._trans_func.update(right_nfa._trans_func)
        left_nfa_old_initial_state = left_nfa._initial_state
        left_nfa_old_final_state = left_nfa._final_state
        right_nfa_old_initial_state = right_nfa._initial_state
        right_nfa_old_finale_state = right_nfa._final_state

        new_initial_state = NFA._next_state_id
        new_final_state = NFA._next_state_id + 1
        NFA._next_state_id += 2
        self._states.extend((new_initial_state, new_final_state))

        self._update_trans_func(right_nfa_old_finale_state, new_final_state)
        self._update_trans_func(left_nfa_old_final_state, new_final_state)
        self._update_trans_func(new_initial_state, right_nfa_old_initial_state)
        self._update_trans_func(new_initial_state, left_nfa_old_initial_state)

        self._initial_state = new_initial_state
        self._final_state = new_final_state

    def join_on_concat_operator(self, left_nfa: NFA, right_nfa: NFA) -> None:
        self._states = left_nfa._states + right_nfa._states
        self._alphabet = left_nfa._alphabet | right_nfa._alphabet
        self._trans_func.update(left_nfa._trans_func)
        self._trans_func.update(right_nfa._trans_func)
        left_nfa_old_initial_state = left_nfa._initial_state
        left_nfa_old_final_state = left_nfa._final_state
        right_nfa_old_initial_state = right_nfa._initial_state
        right_nfa_old_finale_state = right_nfa._final_state

        self._states.remove(right_nfa_old_initial_state)

        for (state, character) in list(self._trans_func):
            if state == right_nfa_old_initial_state:
                states = self._trans_func.pop((state, character))
                self._trans_func.update({(left_nfa_old_final_state, character): states})

        self._initial_state = left_nfa_old_initial_state
        self._final_state = right_nfa_old_finale_state

    def _update_trans_func(self, source: int, destination: int) -> None:
        if (source, NFA._REGEX_EMPTY_STR) in self._trans_func:
            source_dest_states = self._trans_func[(source, NFA._REGEX_EMPTY_STR)]
            source_dest_states.append(destination)
        else:
            self._trans_func[(source, NFA._REGEX_EMPTY_STR)] = [destination]
