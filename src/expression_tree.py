from __future__ import annotations

from simple_data_structures import Character


class ExprTree:
    def __init__(
        self,
        character: Character,
        left_child: ExprTree = None,
        right_child: ExprTree = None,
    ) -> None:
        self.left_child = left_child
        self.right_child = right_child
        self.character = character

    def __str__(self) -> str:
        expression_tree_repr = "Generated Expression Tree:\n"
        expression_tree_repr += self._print_expression_tree(0, self)
        return expression_tree_repr

    def _print_expression_tree(self, indentation: int, root: ExprTree) -> str:
        if root is not None:
            right_repr = self._print_expression_tree(indentation + 1, root.right_child)
            (root_symbol, _) = root.character
            central_repr = "\t\t\t  |" + "\t\t" * indentation + f"({root_symbol})"
            if root.left_child != None:
                (left_child_symbol, _) = root.left_child.character
                central_repr += f":({left_child_symbol})"
            if root.right_child != None:
                (right_child_symbol, _) = root.right_child.character
                central_repr += f"({right_child_symbol})"
            central_repr += "\n"
            right_repr += central_repr
            left_repr = self._print_expression_tree(indentation + 1, root.left_child)
            right_repr += left_repr

            return right_repr
        else:
            return ""
