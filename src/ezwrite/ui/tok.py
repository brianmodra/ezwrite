import tkinter as tk
import tkinter.font
from abc import ABC, abstractmethod
from argparse import ArgumentTypeError
from typing import List, Optional, Tuple, override

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.editors.ez_editor import EzEditor
from ezwrite.graph.ezentity import Entity, EzEntity
from ezwrite.graph.graph_token import GraphToken
from ezwrite.ui.position import Position


class EditableEntity(ABC):
    """provides functions needed to make an entity editable"""
    @property
    @abstractmethod
    def editor(self) -> EzEditor:
        pass

    @property
    @abstractmethod
    def parent(self) -> Optional[Entity]:
        pass

    def get_root_container(self) -> "RootContainer":
        container: EzwriteContainer | None = None
        entity: Entity | None = self.parent
        while entity is not None:
            if not isinstance(entity, EzwriteContainer):
                break
            container = entity
            entity = entity.parent
        if container is None:
            raise ValueError("root container can't be found")
        if not isinstance(container, RootContainer):
            raise ValueError("Root container must be an instance of RootContainer")
        parent: RootContainer = container
        return parent

    def get_root_editor(self) -> EzEditor:
        parent: EzwriteContainer = self.get_root_container()
        root_editor: EzEditor = parent.editor
        return root_editor

class AbstractToken(GraphToken, EditableEntity, ABC):
    """This provides an interface to manipulate a token, without specifying
    the actual implementation of the token"""
    def __init__(self, graph: Graph):
        super().__init__(graph)

    @abstractmethod
    def remove_cursor(self) -> None:
        pass

    @abstractmethod
    def place_cursor(self, pos: Position) -> None:
        pass

    @property
    @abstractmethod
    def canvas(self) -> tk.Canvas:
        pass


class EzwriteContainer(EzEntity, EditableEntity, ABC):
    """A generic container interface for all objects in the UI that contain others,
    for example, sentence, paragraph, and chapter."""
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)

    @abstractmethod
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        pass

    @abstractmethod
    def deselect_all(self) -> None:
        pass

    def get_selected(self) -> List["Tok"]:
        selected: List["Tok"] = []
        for child in self.child_entities:
            if isinstance(child, Tok):
                tok: Tok = child
                selected.extend(tok.get_selected())
                continue
            if not isinstance(child, EzwriteContainer):
                continue
            container: EzwriteContainer = child
            selected.extend(container.get_selected())
        return selected

class RootContainer(EzwriteContainer, ABC):
    """Generic class of the container of other containers - the root of a document"""
    @abstractmethod
    def layout(self) -> None:
        pass

    @abstractmethod
    def set_layout_needed(self) -> None:
        pass


class TokenContainer(EzwriteContainer, ABC):
    """This is more specifically an abstractrion of a sentence"""
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)

    @abstractmethod
    def layout(self, pos: Position, frame_width: int) -> int:
        pass

    @abstractmethod
    def parent_frame(self) -> tk.Frame:
        pass


class RelativeCursor():
    """Used to contain a cursor position relative to a token"""
    def __init__(self, x: int, word_index: int, token: "Tok"):
        self.x = x
        self.word_index = word_index
        self.token = token

