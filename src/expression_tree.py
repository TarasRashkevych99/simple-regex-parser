from __future__ import annotations


class ExprTree:
    def __init__(
        self,
        character: str,
        left_child: ExprTree = None,
        right_child: ExprTree = None,
    ) -> None:
        self.left_child = left_child
        self.right_child = right_child
        self.character = character
