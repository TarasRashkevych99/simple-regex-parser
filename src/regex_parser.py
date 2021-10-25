from typing import List, Set
from simple_data_structures import Character, CharacterList
from expression_tree import ExprTree
from nfa import NFA


# TODO Write the documentation
class RegexParser:
    _REGEX_LEFT_PAR = "("
    _REGEX_RIGHT_PAR = ")"
    _REGEX_KLEENE_STAR_OP = "*"
    _REGEX_CONCAT_OP = "."
    _REGEX_ALTERNATION_OP = "|"
    _REGEX_EMPTY_STR = "_ε"
    _REGEX_ESCAPE_CHAR = "\\"
    _next_state_id = 0

    def __init__(self, raw_regex: str) -> None:
        RegexParser._next_state_id = 0
        self._raw_regex = raw_regex
        self._escaped_regex = self._escape_regex(self._raw_regex)
        self._preprocessed_regex = self._preprocess_regex(self._escaped_regex)
        self._converted_regex = self._convert_regex(self._preprocessed_regex)
        self._expression_tree = self._create_expression_tree(self._converted_regex)
        self._nfa = self._build_nfa(self._expression_tree)

    @property
    def raw_regex(self) -> str:
        return self._raw_regex

    @property
    def escaped_regex(self) -> str:
        return "".join((symbol for (symbol, _) in self._escaped_regex))

    @property
    def preprocessed_regex(self) -> str:
        return "".join((symbol for (symbol, _) in self._preprocessed_regex))

    @property
    def converted_regex(self) -> str:
        return "".join((symbol for (symbol, _) in self._converted_regex))

    @property
    def expression_tree(self) -> ExprTree:
        return self._expression_tree

    @property
    def nfa(self) -> NFA:
        return self._nfa

    def recognize_word(self, test_word: str) -> bool:
        if not isinstance(test_word, str):
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
                (symbol, _) = root.character
                self._join_on_operand(empty_nfa, symbol)
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

    def _convert_regex(self, preprocessed_regex: CharacterList) -> CharacterList:
        stack: CharacterList = []
        converted_regex: CharacterList = []

        for character in preprocessed_regex:
            next_char = character

            if self._is_operand(next_char):
                converted_regex.append(next_char)
            elif self._is_left_parenthesis(next_char):
                stack.append(next_char)
            elif self._is_right_parenthesis(next_char):
                while not self._is_left_parenthesis(stack[-1]):
                    converted_regex.append(stack.pop())
                stack.pop()
            else:
                while len(stack) != 0 and self._get_precedence(
                    next_char
                ) <= self._get_precedence(stack[-1]):
                    converted_regex.append(stack.pop())
                stack.append(next_char)

        while len(stack) != 0:
            converted_regex.append(stack.pop())

        return converted_regex

    def _preprocess_regex(self, escaped_regex: CharacterList) -> CharacterList:
        preprocessed_regex: CharacterList = []
        pred_char = ("", False)
        current_char = ("", False)
        for character in escaped_regex:
            pred_char = current_char
            current_char = character

            if (
                (self._is_operand(pred_char) and self._is_operand(current_char))
                or (
                    self._is_kleene_star_operator(pred_char)
                    and self._is_operand(current_char)
                )
                or (
                    self._is_kleene_star_operator(pred_char)
                    and self._is_left_parenthesis(current_char)
                )
                or (
                    self._is_left_parenthesis(pred_char)
                    and self._is_right_parenthesis(current_char)
                )
                or (
                    self._is_right_parenthesis(pred_char)
                    and self._is_operand(current_char)
                )
                or (
                    self._is_operand(pred_char)
                    and self._is_left_parenthesis(current_char)
                )
            ):
                preprocessed_regex.extend(
                    ((RegexParser._REGEX_CONCAT_OP, False), current_char)
                )
            else:
                preprocessed_regex.append(current_char)

        return preprocessed_regex

    def _escape_regex(self, raw_regex: str) -> CharacterList:
        if not raw_regex:
            raise ValueError("The regex passed in cannot be empty")

        escaped_regex: CharacterList = []
        escaped = False
        for symbol in raw_regex:
            if self._is_escape_character((symbol, escaped)):
                escaped = True
            else:
                escaped_regex.append((symbol, escaped))
                escaped = False

        return escaped_regex

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

    def _get_precedence(self, character: Character) -> int:
        if self._is_kleene_star_operator(character):
            return 3
        elif self._is_concat_operator(character):
            return 2
        elif self._is_alternation_operator(character):
            return 1
        else:
            return -1

    def _is_operand(self, character: Character) -> bool:
        (symbol, escaped) = character
        return symbol != "" and (
            (
                symbol != RegexParser._REGEX_KLEENE_STAR_OP
                and symbol != RegexParser._REGEX_CONCAT_OP
                and symbol != RegexParser._REGEX_ALTERNATION_OP
                and symbol != RegexParser._REGEX_LEFT_PAR
                and symbol != RegexParser._REGEX_RIGHT_PAR
            )
            or escaped
        )

    def _is_concat_operator(self, character: Character) -> bool:
        (symbol, escaped) = character
        return symbol == RegexParser._REGEX_CONCAT_OP and not escaped

    def _is_alternation_operator(self, character: Character) -> bool:
        (symbol, escaped) = character
        return symbol == RegexParser._REGEX_ALTERNATION_OP and not escaped

    def _is_kleene_star_operator(self, character: Character) -> bool:
        (symbol, escaped) = character
        return symbol == RegexParser._REGEX_KLEENE_STAR_OP and not escaped

    def _is_left_parenthesis(self, character: Character) -> bool:
        (symbol, escaped) = character
        return symbol == RegexParser._REGEX_LEFT_PAR and not escaped

    def _is_right_parenthesis(self, character: Character) -> bool:
        (symbol, escaped) = character
        return symbol == RegexParser._REGEX_RIGHT_PAR and not escaped

    def _is_escape_character(self, character: Character) -> bool:
        (symbol, escaped) = character
        return symbol == RegexParser._REGEX_ESCAPE_CHAR and not escaped


if __name__ == "__main__":

    def test():
        regex = "ab|c*d|asdf|(a(adf)*)"
        parser = RegexParser(regex)

        print()
        print(f"Tests for {parser.raw_regex}:")
        print()

        test_word = ""
        print(f'\t" " is recognized: {parser.recognize_word(test_word)}')

        test_word = "ab"
        print(f'\t"{test_word}" is recognized: {parser.recognize_word(test_word)}')

        test_word = "cd"
        print(f'\t"{test_word}" is recognized: {parser.recognize_word(test_word)}')

        test_word = "asdf"
        print(f'\t"{test_word}" is recognized: {parser.recognize_word(test_word)}')

        test_word = "cccccccd"
        print(f'\t"{test_word}" is recognized: {parser.recognize_word(test_word)}')

        test_word = "ccccccccccccd"
        print(f'\t"{test_word}" is recognized: {parser.recognize_word(test_word)}')

        test_word = "aadfadf"
        print(f'\t"{test_word}" is recognized: {parser.recognize_word(test_word)}')

        test_word = None
        print(f"\t{test_word} is recognized: {parser.recognize_word(test_word)}")

        test_word = 234
        print(f"\t{test_word} is recognized: {parser.recognize_word(test_word)}")

        print()

    test()
