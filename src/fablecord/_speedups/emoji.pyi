from typing import Any, Self

from ..asset import Asset
from ..state import State

class EmojiBase:
    name: str
    id: int | None
    animated: bool
    _state: State | None
    _url: Asset

    @classmethod
    def from_dict(cls, state: State | None, data: dict[str, Any], /) -> Self:
        ...