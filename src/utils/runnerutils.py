from enum import Enum
import math
from typing import TypeAlias


_argsList: TypeAlias = tuple[str | int | bytes | bytearray | bool]
_kwArgsType:  TypeAlias = dict[str | int ]


def clear_terminal_display():
    import os
    columns, lines = os.get_terminal_size() 
    for _ in range(lines):
        print("\033[H\033[J", end="")
        print("\033[H\033[J", end="")
    return (columns, lines)

def bytes_verbose(obj=None, size_bytes:int=0) -> str:
    import sys
    if obj:
        size_bytes = sys.getsizeof(obj)
    
    if size_bytes == 0:
       return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
                     

class pipeType(Enum):
    STDIN = "stdin"
    STDOUT = "stdout"
    PIPE = "pipe"