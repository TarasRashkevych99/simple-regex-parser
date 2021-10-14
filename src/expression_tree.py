from __future__ import annotations


class ExprTree:
    def __init__(
        self, character: str, left_child: ExprTree = None, right_child: ExprTree = None
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
            central_repr = "\t\t\t  |" + "\t\t" * indentation + f"({root.character})"
            if root.left_child != None:
                central_repr += f":({root.left_child.character})"
            if root.right_child != None:
                central_repr += f"({root.right_child.character})"
            central_repr += "\n"
            right_repr += central_repr
            left_repr = self._print_expression_tree(indentation + 1, root.left_child)
            right_repr += left_repr

            return right_repr
        else:
            return ""
