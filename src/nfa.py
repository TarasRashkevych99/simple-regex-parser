from typing import Dict, List, Optional, Set, Tuple

TransFunc = Dict[Tuple[int, str], List[int]]


class NFA:

    _REGEX_EMPTY_STR = "ε"
    _next_state_id = 0

    def __init__(self) -> None:
        self._states: List[int] = None
        self._alphabet: Set[str] = None
        self._initial_state: int = None
        self._final_state: int = None
        self._transition_function: TransFunc = None

    def join_on_operand(self, character) -> None:
        self._inital_state = NFA._next_state_id
        self._final_state = NFA._next_state_id + 1
        NFA._next_state_id += 2
        self._states.extend((self._initial_state, self._final_state))
        self._alphabet.add(character)
        self._transition_function = {
            (self._initial_state, character): [self._final_state]
        }

    def join_on_kleene_star_operator(self, left_nfa: Optional["NFA"]) -> None:
        self._states = left_nfa._states
        self._alphabet = left_nfa._alphabet
        self._transition_function = left_nfa._transition_function
        old_initil_state = left_nfa._initial_state
        old_final_state = left_nfa._final_state

        new_inital_state = NFA._next_state_id
        new_final_state = NFA._next_state_id + 1
        NFA._next_state_id += 2
        self._states.extend((new_inital_state, new_final_state))

        self._update_transition_function(old_final_state, old_initil_state)
        self._update_transition_function(old_final_state, new_final_state)
        self._update_transition_function(new_inital_state, old_initil_state)
        self._update_transition_function(new_inital_state, new_final_state)

        self._initial_state = new_inital_state
        self._final_state = new_final_state

    def join_on_alternation_operator(
        self, left_nfa: Optional["NFA"], right_nfa: Optional["NFA"]
    ) -> None:
        pass

    def join_on_concat_operator(
        self, left_nfa: Optional["NFA"], right_nfa: Optional["NFA"]
    ) -> None:
        pass

    def _update_transition_function(self, source, destination) -> None:
        if (source, NFA._REGEX_EMPTY_STR) in self._transition_function:
            source_dest_states = self._transition_function[
                (source, NFA._REGEX_EMPTY_STR)
            ]
            source_dest_states.append(destination)
            self._transition_function.update(
                (source, NFA._REGEX_EMPTY_STR), source_dest_states
            )
        else:
            self._transition_function[(source, NFA._REGEX_EMPTY_STR)] = [destination]
