import tkinter as tk
from argparse import ArgumentTypeError
from typing import List, Optional, Tuple, override

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.editors.chapter_editor import ChapterEditor
from ezwrite.editors.ez_editor import EzEditor
from ezwrite.graph.ezentity import Entity, EntityTraversal
from ezwrite.graph.ezproperty import EzProperty
from ezwrite.ui.key_handler import Key, KeyHandler
from ezwrite.ui.paragraph import Paragraph, ParagraphContainer
from ezwrite.ui.tok import AbstractToken, RelativeCursor, Tok
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
        self._editor = ChapterEditor()
        key_handler = KeyHandler(self._canvas)
        key_handler.add_handler(self.handle_arrow_click)
        key_handler.add_handler(self.handle_editing_keys)
        key_handler.add_handler(self.handle_typed_character)
        key_handler.add_handler(self.handle_mouse_button_1)
        key_handler.add_handler(self.handle_mouse_moved_1)

    @override
    def is_container(self) -> bool:
        return True

    @override
    @property
    def x(self) -> int:
        return self._canvas.winfo_x()

    @override
    @property
    def y(self) -> int:
        return self._canvas.winfo_y()

    @override
    @property
    def root_x(self) -> int:
        return self._canvas.winfo_rootx()

    @override
    @property
    def root_y(self) -> int:
        return self._canvas.winfo_rooty()

    @override
    @property
    def width(self) -> int:
        return self._canvas.winfo_width()

    @override
    @property
    def height(self) -> int:
        return self._canvas.winfo_height()

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

    def handle_mouse_moved_1(self, _event: tk.Event, keys: List[Key]) -> bool:
        if len(keys) != 1:
            return False
        key = keys[0]
        if key.keysym != "<Button-1>" or not key.moved:
            return False
        print(f"mouse moved {key.x2},{key.y2}")
        return True

    @staticmethod
    def select_token(ent: Entity) -> None:
        if not isinstance(ent, Tok):
            return
        tok: Tok = ent
        tok.select()

    def handle_mouse_button_1(self, _event: tk.Event, keys: List[Key]) -> bool:
        if len(keys) != 1:
            return False

        key = keys[0]
        if key.keysym != "<Button-1>" or not key.released:
            return False

        entity = self.widget_inside(key.widget)
        if not entity:
            print(f"location outside: x={key.x1}, y={key.y1}")
            return False

        rel_press = self._handle_press(entity, key)
        if rel_press is None:
            return False

        rel_release = self._handle_release(entity, key)
        if rel_release is None or rel_press is None:
            return True

        self._apply_selection(rel_press, rel_release)
        return True

    def _handle_press(self,
                      entity: Entity,
                      key: Key
                      ) -> Optional[RelativeCursor]:
        """Return (token, relative_cursor, paragraph) or (None, None, None)."""
        tok: Tok
        if isinstance(entity, Paragraph) or isinstance(entity, Chapter):
            print(f"paragraph: x={key.x1}, y={key.y1}")
            ex = entity.root_x + key.x1
            ey = entity.root_y + key.y1
            closest = entity.get_closest_token(ex, ey)
            if closest is None or not isinstance(closest, Tok):
                print("Could not find token close to paragraph")
                return None
            tok = closest
            if tok == tok.parent.first_child():
                rel_press = tok.calculate_cursor_x(0)
            elif tok == tok.parent.last_child():
                rel_press = tok.calculate_cursor_x(tok.width)
            else:
                rel_press = tok.calculate_cursor_x(ex - tok.root_x)
        elif isinstance(entity, Tok):
            tok = entity
            tok.place_cursor_x(key.x1)
            print(f"token: {tok.word} x={key.x1}, y={key.y1}")
            if tok.parent is None:
                print("parent of Tok cannot be None")
                return None
            parent = tok.parent.parent  # Paragraph
            if parent is None or not isinstance(parent, Paragraph):
                print("grandparent of Tok must be a Paragraph")
                return None
            rel_press = tok.calculate_cursor_x(key.x1)
        else:
            print("Could not find entity near press")
            return None

        tok.place_cursor_at_word_index_and_x_position(rel_press.word_index, rel_press.x)
        return rel_press

    def _handle_release(self,
                        entity: Entity,
                        key: Key
                        ) -> Optional[RelativeCursor]:
        """Return rel_release or None (meaning early exit but no error)."""
        tok_release: Tok
        if isinstance(entity, Paragraph) or isinstance(entity, Chapter):
            print(f"paragraph release: x={key.x2}, y={key.y2}")
            ex = entity.root_x + key.x2
            ey = entity.root_y + key.y2
            closest = self.get_closest_token(ex, ey)
            if closest is None or not isinstance(closest, Tok):
                print("No token near paragraph on release")
                return None
            tok_release = closest
            if tok_release == tok_release.parent.first_child():
                return tok_release.calculate_cursor_x(0)
            if tok_release == tok_release.parent.last_child():
                return tok_release.calculate_cursor_x(tok_release.width)
            return tok_release.calculate_cursor_x(ex - tok_release.root_x)

        # entity is a Tok
        if not isinstance(entity, Tok) or entity.parent is None:
            print("entity must be Tok or Paragraph, and parent of Tok cannot be None")
            return None

        canvas = entity.canvas
        ex = canvas.winfo_rootx() + key.x2
        ey = canvas.winfo_rooty() + key.y2
        ent_release = self.get_closest_token(ex, ey)
        if ent_release is None or not isinstance(ent_release, Tok):
            print("Could not find closest token on release")
            return None

        tok_release = ent_release
        rel_x = ex - tok_release.canvas.winfo_rootx()
        return tok_release.calculate_cursor_x(rel_x)

    def _apply_selection(self,
                         rel_press: RelativeCursor,
                         rel_release: RelativeCursor
                         ) -> bool:
        """Apply selection logic exactly as before."""
        self.deselect_all()

        if rel_release.token == rel_press.token:
            if rel_release.word_index == rel_press.word_index:
                return True
            if rel_release.word_index < rel_press.word_index:
                rel_press.token.select(rel_release.word_index, rel_press.word_index)
            else:
                rel_press.token.select(rel_press.word_index, rel_release.word_index)
        else:
            traversal = EntityTraversal(rel_press.token, rel_release.token, Chapter.select_token)
            traversal.traverse_leaf_entities_between(self)
            if traversal.ent_first != rel_press.token:
                rel_release.token.select(rel_release.word_index, -1)
                rel_press.token.select(0, rel_press.word_index)
            else:
                rel_press.token.select(rel_press.word_index, -1)
                rel_release.token.select(0, rel_release.word_index)

        return True

    def get_closest_token(self, x: int, y: int) -> Entity | None:
        closest_dd: int = 0
        closest: Tok | None = None
        for child in self.child_entities:
            if not isinstance(child, Paragraph):
                continue
            paragraph: Paragraph = child
            ent = paragraph.get_closest_token(x, y)
            if ent is not None and isinstance(ent, Tok):
                tok: Tok = ent
                if tok.inside(x, y):
                    return tok
                tok_x1 = tok.root_x
                tok_y1 = tok.root_y
                tok_x2 = tok_x1 + tok.width - 1
                tok_y2 = tok_y1 + tok.height - 1
                xx = (tok_x1 + tok_x2) // 2
                yy = (tok_y1 + tok_y2) // 2
                dx = x - xx
                dy = y - yy
                dd = dx * dx + dy * dy
                # if it is closer than the last one
                if closest is None or dd < closest_dd:
                    closest = tok
                    closest_dd = dd
        return closest

    def handle_arrow_click(self, event: tk.Event, keys: List[Key]) -> bool:
        if len(keys) != 1:
            return False
        keysym: str = keys[0].keysym
        if keysym not in ('Left', 'Right', 'Up', 'Down'):
            return False
        entity: Entity | None = self.widget_inside(event.widget)
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
        entity: Entity | None = self.widget_inside(event.widget)
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
        entity: Entity | None = self.widget_inside(event.widget)
        if entity is None:
            return False
        if not isinstance(entity, Tok):
            return False
        tok: Tok = entity
        # TODO: finish this
        return False

    def widget_inside(self, widget: tk.Misc) -> Entity | None:
        for child in self.child_entities:
            if not isinstance(child, Paragraph):
                continue
            paragraph: Paragraph = child
            entity: Entity | None = paragraph.widget_inside(widget)
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

    @override
    def deselect_all(self) -> None:
        for child in self.child_entities:
            if not isinstance(child, Paragraph):
                continue
            paragraph: Paragraph = child
            paragraph.deselect_all()
