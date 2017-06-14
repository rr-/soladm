import os
from typing import Any, List


def tail(handle: Any, lines: int, _buffer: int = 256) -> List[bytes]:
    lines_found: List[bytes] = []
    block_counter = -1
    while len(lines_found) < lines + 1:
        try:
            handle.seek(block_counter * _buffer, os.SEEK_END)
        except IOError as ex:
            handle.seek(0)
            return handle.readlines()
        lines_found = handle.readlines()
        block_counter -= 1
    return lines_found[-lines:]
