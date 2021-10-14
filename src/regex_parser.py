from typing import List
from expression_tree import ExprTree
from nfa import NFA


class RegexParser:
    _REGEX_LEFT_PAR = "("
    _REGEX_RIGHT_PAR = ")"
    _REGEX_KLEENE_STAR_OP = "*"
    _REGEX_CONCAT_OP = "."
    _REGEX_ALTERNATION_OP = "|"

    def __init__(self, regex: str) -> None:
        self._raw_regex = regex
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
    def nfa(self) -> NFA:
        return self._nfa

    def _build_nfa(self, root: ExprTree) -> NFA:
        if root is not None:
            left_nfa = self._build_nfa(root.left_child)
            right_nfa = self._build_nfa(root.right_child)
            empty_nfa = NFA()
            if self._is_operand(root.character):
                return empty_nfa.join_on_operand(root.character)
            elif self._is_kleene_star_operator(root.character):
                return empty_nfa.join_on_kleene_star_operator(left_nfa)
            elif self._is_alternation_operator(root.character):
                return empty_nfa.join_on_alternation_operator(left_nfa, right_nfa)
            elif self._is_concat_operator(root.character):
                return empty_nfa.join_on_concat_operator(left_nfa, right_nfa)

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
    # regex = "ab|c*d|asdf|(a(adf)*)"
    regex = "(a|b|c|d)*"
    parser = RegexParser(regex)
    print(f"Raw regex in infix notation:\t\t {parser.raw_regex}")
    print(f"Preprocessed regex in infix notation:\t {parser.preprocessed_regex}")
    print(f"Converted regex in postfix notation:\t {parser.converted_regex}")
    nfa = parser.nfa
    print(nfa)
