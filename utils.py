import re
from typing import Any, Callable, Type

from pydash import flow

type Converter = Type[Any] | Callable[..., Any]

def apply(*map_funcs: Converter) -> Callable:
    def decorator(f: Callable) -> Callable[..., Converter]:
        def wrapper(*args: Any, **kwarg: Any) -> Any:
            return flow(*map_funcs)(f(*args, **kwarg))
        return wrapper
    return decorator


def remove_color(s: str) -> str:
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', s)
