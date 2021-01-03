from typing import NamedTuple, Optional, Union, Callable, List
from typing_extensions import Literal

from .request import Req


AuthPolicy = Union[
    Literal["user-owns"],
    Literal["user-belongs-to"],
    Literal["user-has-permissions"],
]


TokenType = Union[Literal["session"], Literal["refresh"]]


class AuthConf(NamedTuple):
    policy: AuthPolicy
    obj_ids: Optional[Callable[[Req], List[str]]]
