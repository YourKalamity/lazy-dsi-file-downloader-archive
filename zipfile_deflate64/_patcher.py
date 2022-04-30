import functools
from typing import Any, Callable, Dict


class patch:  # noqa: N801
    originals: Dict[str, Any] = {}

    def __init__(self, host: Any, name: str):
        self.host = host
        self.name = name

    def __call__(self, func: Callable):
        original = getattr(self.host, self.name)
        self.originals[self.name] = original

        functools.update_wrapper(func, original)

        setattr(self.host, self.name, func)

        return func
