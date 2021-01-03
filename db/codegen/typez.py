from enum import Enum
from typing import List, NamedTuple, Tuple, Optional, Any, Union, Literal


class DefineLang(Enum):
    scala = "scala"
    python = "python"


class OutputObjType(Enum):
    views = "views"
    fns = "fns"


class FnArg(NamedTuple):
    name: str
    type: str
    default: Optional[Any] = None


class FnRecord(NamedTuple):
    name: str
    ret_type: str
    args: List[FnArg]


class ColumnRecord(NamedTuple):
    name: str
    type: str


class TableRecord(NamedTuple):
    name: str
    columns: List[ColumnRecord]
