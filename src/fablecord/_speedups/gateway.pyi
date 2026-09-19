from collections.abc import Buffer

def peek(payload: Buffer, /) -> tuple[int, int | None, str | None] | None:
    ...