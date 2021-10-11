from typing import Optional


class ExprTree:
    def __init__(
        self,
        character: str,
        left_child: Optional["ExprTree"] = None,
        right_child: Optional["ExprTree"] = None,
    ) -> None:
        self.left_child = left_child
        self.right_child = right_child
        self.character = character
