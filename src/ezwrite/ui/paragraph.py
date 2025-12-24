import tkinter as tk
from abc import ABC, abstractmethod
from argparse import ArgumentTypeError
from typing import List, override

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.editors.ez_editor import EzEditor
from ezwrite.graph.ezentity import Entity
from ezwrite.graph.ezproperty import EzProperty
from ezwrite.ui.position import Position
from ezwrite.ui.sentence import Sentence, SentenceContainer
from ezwrite.ui.tok import AbstractToken, RootContainer, Tok


class ParagraphContainer(RootContainer, ABC):
    """Just needed to avoid circular dependencies"""
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)

    @property
    @abstractmethod
    def graph(self):
        pass

    @property
    @abstractmethod
    def canvas(self) -> tk.Canvas:
        pass


class Paragraph(SentenceContainer):
    """A paragraph is a Frame in the Canvas (Chapter). A Paragraph contains sentences. """
    def __init__(self, chapter: ParagraphContainer, graph: Graph, first_line_indent: int = 0):
        super().__init__(
            graph,
            URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Paragraph")
        )
        self._graph = graph
        self._chapter = chapter
        self._frame = tk.Frame(chapter.canvas,
                          bg="light grey",
                          bd=0,
                          height=80,
                          padx=0,
                          pady=0,
                          borderwidth=0,
                          relief="flat",
                          cursor="ibeam")
        self._frame.bind('<Button-1>', self._handle_mouse_button_1)
        self._frame_id = self._chapter.canvas.create_window(0, 0, anchor="nw", window=self._frame)
        self._first_line_indent = first_line_indent
        self._editor: EzEditor | None = None
        chapter.add_child_entity(self)

    @override
    def zap(self) -> None:
        super().zap()
        self._frame.destroy()

    @override
    def is_container(self) -> bool:
        return True

    @property
    @override
    def editor(self) -> EzEditor:
        if self._editor is not None:
            return self._editor
        chapter_editor = self.get_root_editor()
        self._editor = chapter_editor.get_paragraph_editor()
        return self._editor

    def widget_inside(self, widget: tk.Misc) -> Entity | None:
        for child in self.child_entities:
            if not isinstance(child, Sentence):
                continue
            sentence: Sentence = child
            entity: Entity | None = sentence.widget_inside(widget)
            if entity is not None:
                return entity
        if self._frame == widget:
            return self
        return None

    def get_closest_token(self, x: int, y: int) -> Entity | None:
        # first try to find if the coordinate is within the contained tokens
        for sen in self.child_entities:
            if not isinstance(sen, Sentence):
                continue
            sentence: Sentence = sen
            for child in sentence.child_entities:
                if not isinstance(child, Tok):
                    continue
                tok: Tok = child
                if tok.inside(x, y):
                    return tok
        # not within, then find the closest token at the start or end of the paragraph.
        ent: Entity | None = self.first_child()
        if ent is not None:
            ent = ent.first_child()
            if ent is not None and isinstance(ent, Tok):
                tok = ent
                if y < tok.root_y:
                    return tok
                if y < tok.root_y + tok.height and x < tok.root_x:
                    return tok
        ent = self.last_child()
        if ent is not None:
            ent = ent.last_child()
            if ent is not None and isinstance(ent, Tok):
                tok = ent
                if y < tok.root_y:
                    return None
                if x >= tok.root_x + tok.width or y >= tok.root_y + tok.height:
                    return tok
        return None

    @property
    @override
    def frame(self) -> tk.Frame:
        return self._frame

    @property
    def graph(self) -> Graph:
        return self._graph

    def _handle_mouse_button_1(self, event: tk.Event) -> None:
        print(f"button 1 {event.x},{event.y}")

    @override
    def layout(self, frame_y_offset: int, canvas_width: int) -> int:
        pos: Position = Position(self._first_line_indent, 0)
        frame_height: int = 0
        for sentence in self.child_entities:
            if not isinstance(sentence, Sentence): raise ArgumentTypeError("sentence must be an instance of Sentence")
            container: Sentence = sentence
            frame_height = max(frame_height, container.layout(pos, canvas_width))
        self._frame.place(x=0, y=frame_y_offset, height=frame_height, width=canvas_width)
        return frame_height

    @property
    def frame_id(self) -> int:
        return self._frame_id

    def add_child_entity(self, child: Entity) -> None:
        if not isinstance(child, Sentence): raise ArgumentTypeError("token_container must be an instance of Sentence")
        sentence: Sentence = child
        self._property_list.append(EzProperty.HAS_PART, sentence)

    @override
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        for child in self.child_entities:
            if not isinstance(child, Sentence): raise ArgumentTypeError("child must be an instance of Sentence")
            sentence: Sentence = child
            sentence.remove_cursor_except(tok)

    @property
    def max_tok_height(self) -> int:
        height: int = 0
        for child in self.child_entities:
            if not isinstance(child, Sentence): raise ArgumentTypeError("child must be an instance of Sentence")
            sentence: Sentence = child
            height = max(height, sentence.max_tok_height)
        return height

    @property
    @override
    def parent(self) -> Entity | None:
        return self._chapter

    @property
    @override
    def child_entities(self) -> List[Entity]:
        return self._property_list.entities_of(EzProperty.HAS_PART, Sentence)

    @override
    def deselect_all(self) -> None:
        for child in self.child_entities:
            if not isinstance(child, Sentence):
                continue
            sentence: Sentence = child
            sentence.deselect_all()

    @override
    @property
    def x(self) -> int:
        return self._frame.winfo_x()

    @override
    @property
    def y(self) -> int:
        return self._frame.winfo_y()

    @override
    @property
    def root_x(self) -> int:
        return self._frame.winfo_rootx()

    @override
    @property
    def root_y(self) -> int:
        return self._frame.winfo_rooty()

    @override
    @property
    def width(self) -> int:
        return self._frame.winfo_width()

    @override
    @property
    def height(self) -> int:
        return self._frame.winfo_height()
