import tkinter as tk
import tkinter.font
from abc import ABC, abstractmethod
from argparse import ArgumentTypeError
from typing import List, override

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.graph.ezentity import Entity, EzEntity
from ezwrite.ui.position import Position


class AbstractToken(EzEntity, ABC):
    """This provides an interface to manipulate a token, without specifying
    the actual implemetation of the token"""
    def __init__(self, graph: Graph):
        super().__init__(graph, URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Token"))
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

class EzwriteContainer(EzEntity, ABC):
    """A generic container interface for all objects in the UI that contain others,
    for example, sentence, paragraph, and chapter."""
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)

    @abstractmethod
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        pass


class TokenContainer(EzwriteContainer, ABC):
    """This is more specifically an abstractrion of a sentence"""
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)

    @abstractmethod
    def layout(self, pos: Position, frame_width: int) -> int:
        pass


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

    def __init__(self, sentence: TokenContainer, word: str, font=None):
        self._word = word
        if font is None:
            font = tkinter.font.Font(name="TkDefaultFont", exists=True)
        self._font = font
        if sentence.parent is None: raise ArgumentTypeError("The sentence must not be None")
        frame: tk.Frame = sentence.parent.frame
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
        self._text_id = self._canvas.create_text(0, 0,
                         text=word,
                         fill="black",
                         font=font,
                         anchor="nw")
        self._canvas.config(width=width, height=height)
        self._canvas.pack()
        self._sentence: TokenContainer = sentence
        self._canvas.bind('<Button-1>', self._handle_mouse_button_1)
        self._canvas.bind('<Left>', self.move_left)
        self._canvas.bind('<Right>', self.move_right)
        self._canvas.bind('<Up>', self.move_up)
        self._canvas.bind('<Down>', self.move_down)
        sentence.add_child_entity(self)

    @property
    @override
    def canvas(self) -> tk.Canvas:
        return self._canvas

    def _handle_mouse_button_1(self, event: tk.Event) -> None:
        self.place_cursor_x(event.x)

    def remove_cursor_everywhere_except_this(self) -> None:
        parent: EzwriteContainer | None = None
        entity: Entity | None = self._sentence
        while entity is not None:
            parent_ent = entity.parent
            if parent_ent is None or not isinstance(parent_ent, EzwriteContainer):
                break
            parent = parent_ent
            entity = parent
        if parent is not None:
            parent.remove_cursor_except(self)

    def place_cursor_at_word_index_and_x_position(self, word_index: int, x: int):
        self._cursor_word_index = word_index
        self.place_cursor(Position(x + 1 if word_index == 0 else x, 0))
        self.remove_cursor_everywhere_except_this()

    def set_cursor_word_index(self, word_index: int):
        self._cursor_word_index = word_index

    def place_cursor_x(self, event_x: int) -> None:
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
                next_tok.place_cursor_at_word_index_and_x_position(0, 0)
                return
        self.place_cursor_at_word_index_and_x_position(word_index, closest_x)

    def move_left(self, event: tk.Event) -> None:
        if self._cursor_word_index == 0:
            prev_entity = self.previous_peer()
            if prev_entity is None:
                return
            if not isinstance(prev_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            prev_tok: Tok = prev_entity
            prev_tok.set_cursor_word_index(len(prev_tok.word))
            prev_tok.move_left(event)
            return
        x: int = 0 if self._cursor_word_index == 1 else self._font.measure(self._word[0:self._cursor_word_index - 1])
        self.place_cursor_at_word_index_and_x_position(self._cursor_word_index - 1, x)

    def move_right(self, _event: tk.Event) -> None:
        if self._cursor_word_index == len(self._word) - 1:
            next_entity = self.next_peer()
            if next_entity is None:
                return
            if not isinstance(next_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            next_tok: Tok = next_entity
            next_tok.place_cursor_at_word_index_and_x_position(0, 0)
            return
        x = self._font.measure(self._word[0:self._cursor_word_index + 1])
        if self._cursor_word_index == len(self._word):
            x -= 2
        self.place_cursor_at_word_index_and_x_position(self._cursor_word_index + 1, x)

    def move_up(self, _event: tk.Event) -> None:
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
            return
        closest.place_cursor_x(abs_cursor_x - closest.canvas.winfo_rootx())

    def move_down(self, _event: tk.Event) -> None:
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
            return
        closest.place_cursor_x(abs_cursor_x - closest.canvas.winfo_rootx())

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

    @property
    def height(self) -> int:
        return self._canvas.winfo_height()

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

    @property
    @override
    def parent(self) -> Entity:
        return self._sentence

    @property
    @override
    def child_entities(self) -> List[Entity]:
        return []

    @override
    def add_child_entity(self, child: Entity) -> None:
        return

    @property
    def word(self) -> str:
        return self._word
