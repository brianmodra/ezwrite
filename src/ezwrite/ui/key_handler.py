import tkinter as tk
from collections.abc import Callable
from typing import List


class Key():
    """state of a key that was pressed"""
    def __init__(
            self,
            char: str,
            keysym: str,
            button_num: int,
            widget: tk.Misc,
            x: int,
            y: int
    ): # pylint: disable=too-many-arguments
        self.char = char
        self.keysym = keysym
        self.button_num = button_num
        self.widget = widget
        self.x1 = x
        self.y1 = y
        self.x2 = x
        self.y2 = y
        self.released = False
        self.moved = False


class KeyHandler():
    """This key handler converts low level events into higher level to combine
    actions like control-B into one event, and key press/release to key click."""

    def __init__(self, canvas: tk.Canvas):
        self._keys: List[Key] = []
        self._handlers: List[Callable[[tk.Event, List[Key]], bool]] = []
        canvas.bind_all('<KeyPress>', self.key_press)
        canvas.bind_all('<KeyRelease>', self.key_release)
        canvas.bind_all('<Button-1>', self.key_press)
        canvas.bind_all('<ButtonRelease-1>', self.key_release)
        canvas.bind_all('<Motion>', self.mouse_moved)

    def add_handler(self, handler: Callable[[tk.Event, List[Key]], bool]):
        self._handlers.append(handler)

    def mouse_moved(self, event: tk.Event) -> None:
        for key in self._keys:
            if key.keysym[0:7] == "<Button" and not key.released:
                key.moved = True
                key.x2 = event.x
                key.y2 = event.y
                for handler in self._handlers:
                    if handler(event, self._keys):
                        return

    def key_press(self, event: tk.Event) -> None:
        if event.type == tk.EventType.KeyPress:
            key = Key(event.char, event.keysym, -1, event.widget, 0, 0)
        elif event.type == tk.EventType.ButtonPress:
            key = Key("", f"<Button-{event.num}>", event.num, event.widget, event.x, event.y)
        else:
            return
        self._keys.append(key)

    def key_release(self, event: tk.Event) -> None:
        if event.type == tk.EventType.KeyRelease:
            keysym = event.keysym
            release_x = 0
            release_y = 0
        elif event.type == tk.EventType.ButtonRelease:
            keysym = f"<Button-{event.num}>"
            release_x = event.x
            release_y = event.y
        else:
            return
        all_released: bool = True
        for key in self._keys:
            if keysym == key.keysym:
                key.released = True
                key.x2 = release_x
                key.y2 = release_y
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
