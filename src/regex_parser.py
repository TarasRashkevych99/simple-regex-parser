from typing import NoReturn
from expression_tree import ExpressionTree


class RegexParser:
    _REGEX_LEFT_PAR = "("
    _REGEX_RIGHT_PAR = ")"
    _REGEX_KLEENE_STAR_OP = "*"
    _REGEX_CONCAT_OP = "."
    _REGEX_ALTERNATION_OP = "|"

    def __init__(self, regex: str) -> None:
        self._regex_in_infix_notation_raw = regex
        self._regex_in_infix_notation_preprocessed = self._preprocess_regex(regex)
        self._regex_in_postfix_notation = ""
        self._expression_tree = None

    @property
    def regex_in_infix_notation_raw(self) -> str:
        return self._regex_in_infix_notation_raw

    @property
    def regex_in_infix_notation_preprocessed(self) -> str:
        return self._regex_in_infix_notation_preprocessed

    @property
    def regex_in_postfix_notation(self) -> str:
        if self._regex_in_postfix_notation:
            return self._regex_in_postfix_notation
        else:
            raise ValueError(
                "The regex has not been parsed. Please call the convert_from_infix_to_postfix() method."
            )

    def convert_from_infix_to_postfix_notation(self) -> None:
        stack = []

        for i in range(len(self._regex_in_infix_notation_preprocessed)):
            next_char = self._regex_in_infix_notation_preprocessed[i]

            if self._is_operand(next_char):
                self._regex_in_postfix_notation += next_char
            elif next_char == RegexParser._REGEX_LEFT_PAR:
                stack.append(RegexParser._REGEX_LEFT_PAR)
            elif next_char == RegexParser._REGEX_RIGHT_PAR:
                while stack[-1] != RegexParser._REGEX_LEFT_PAR:
                    self._regex_in_postfix_notation += stack.pop()
                stack.pop()
            else:
                while len(stack) != 0 and self._get_precedence(
                    next_char
                ) <= self._get_precedence(stack[-1]):
                    self._regex_in_postfix_notation += stack.pop()
                stack.append(next_char)

        while len(stack) != 0:
            self._regex_in_postfix_notation += stack.pop()

    def create_expression_tree(self) -> None:
        stack = []

        for character in self.regex_in_postfix_notation:
            if self._is_kleene_star_operator(character):
                left_child = stack.pop()
                stack.append(ExpressionTree(character, left_child))
            elif self._is_concat_operator(character) or self._is_alternation_operator(
                character
            ):
                right_child = stack.pop()
                left_child = stack.pop()
                stack.append(ExpressionTree(character, left_child, right_child))
            else:
                stack.append(ExpressionTree(character))

        self._expression_tree = stack[-1]

    def _preprocess_regex(self, regex: str) -> str:
        if not regex:
            return regex

        preprocessed_regex = ""
        pred_char = ""
        current_char = ""
        for i in range(len(regex)):
            pred_char = current_char
            current_char = regex[i]

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
    regex = "ab|c*d|asdf|(a(adf)*)"
    parser = RegexParser(regex)
    print(f"Raw regex in infix notation:\t\t {parser.regex_in_infix_notation_raw}")
    print(
        f"Preprocessed regex in infix notation:\t {parser.regex_in_infix_notation_preprocessed}"
    )
    parser.convert_from_infix_to_postfix_notation()
    print(f"Parsed regex in postfix notation:\t {parser.regex_in_postfix_notation}")
