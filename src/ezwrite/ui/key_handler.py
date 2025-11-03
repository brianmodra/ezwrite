import tkinter as tk
from collections.abc import Callable
from typing import List


class Key():
    """state of a key that was pressed"""
    def __init__(self, char: str, keysym: str):
        self.char = char
        self.keysym = keysym
        self.released = False

class KeyHandler():
    """This key handler converts low level events into higher level to combine
    actions like control-B into one event, and key press/release to key click."""

    def __init__(self, canvas: tk.Canvas):
        self._keys: List[Key] = []
        self._handlers: List[Callable[[tk.Event, List[Key]], bool]] = []
        canvas.bind_all('<KeyPress>', self.key_press)
        canvas.bind_all('<KeyRelease>', self.key_release)

    def add_handler(self, handler: Callable[[tk.Event, List[Key]], bool]):
        self._handlers.append(handler)

    def key_press(self, event: tk.Event) -> None:
        key = Key(event.char, event.keysym)
        self._keys.append(key)

    def key_release(self, event: tk.Event) -> None:
        all_released: bool = True
        for key in self._keys:
            if key.keysym == event.keysym:
                key.released = True
            elif not key.released:
                all_released = False
        if all_released:
            handled: bool = False
            for handler in self._handlers:
                if handler(event, self._keys):
                    handled = True
                    break
            if not handled:
                print("unhandled key sequence: " + ", ".join(map(lambda key: key.keysym, self._keys)))
            self._keys.clear()
