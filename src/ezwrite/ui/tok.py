import tkinter as tk
import tkinter.font
from typing import List, override
from abc import ABC, abstractmethod
from ezwrite.ui.position import Position
from ezwrite.graph.ezentity import Entity, EzEntity
from rdflib.term import URIRef
from argparse import ArgumentTypeError

"""A Tok is a token (could not use the name 'Token' - already in use)
It is the smallest entity in the knowledge graph to describe the text.
It could be a word, punctuation, whitespace, or the end of a word, e.g.
In the word: Dave's, we'd have two tokens: Dave, and 's"""

class AbstractToken(EzEntity, tk.Canvas, ABC):
    @abstractmethod
    def remove_cursor(self) -> None:
        pass

    @abstractmethod
    def place_cursor(self, pos: Position) -> None:
        pass

class EzwriteContainer(EzEntity, ABC):
    @abstractmethod
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        pass

class TokenContainer(EzwriteContainer, ABC):
    """needed to avoid circular dependencies"""
    @abstractmethod
    def layout(self, pos: Position, frame_width: int) -> int:
        pass

class Tok(AbstractToken):
    """A token is a word or single punctuation character. It is modeled as a Label."""
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
        if sentence.parent is None: raise ArgumentTypeError("The sentence (of a Tok) must not be None")
        if not isinstance(sentence.parent, tk.Frame): raise ArgumentTypeError("The sentence (of a Tok) must inherit from Frame")
        frame: tk.Frame = sentence.parent
        tk.Canvas.__init__(self, frame,
                         borderwidth=0,
                         bd=0,
                         highlightthickness=0,
                         relief="flat")
        EzEntity.__init__(self, sentence.graph, URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Token"))
        width = font.measure(word)
        if width < 2:
            width = 2 # for carriage return etc, need space to display the cursor
        height = font.metrics()['linespace']
        self._cursor_pos = Position(-5, 0)
        self._cursor_height: int = height
        self._cursor_job_id: str | None = None
        self._cursor_word_index: int = 0
        self._cursor_id = self.create_line(
            self._cursor_pos.x,
            self._cursor_pos.y,
            self._cursor_pos.x,
            self._cursor_pos.y + self._cursor_height,
            fill="white",
            width=2)
        self._text_id = self.create_text(0, 0,
                         text=word,
                         fill="black",
                         font=font,
                         anchor="nw")
        self.config(width=width, height=height)
        self.pack()
        self._sentence: TokenContainer = sentence
        self.bind('<Button-1>', self._handle_mouse_button_1)
        self.bind('<Left>', self._move_left)
        self.bind('<Right>', self._move_right)
        self.bind('<Up>', self._move_up)
        self.bind('<Down>', self._move_down)
        sentence.add_child_entity(self)

    def _handle_mouse_button_1(self, event: tk.Event) -> None:
        self._place_cursor_x(event.x)

    def remove_cursor_everywhere_except_this(self) -> None:
        parent: EzwriteContainer | None = None
        entity: Entity | None = self._sentence
        while entity is not None:
            parent_ent = entity.parent
            if parent_ent is None or not isinstance(parent_ent, EzwriteContainer):
                return
            parent = parent_ent
            entity = parent
        if parent is not None:
            parent.remove_cursor_except(self)

    def _place_cursor_x(self, event_x: int) -> None:
        closest_x: int = 0
        closest_distance: int | None = None
        self._cursor_word_index = 0
        for i in range(len(self._word) + 1):
            x_after_substring = 0 if i == 0 else self._font.measure(self._word[0:i])
            distance = abs(event_x - x_after_substring)
            if closest_distance is None or distance < closest_distance:
                closest_x = x_after_substring
                self._cursor_word_index = i
            else:
                break
            closest_distance = distance
        if self._cursor_word_index == len(self._word):
            next_entity = self.next_peer()
            if next_entity is None:
                closest_x -= 2
            else:
                if not isinstance(next_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
                next_tok: Tok = next_entity
                next_tok._cursor_word_index = 0
                next_tok.place_cursor(Position(1, 0))
                next_tok.remove_cursor_everywhere_except_this()
                return
        if self._cursor_word_index == 0:
            self.place_cursor(Position(closest_x + 1, 0))
        else:
            self.place_cursor(Position(closest_x, 0))
        self.remove_cursor_everywhere_except_this()

    def _move_left(self, event: tk.Event) -> None:
        if self._cursor_word_index == 0:
            prev_entity = self.previous_peer()
            if prev_entity is None:
                return
            if not isinstance(prev_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            prev_tok: Tok = prev_entity
            prev_tok._cursor_word_index = len(prev_tok._word)
            prev_tok._move_left(event)
            return
        self._cursor_word_index -= 1
        if self._cursor_word_index == 0:
            self.place_cursor(Position(1, 0))
        else:
            x = self._font.measure(self._word[0:self._cursor_word_index])
            self.place_cursor(Position(x, 0))
        self.remove_cursor_everywhere_except_this()

    def _move_right(self, event: tk.Event) -> None:
        if self._cursor_word_index == len(self._word) - 1:
            next_entity = self.next_peer()
            if next_entity is None:
                return
            if not isinstance(next_entity, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            next_tok: Tok = next_entity
            next_tok._cursor_word_index = 0
            next_tok.place_cursor(Position(1, 0))
            next_tok.remove_cursor_everywhere_except_this()
            return
        self._cursor_word_index += 1
        x = self._font.measure(self._word[0:self._cursor_word_index])
        if self._cursor_word_index == len(self._word):
            x -= 2
        self.place_cursor(Position(x, 0))
        self.remove_cursor_everywhere_except_this()

    def _move_up(self, event: tk.Event) -> None:
        abs_cursor_x = self.winfo_rootx() + self._cursor_pos.x
        abs_cursor_y = self.winfo_rooty() + self._cursor_pos.y
        closest: Tok | None = None
        closest_distance: float | None = None
        ent = self.previous_peer()
        while ent is not None:
            if not isinstance(ent, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            tok: Tok = ent
            x = tok.winfo_rootx() + tok.winfo_width() / 2
            y = tok.winfo_rooty() + tok.winfo_height()
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
        closest._place_cursor_x(abs_cursor_x - closest.winfo_rootx())

    def _move_down(self, event: tk.Event) -> None:
        abs_cursor_x = self.winfo_rootx() + self._cursor_pos.x
        abs_cursor_y = self.winfo_rooty() + self._cursor_pos.y + self._cursor_height
        closest: Tok | None = None
        closest_distance: float | None = None
        ent = self.next_peer()
        while ent is not None:
            if not isinstance(ent, Tok): raise ArgumentTypeError("a peer of a Tok must be a Tok")
            tok: Tok = ent
            x = tok.winfo_rootx() + tok.winfo_width() / 2
            y = tok.winfo_rooty()
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
        closest._place_cursor_x(abs_cursor_x - closest.winfo_rootx())

    def layout(self, pos: Position, frame_width: int) -> int:
        width = self._font.measure(self._word)
        if width < 2:
            width = 2 # for carriage return etc, need space to display the cursor
        height = self._font.metrics()['linespace']
        self.config(width=width, height=height) # probably unnecessary, but no harm done
        self.pack(padx=0, pady=0)
        if pos.x + width > frame_width:
            pos.x = 0
            pos.y += height
        self.place(x=pos.x, y=pos.y, width=width, height=height)
        pos.x += width
        return pos.y + height

    @property
    def height(self) -> int:
        return self.winfo_height()

    @override
    def remove_cursor(self) -> None:
        if self._cursor_pos.x < 0:
            return
        self.move(self._cursor_id, -5 - self._cursor_pos.x, 0)
        self._cursor_pos.x = -5

    @override
    def place_cursor(self, pos: Position) -> None:
        self.focus_set()
        self.move(
            self._cursor_id,
            pos.x - self._cursor_pos.x,
            pos.y - self._cursor_pos.y
        )
        self._cursor_pos = pos
        root = self.winfo_toplevel()
        if self._cursor_job_id is not None:
            root.after_cancel(self._cursor_job_id)
            self._cursor_job_id = None
        self._cursor_job_id = root.after(150, self.cycle_cursor_colour)

    def cycle_cursor_colour(self) -> None:
        self._cursor_job_id = None
        if self._cursor_pos.x < 0:
            return
        self.itemconfig(self._cursor_id, fill=Tok._cursor_colour())
        self._cursor_job_id = self.winfo_toplevel().after(370, self.cycle_cursor_colour)

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
