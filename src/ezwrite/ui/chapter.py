import tkinter as tk
from argparse import ArgumentTypeError
from typing import List, override

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.editors.chapter_editor import ChapterEditor
from ezwrite.editors.ez_editor import EzEditor
from ezwrite.graph.ezentity import Entity
from ezwrite.graph.ezproperty import EzProperty
from ezwrite.ui.key_handler import Key, KeyHandler
from ezwrite.ui.paragraph import Paragraph, ParagraphContainer
from ezwrite.ui.tok import AbstractToken, Tok
from ezwrite.utils.lock import Lock


class Chapter(ParagraphContainer):
    """The entire canvas of the editor is (at one point in time) a chapter of the book.
    It contains the paragraphs, and the canvas is scrollable."""
    def __init__(self, frame: tk.Frame, graph: Graph):
        super().__init__(graph, URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Chapter"))
        self._lock: Lock = Lock()
        self._laying_out: bool = True
        self._frame = frame
        self._laying_out = False
        self._graph = graph
        self._canvas = tk.Canvas(frame, bg="white", cursor="arrow")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind("<Configure>", self.on_resize)
        self._frame.bind_all('<Button-1>', self._handle_mouse_button_1)
        self._editor = ChapterEditor()
        key_handler = KeyHandler(self._canvas)
        key_handler.add_handler(self.handle_arrow_click)
        key_handler.add_handler(self.handle_editing_keys)
        key_handler.add_handler(self.handle_typed_character)

    @property
    @override
    def editor(self) -> EzEditor:
        return self._editor

    @property
    @override
    def canvas(self) -> tk.Canvas:
        return self._canvas

    @property
    def graph(self) -> Graph:
        return self._graph

    def _handle_mouse_button_1(self, event: tk.Event) -> None:
        entity: Entity | None = self.inside(event.widget)
        if entity is None:
            print(f"location outside: x={event.x}, y={event.y}")
            return
        if isinstance(entity, Chapter):
            print(f"chapter: x={event.x}, y={event.y}")
            return
        if isinstance(entity, Paragraph):
            print(f"paragraph: x={event.x}, y={event.y}")
            paragraph: Paragraph = entity
            closest: Entity | None = paragraph.get_closest_token(event.widget, event.x, event.y)
            if closest is not None and isinstance(closest, Tok):
                closest_tok: Tok = closest
                closest_tok.place_cursor_x(min(max(event.x - closest_tok.x, 0), closest_tok.width))
                print(f"token: {closest_tok.word} x={event.x}, y={event.y}")
        if isinstance(entity, Tok):
            tok: Tok = entity
            tok.place_cursor_x(event.x)
            print(f"token: {tok.word} x={event.x}, y={event.y}")
            return

    def handle_arrow_click(self, event: tk.Event, keys: List[Key]) -> bool:
        if len(keys) != 1:
            return False
        keysym: str = keys[0].keysym
        if keysym not in ('Left', 'Right', 'Up', 'Down'):
            return False
        entity: Entity | None = self.inside(event.widget)
        if entity is None:
            return False
        if not isinstance(entity, Tok):
            return False
        tok: Tok = entity
        match keysym:
            case "Left":
                tok.move_left()
            case "Right":
                tok.move_right()
            case "Up":
                tok.move_up()
            case "Down":
                tok.move_down()
        return True

    def handle_editing_keys(self, event: tk.Event, keys: List[Key]) -> bool:
        entity: Entity | None = self.inside(event.widget)
        if entity is None:
            return False
        if not isinstance(entity, Tok):
            return False
        tok: Tok = entity
        if len(keys) == 1 and keys[0].keysym == "BackSpace":
            if tok.editor.delete_character_left(tok):
                self.cleanup_empty_containers()
                return True
        return False

    def handle_typed_character(self, event: tk.Event, keys: List[Key]) -> bool:
        if len(keys) != 1:
            return False
        keysym: str = keys[0].keysym
        entity: Entity | None = self.inside(event.widget)
        if entity is None:
            return False
        if not isinstance(entity, Tok):
            return False
        tok: Tok = entity
        # TODO: finish this
        return False

    def inside(self, widget: tk.Misc) -> Entity | None:
        for child in self.child_entities:
            if not isinstance(child, Paragraph):
                continue
            paragraph: Paragraph = child
            entity: Entity | None = paragraph.inside(widget)
            if entity is not None:
                return entity
        if self._canvas == widget:
            return self
        return None

    @override
    def add_child_entity(self, child: Entity) -> None:
        if not isinstance(child, Paragraph):
            raise ArgumentTypeError("token_container needs to be an instance of Sentence")
        paragraph: Paragraph = child
        self._property_list.append(EzProperty.HAS_PART, paragraph)

    @override
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        for child in self.child_entities:
            if not isinstance(child, Paragraph): raise ArgumentTypeError("children need to be instances of Paragraph")
            paragraph: Paragraph = child
            paragraph.remove_cursor_except(tok)

    def on_resize(self, event: tk.Event) -> None:
        """Called when the canvas is resized."""
        print(f"Canvas resized to {event.width}x{event.height} width = {self._canvas.winfo_width()}")

        self.layout()

    def layout(self) -> None:
        with self._lock:
            if self._laying_out:
                return
            self._laying_out = True

        canvas_width: int = self._canvas.winfo_width()
        frame_y_offset: int = 0
        for child in self.child_entities:
            if not isinstance(child, Paragraph): raise ArgumentTypeError("children need to be instances of Paragraph")
            paragraph: Paragraph = child
            frame_height: int = paragraph.layout(frame_y_offset, canvas_width)
            frame_y_offset += frame_height + paragraph.max_tok_height

        with self._lock:
            self._laying_out = False

    @property
    @override
    def parent(self) -> Entity | None:
        return None

    @property
    @override
    def child_entities(self) -> List[Entity]:
        return self._property_list.entities_of(EzProperty.HAS_PART, Paragraph)
