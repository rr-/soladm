from typing import Any, List, Callable


class EventHandler:
    def __init__(self) -> None:
        self.funcs: List[Callable] = []

    def append(self, func: Callable) -> None:
        self.funcs.append(func)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        for func in self.funcs:
            func(*args, **kwargs)
