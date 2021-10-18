from typing import List, Set
from expression_tree import ExprTree
from nfa import NFA


class RegexParser:
    _REGEX_LEFT_PAR = "("
    _REGEX_RIGHT_PAR = ")"
    _REGEX_KLEENE_STAR_OP = "*"
    _REGEX_CONCAT_OP = "."
    _REGEX_ALTERNATION_OP = "|"
    _REGEX_EMPTY_STR = "ε"
    _next_state_id = 0

    def __init__(self, regex: str) -> None:
        RegexParser._next_state_id = 0
        self._raw_regex = regex.replace(" ", "")
        self._preprocessed_regex = self._preprocess_regex(self._raw_regex)
        self._converted_regex = self._convert_regex(self._preprocessed_regex)
        self._expression_tree = self._create_expression_tree(self._converted_regex)
        self._nfa = self._build_nfa(self._expression_tree)

    @property
    def raw_regex(self) -> str:
        return self._raw_regex

    @property
    def preprocessed_regex(self) -> str:
        return self._preprocessed_regex

    @property
    def converted_regex(self) -> str:
        return self._converted_regex

    @property
    def expression_tree(self) -> ExprTree:
        return self._expression_tree

    @property
    def nfa(self) -> NFA:
        return self._nfa

    def recognize_word(self, test_word: str) -> bool:
        if test_word == "" or test_word is None:
            return False

        epsilon_closure_states = self._execute_epsilon_closure(self.nfa.initial_state)

        for symbol in test_word:
            next_states = set()
            for state in epsilon_closure_states:
                next_states |= set(self.nfa.trans_func.get((state, symbol), []))
            epsilon_closure_states = self._execute_set_epsilon_closure(next_states)

        if self.nfa.final_state in epsilon_closure_states:
            return True
        else:
            return False

    def _build_nfa(self, root: ExprTree) -> NFA:
        if root is not None:
            left_nfa = self._build_nfa(root.left_child)
            right_nfa = self._build_nfa(root.right_child)
            empty_nfa = NFA()
            if self._is_operand(root.character):
                self._join_on_operand(empty_nfa, root.character)
            elif self._is_kleene_star_operator(root.character):
                self._join_on_kleene_star_operator(empty_nfa, left_nfa)
            elif self._is_alternation_operator(root.character):
                self._join_on_alternation_operator(empty_nfa, left_nfa, right_nfa)
            elif self._is_concat_operator(root.character):
                self._join_on_concat_operator(empty_nfa, left_nfa, right_nfa)

            return empty_nfa
        else:  # a new NFA is returned but never used(it is put here only for formal soundness)
            return NFA()

    def _create_expression_tree(self, converted_regex: str) -> ExprTree:
        stack: List[ExprTree] = []

        for character in converted_regex:
            if self._is_kleene_star_operator(character):
                left_child = stack.pop()
                stack.append(ExprTree(character, left_child))
            elif self._is_concat_operator(character) or self._is_alternation_operator(
                character
            ):
                right_child = stack.pop()
                left_child = stack.pop()
                stack.append(ExprTree(character, left_child, right_child))
            else:
                stack.append(ExprTree(character))

        return stack[-1]

    def _convert_regex(self, preprocessed_regex: str) -> str:
        stack: List[str] = []
        converted_regex = ""

        for i in range(len(preprocessed_regex)):
            next_char = preprocessed_regex[i]

            if self._is_operand(next_char):
                converted_regex += next_char
            elif next_char == RegexParser._REGEX_LEFT_PAR:
                stack.append(RegexParser._REGEX_LEFT_PAR)
            elif next_char == RegexParser._REGEX_RIGHT_PAR:
                while stack[-1] != RegexParser._REGEX_LEFT_PAR:
                    converted_regex += stack.pop()
                stack.pop()
            else:
                while len(stack) != 0 and self._get_precedence(
                    next_char
                ) <= self._get_precedence(stack[-1]):
                    converted_regex += stack.pop()
                stack.append(next_char)

        while len(stack) != 0:
            converted_regex += stack.pop()

        return converted_regex

    def _preprocess_regex(self, raw_regex: str) -> str:
        preprocessed_regex = ""
        pred_char = ""
        current_char = ""
        for i in range(len(raw_regex)):
            pred_char = current_char
            current_char = raw_regex[i]

            if (
                (self._is_operand(pred_char) and self._is_operand(current_char))
                or (
                    self._is_kleene_star_operator(pred_char)
                    and self._is_operand(current_char)
                )
                or (
                    self._is_kleene_star_operator(pred_char)
                    and self._is_left_parentesis(current_char)
                )
                or (
                    self._is_left_parentesis(pred_char)
                    and self._is_right_parentesis(current_char)
                )
                or (
                    self._is_right_parentesis(pred_char)
                    and self._is_operand(current_char)
                )
                or (
                    self._is_operand(pred_char)
                    and self._is_left_parentesis(current_char)
                )
            ):
                preprocessed_regex += RegexParser._REGEX_CONCAT_OP + current_char
            else:
                preprocessed_regex += current_char

        return preprocessed_regex

    def _execute_set_epsilon_closure(self, states: Set[int]) -> Set[int]:
        epsilon_closure_states = set()
        for state in states:
            epsilon_closure_states |= self._execute_epsilon_closure(state)
        return epsilon_closure_states

    def _execute_epsilon_closure(self, state: int) -> Set[int]:
        states = set()
        already_on = [False for _ in range(len(self.nfa.states))]
        self._execute_epsilon_closure_rec(state, states, already_on)
        return states

    def _execute_epsilon_closure_rec(
        self, state: int, states: Set[int], already_on: List[bool]
    ) -> None:
        states.add(state)
        already_on[state] = True
        for next_state in self.nfa.trans_func.get(
            (state, RegexParser._REGEX_EMPTY_STR), []
        ):
            if not already_on[next_state]:
                self._execute_epsilon_closure_rec(next_state, states, already_on)

    def _join_on_operand(self, empty_nfa: NFA, character: str) -> None:
        empty_nfa.initial_state = RegexParser._next_state_id
        empty_nfa.final_state = RegexParser._next_state_id + 1
        RegexParser._next_state_id += 2
        empty_nfa.states.extend((empty_nfa.initial_state, empty_nfa.final_state))

        empty_nfa.alphabet.add(character)

        empty_nfa.trans_func = {
            (empty_nfa.initial_state, character): [empty_nfa.final_state]
        }

    def _join_on_kleene_star_operator(self, empty_nfa: NFA, left_nfa: NFA) -> None:
        empty_nfa.states = left_nfa.states
        empty_nfa.alphabet = left_nfa.alphabet
        empty_nfa.trans_func = left_nfa.trans_func
        old_initil_state = left_nfa.initial_state
        old_final_state = left_nfa.final_state

        new_initial_state = RegexParser._next_state_id
        new_final_state = RegexParser._next_state_id + 1
        RegexParser._next_state_id += 2
        empty_nfa.states.extend((new_initial_state, new_final_state))

        self._update_trans_func(empty_nfa, old_final_state, old_initil_state)
        self._update_trans_func(empty_nfa, old_final_state, new_final_state)
        self._update_trans_func(empty_nfa, new_initial_state, old_initil_state)
        self._update_trans_func(empty_nfa, new_initial_state, new_final_state)

        empty_nfa.initial_state = new_initial_state
        empty_nfa.final_state = new_final_state

    def _join_on_alternation_operator(
        self, empty_nfa: NFA, left_nfa: NFA, right_nfa: NFA
    ) -> None:
        empty_nfa.states = left_nfa.states + right_nfa.states
        empty_nfa.alphabet = left_nfa.alphabet | right_nfa.alphabet
        empty_nfa.trans_func.update(left_nfa.trans_func)
        empty_nfa.trans_func.update(right_nfa.trans_func)
        left_nfa_old_initial_state = left_nfa.initial_state
        left_nfa_old_final_state = left_nfa.final_state
        right_nfa_old_initial_state = right_nfa.initial_state
        right_nfa_old_final_state = right_nfa.final_state

        new_initial_state = RegexParser._next_state_id
        new_final_state = RegexParser._next_state_id + 1
        RegexParser._next_state_id += 2
        empty_nfa.states.extend((new_initial_state, new_final_state))

        self._update_trans_func(empty_nfa, right_nfa_old_final_state, new_final_state)
        self._update_trans_func(empty_nfa, left_nfa_old_final_state, new_final_state)
        self._update_trans_func(
            empty_nfa, new_initial_state, right_nfa_old_initial_state
        )
        self._update_trans_func(
            empty_nfa, new_initial_state, left_nfa_old_initial_state
        )

        empty_nfa.initial_state = new_initial_state
        empty_nfa.final_state = new_final_state

    def _join_on_concat_operator(
        self, empty_nfa: NFA, left_nfa: NFA, right_nfa: NFA
    ) -> None:
        empty_nfa.states = left_nfa.states + right_nfa.states
        empty_nfa.alphabet = left_nfa.alphabet | right_nfa.alphabet
        empty_nfa.trans_func.update(left_nfa.trans_func)
        empty_nfa.trans_func.update(right_nfa.trans_func)
        left_nfa_old_initial_state = left_nfa.initial_state
        left_nfa_old_final_state = left_nfa.final_state
        right_nfa_old_initial_state = right_nfa.initial_state
        right_nfa_old_final_state = right_nfa.final_state

        self._concatenate_right_nfa(
            empty_nfa, right_nfa, left_nfa_old_final_state, right_nfa_old_initial_state
        )

        self._update_right_nfa_state_ids(empty_nfa, right_nfa_old_final_state)

        RegexParser._next_state_id -= 1

        empty_nfa.initial_state = left_nfa_old_initial_state
        empty_nfa.final_state = right_nfa_old_final_state - 1

    def _update_right_nfa_state_ids(
        self, empty_nfa: NFA, right_nfa_old_final_state: int
    ) -> None:
        for (state, character) in list(empty_nfa.trans_func):
            dest_states = empty_nfa.trans_func[(state, character)]
            if right_nfa_old_final_state in dest_states:
                dest_states.remove(right_nfa_old_final_state)
                dest_states.append(right_nfa_old_final_state - 1)

        empty_nfa.states.remove(right_nfa_old_final_state)
        empty_nfa.states.append(right_nfa_old_final_state - 1)

    def _concatenate_right_nfa(
        self,
        empty_nfa: NFA,
        right_nfa: NFA,
        left_nfa_old_final_state: int,
        right_nfa_old_initial_state: int,
    ) -> None:
        empty_nfa.states.remove(right_nfa_old_initial_state)

        all_possible_trans_from_right_nfa_old_initial_state = [
            (right_nfa_old_initial_state, character) for character in right_nfa.alphabet
        ]
        all_possible_trans_from_right_nfa_old_initial_state.append(
            (right_nfa_old_initial_state, RegexParser._REGEX_EMPTY_STR)
        )

        for (source, character) in all_possible_trans_from_right_nfa_old_initial_state:
            source_dest_states = empty_nfa.trans_func.pop((source, character), [])
            if source_dest_states != []:
                empty_nfa.trans_func.update(
                    {(left_nfa_old_final_state, character): source_dest_states}
                )

    def _update_trans_func(self, empty_nfa: NFA, source: int, destination: int) -> None:
        if (source, RegexParser._REGEX_EMPTY_STR) in empty_nfa.trans_func:
            source_dest_states = empty_nfa.trans_func[
                (source, RegexParser._REGEX_EMPTY_STR)
            ]
            source_dest_states.append(destination)
        else:
            empty_nfa.trans_func[(source, RegexParser._REGEX_EMPTY_STR)] = [destination]

    def _get_precedence(self, character: str) -> int:
        if character == RegexParser._REGEX_KLEENE_STAR_OP:
            return 3
        elif character == RegexParser._REGEX_CONCAT_OP:
            return 2
        elif character == RegexParser._REGEX_ALTERNATION_OP:
            return 1
        else:
            return -1

    def _is_operand(self, character: str) -> bool:
        return (
            character != ""
            and character != RegexParser._REGEX_KLEENE_STAR_OP
            and character != RegexParser._REGEX_CONCAT_OP
            and character != RegexParser._REGEX_ALTERNATION_OP
            and character != RegexParser._REGEX_LEFT_PAR
            and character != RegexParser._REGEX_RIGHT_PAR
        )

    def _is_concat_operator(self, character: str) -> bool:
        return character == RegexParser._REGEX_CONCAT_OP

    def _is_alternation_operator(self, character: str) -> bool:
        return character == RegexParser._REGEX_ALTERNATION_OP

    def _is_kleene_star_operator(self, character: str) -> bool:
        return character == RegexParser._REGEX_KLEENE_STAR_OP

    def _is_left_parentesis(self, character: str) -> bool:
        return character == RegexParser._REGEX_LEFT_PAR

    def _is_right_parentesis(self, character: str) -> bool:
        return character == RegexParser._REGEX_RIGHT_PAR


if __name__ == "__main__":

    def test():
        regex = "ab|c*d|asdf|(a(adf)*)"
        # regex = "(ab|cd)"
        parser = RegexParser(regex)
        print(f"Raw regex in infix notation:\t\t {parser.raw_regex}")
        print(f"Preprocessed regex in infix notation:\t {parser.preprocessed_regex}")
        print(f"Converted regex in postfix notation:\t {parser.converted_regex}")
        print(parser.expression_tree)
        print(parser.nfa)

        print(f"ab is recognized: {parser.recognize_word('ab')}")
        print(f"cd is recognized: {parser.recognize_word('cd')}")
        print(f"asdf is recognized: {parser.recognize_word('asdf')}")
        print(f"cccccccd is recognized: {parser.recognize_word('cccccccd')}")
        print(f"ccccccccccccd is recognized: {parser.recognize_word('ccccccccccccd')}")
        print(f"aadfadf is recognized: {parser.recognize_word('aadfadf')}")

    test()
