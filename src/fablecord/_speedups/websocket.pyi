from collections.abc import Buffer
from collections import deque

def frame(opcode: int, key: int, payload: Buffer, /) -> bytes:
    ...

def parse(buffer: Buffer, offset: int, max_size: int, messages: deque[str | bytes], /) -> int:
    ...