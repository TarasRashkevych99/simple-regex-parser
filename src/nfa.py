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
        nfa_repr += f"\tAlphabet({len(self.alphabet)}): {self.alphabet}\n"
        nfa_repr += f"\tTransition Function({sum((len(self.trans_func[key]) for key in self.trans_func))}): "
        for key in self.trans_func:
            nfa_repr += f"\n{str(key).rjust(40)} --> {self.trans_func[key]}"

        return nfa_repr
