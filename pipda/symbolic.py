from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .expression import Expression

if TYPE_CHECKING:
    from .context import ContextType


class Symbolic(Expression):
    """The symbolic class, works as a proxy to represent the data

    In most cases it is used to construct the Reference objects.
    """
    _pipda_level = 0

    def __str__(self) -> str:
        return ""

    def _pipda_eval(self, data: Any, context: ContextType = None) -> Any:
        """When evaluated, this should just return the data directly"""
        return data