class Tok(AbstractToken):
    """A Tok is a token (could not use the name 'Token' - already in use)
    It is the smallest entity in the knowledge graph to describe the text.
    It could be a word, punctuation, whitespace, or the end of a word, e.g.
    In the word: Dave's, we'd have two tokens: Dave, and 's

    A token is a word or single punctuation character. It is modeled as a Label."""

    cursor_colours: List[str] = ["purple","gold"]
    cursor_index: int = 0
    @classmethod
    def _cursor_colour(cls) -> str:
        Tok.cursor_index = (Tok.cursor_index + 1) % len(Tok.cursor_colours)
        return Tok.cursor_colours[Tok.cursor_index]

    def __init__(self, sentence: TokenContainer, word: str, font=None, append_to_sentence = True):
        self._word = word
        if font is None:
            font = tkinter.font.Font(name="TkDefaultFont", exists=True)
        self._font = font
        frame: tk.Frame = sentence.parent_frame()
        super().__init__(sentence.graph)
        self._canvas = tk.Canvas(frame,
                                 borderwidth=0,
                                 bd=0,
                                 highlightthickness=0,
                                 relief="flat")
        width = font.measure(word)
        width = max(width, 2) # for carriage return etc, need space to display the cursor
        height = font.metrics()['linespace']
        self._cursor_pos = Position(-5, 0)
        self._cursor_height: int = height
        self._cursor_job_id: str | None = None
        self._cursor_word_index: int = 0
        self._cursor_id = self._canvas.create_line(
            self._cursor_pos.x,
            self._cursor_pos.y,
            self._cursor_pos.x,
            self._cursor_pos.y + self._cursor_height,
            fill="white",
            width=2)
        self._highlight_id: int | None = None
        self._start_select = 0
        self._end_select = 0
        self._text_id = self._canvas.create_text(0, 0,
                         text=word,
                         fill="black",
                         font=font,
                         anchor="nw")
        self._canvas.config(width=width, height=height)
        self._canvas.pack()
        self._sentence: TokenContainer = sentence
        self._editor: EzEditor | None = None
        if append_to_sentence:
            sentence.add_child_entity(self)

    @override
    def zap(self) -> None:
        self._cursor_pos.x = -1
        self._canvas.destroy()
        super().zap()
        self.get_root_container().set_layout_needed()

    def change_word(self, new_word: str):
        self._word = new_word
        self.resize()
        self._canvas.itemconfig(self._text_id, text=new_word)
        self.mark_dirty()

    def widget_inside(self, widget: tk.Misc) -> Entity | None:
        if self._canvas == widget:
            return self
        return None

    @property
    def font(self) -> tkinter.font.Font:
        return self._font

    @property
    def cursor_pos(self) -> Position:
        return self._cursor_pos

    @property
    def cursor_word_index(self) -> int:
        return self._cursor_word_index

    @property
    @override
    def editor(self) -> EzEditor:
        if self._editor is not None:
            return self._editor
        chapter_editor = self.get_root_editor()
        self._editor = chapter_editor.get_token_editor()
        return self._editor

    @property
    @override
    def canvas(self) -> tk.Canvas:
        return self._canvas

    def select(self, start_word_index: int = 0, end_word_index: int = -1) -> None:
        self.deselect()
        (start_word_index, start_x) = self.get_x_pos_of_word_index(start_word_index)
        (end_word_index, end_x) = self.get_x_pos_of_word_index(end_word_index)
        self._highlight_id = self._canvas.create_rectangle(
            start_x,
            0,
            end_x,
            self._cursor_height,
            fill="turquoise", outline=""
        )
        self._canvas.tag_lower(self._highlight_id, self._cursor_id)
        self._start_select = start_word_index
        self._end_select = end_word_index

    def deselect(self) -> bool:
        if self._highlight_id is None:
            return False
        self._canvas.delete(self._highlight_id)
        self._highlight_id = None
        return True

    def get_selected(self) -> List["Tok"]:
        if self._highlight_id is not None:
            return [self]
        return []

    def get_x_pos_of_word_index(self, word_index) -> Tuple[int, int]:
        max_len = len(self._word)
        i = max_len if word_index == -1 else min(max_len, word_index)
        x = 0 if i == 0 else self._font.measure(self._word[0:i])
        return (i, x)

    def remove_cursor_everywhere_except_this(self) -> None:
        self.get_root_container().remove_cursor_except(self)

    def place_cursor_at_word_index(self, word_index: int):
        (i, x) = self.get_x_pos_of_word_index(word_index)
        self.place_cursor_at_word_index_and_x_position(i, x)

    def place_cursor_at_word_index_and_x_position(self, word_index: int, x: int):
        self._cursor_word_index = word_index
        self.place_cursor(Position(x + 1 if word_index == 0 else x, 0))
        self.remove_cursor_everywhere_except_this()

    def set_cursor_word_index(self, word_index: int):
        self._cursor_word_index = word_index

    def calculate_cursor_x(self, event_x: int) -> RelativeCursor:
        closest_x: int = 0
        closest_distance: int | None = None
        word_index: int = 0
        for i in range(len(self._word) + 1):
            x_after_substring = 0 if i == 0 else self._font.measure(self._word[0:i])
            distance = abs(event_x - x_after_substring)
            if closest_distance is None or distance < closest_distance:
                closest_x = x_after_substring
                word_index = i
            else:
                break
            closest_distance = distance
        if word_index == len(self._word):
            next_entity = self.next_peer()
            if next_entity is None:
                closest_x -= 2
            else:
                if not isinstance(next_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
                next_tok: Tok = next_entity
                rel = RelativeCursor(0, 0, next_tok)
                return rel
        rel = RelativeCursor(closest_x, word_index, self)
        return rel

    def place_cursor_x(self, event_x: int) -> None:
        rel = self.calculate_cursor_x(event_x)
        rel.token.place_cursor_at_word_index_and_x_position(rel.word_index, rel.x)

    def move_left(self) -> Optional["Tok"]:
        if self._cursor_word_index == 0:
            prev_entity = self.previous_peer()
            if prev_entity is None:
                return None
            if not isinstance(prev_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            prev_tok: Tok = prev_entity
            prev_tok.set_cursor_word_index(len(prev_tok.word))
            return prev_tok.move_left()
        x: int = 0 if self._cursor_word_index == 1 else self._font.measure(self._word[0:self._cursor_word_index - 1])
        self.place_cursor_at_word_index_and_x_position(self._cursor_word_index - 1, x)
        return self

    def move_right(self) -> Optional["Tok"]:
        if self._cursor_word_index == len(self._word) - 1:
            next_entity = self.next_peer()
            if next_entity is None:
                return None
            if not isinstance(next_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            next_tok: Tok = next_entity
            return next_tok.place_cursor_at_word_index_and_x_position(0, 0)
        x = self._font.measure(self._word[0:self._cursor_word_index + 1])
        if self._cursor_word_index == len(self._word):
            x -= 2
        self.place_cursor_at_word_index_and_x_position(self._cursor_word_index + 1, x)
        return self

    def move_up(self) -> Optional["Tok"]:
        abs_cursor_x = self._canvas.winfo_rootx() + self._cursor_pos.x
        abs_cursor_y = self._canvas.winfo_rooty() + self._cursor_pos.y
        closest: Tok | None = None
        closest_distance: float | None = None
        ent = self.previous_peer()
        while ent is not None:
            if not isinstance(ent, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            tok: Tok = ent
            x = tok.canvas.winfo_rootx() + tok.canvas.winfo_width() / 2
            y = tok.canvas.winfo_rooty() + tok.canvas.winfo_height()
            if y <= abs_cursor_y:
                distance = abs(x - abs_cursor_x)
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest = tok
                else:
                    break
            ent = ent.previous_peer()
        if closest is None:
            return None
        closest.place_cursor_x(abs_cursor_x - closest.canvas.winfo_rootx())
        return closest

    def move_down(self) -> Optional["Tok"]:
        abs_cursor_x = self._canvas.winfo_rootx() + self._cursor_pos.x
        abs_cursor_y = self._canvas.winfo_rooty() + self._cursor_pos.y + self._cursor_height
        closest: Tok | None = None
        closest_distance: float | None = None
        ent = self.next_peer()
        while ent is not None:
            if not isinstance(ent, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            tok: Tok = ent
            x = tok.canvas.winfo_rootx() + tok.canvas.winfo_width() / 2
            y = tok.canvas.winfo_rooty()
            if y >= abs_cursor_y:
                distance = abs(x - abs_cursor_x)
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest = tok
                else:
                    break
            ent = ent.next_peer()
        if closest is None:
            return None
        closest.place_cursor_x(abs_cursor_x - closest.canvas.winfo_rootx())
        return closest

    def resize(self) -> None:
        # for carriage return etc, need space to display the cursor, hence at least 2:
        width = max(self._font.measure(self._word), 2)
        height = self._font.metrics()['linespace']
        self._canvas.config(width=width, height=height) # probably unnecessary, but no harm done
        #self._canvas.pack(padx=0, pady=0)

    def layout(self, pos: Position, frame_width: int) -> int:
        # for carriage return etc, need space to display the cursor, hence at least 2:
        width = max(self._font.measure(self._word), 2)
        height = self._font.metrics()['linespace']
        self._canvas.config(width=width, height=height) # probably unnecessary, but no harm done
        self._canvas.pack(padx=0, pady=0)
        if pos.x + width > frame_width:
            pos.x = 0
            pos.y += height
        self._canvas.place(x=pos.x, y=pos.y, width=width, height=height)
        pos.x += width
        return pos.y + height

    @override
    def remove_cursor(self) -> None:
        if self._cursor_pos.x < 0:
            return
        self._canvas.move(self._cursor_id, -5 - self._cursor_pos.x, 0)
        self._cursor_pos.x = -5

    @override
    def place_cursor(self, pos: Position) -> None:
        self._canvas.focus_set()
        self._canvas.move(
            self._cursor_id,
            pos.x - self._cursor_pos.x,
            pos.y - self._cursor_pos.y
        )
        self._cursor_pos = pos
        root = self._canvas.winfo_toplevel()
        if self._cursor_job_id is not None:
            root.after_cancel(self._cursor_job_id)
            self._cursor_job_id = None
        self._cursor_job_id = root.after(150, self.cycle_cursor_colour)

    def cycle_cursor_colour(self) -> None:
        self._cursor_job_id = None
        if self._cursor_pos.x < 0:
            return
        self._canvas.itemconfig(self._cursor_id, fill=Tok._cursor_colour())
        self._cursor_job_id = self._canvas.winfo_toplevel().after(370, self.cycle_cursor_colour)

    @override
    def remove_child_entity(self, child: Entity) -> bool:
        return False # at the moment a Tok has no children

    @property
    @override
    def parent(self) -> Entity:
        return self._sentence

    @property
    @override
    def child_entities(self) -> List[Entity]:
        return []

    @override
    def is_container(self) -> bool:
        return False

    @override
    def add_child_entity(self, child: Entity) -> None:
        return

    @property
    def word(self) -> str:
        return self._word

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
    def selection_start(self) -> int:
        return self._start_select

    @property
    def selection_end(self) -> int:
        return self._end_select
