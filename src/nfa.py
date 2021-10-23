from __future__ import annotations
from typing import Dict, List, Set, Tuple


TransFunc = Dict[Tuple[int, str], List[int]]


class NFA:
    def __init__(self) -> None:
        self.states: List[int] = []
        self.alphabet: Set[str] = set()
        self.initial_state: int = -1
        self.final_state: int = -1
        self.trans_func: TransFunc = {}

    def __str__(self) -> str:
        nfa_repr = "Generated NFA:\n"
        nfa_repr += f"\tInitial State: ({self.initial_state})\n"
        nfa_repr += f"\tFinal State: (({self.final_state}))\n"
        nfa_repr += f"\tStates({len(self.states)}): {self.states}\n"
        nfa_repr += f"\tAlphabet({len(self.alphabet)}): {self._print_alphabet()}\n"
        nfa_repr += f"\tTransition Function({self._compute_number_of_edges()}): "
        nfa_repr += self._print_trans_func()

        return nfa_repr

    def _print_alphabet(self) -> str:
        alphabet_repr = "{"
        alphabet = sorted(self.alphabet)
        alphabet_repr += ", ".join("'" + character + "'" for character in alphabet)
        alphabet_repr += "}"

        return alphabet_repr

    def _print_trans_func(self) -> str:
        trans_func_repr = ""
        for key in self.trans_func:
            (state, character) = key
            key_repr = f"({state}, '{character}')"
            trans_func_repr += f"\n{key_repr.rjust(40)} --> {self.trans_func[key]}"

        return trans_func_repr

    def _compute_number_of_edges(self) -> int:
        return sum((len(self.trans_func[key]) for key in self.trans_func))
