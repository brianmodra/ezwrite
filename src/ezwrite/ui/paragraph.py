import tkinter as tk
from typing import override, List
from abc import ABC, abstractmethod
from argparse import ArgumentTypeError
from ezwrite.ui.sentence import Sentence, SentenceContainer
from ezwrite.ui.tok import AbstractToken, EzwriteContainer
from ezwrite.graph.ezentity import Entity, EzEntity
from ezwrite.ui.position import Position
from ezwrite.graph.ezproperty import EzProperty
from rdflib.term import URIRef
from rdflib.graph import Graph

class ParagraphContainer(EzwriteContainer, tk.Canvas, ABC):
    """Just needed to avoid circular dependencies"""
    @property
    @abstractmethod
    def graph(self):
        pass

class Paragraph(SentenceContainer):
    """A paragraph is a Frame in the Canvas (Chapter). A Paragraph contains sentences. """
    def __init__(self, chapter: ParagraphContainer, first_line_indent: int = 0):
        tk.Frame.__init__(self, chapter,
                         bg="light grey",
                         bd=0,
                         height=80,
                         padx=0,
                         pady=0,
                         borderwidth=0,
                         relief="flat",
                         cursor="ibeam")
        EzEntity.__init__(self, self.graph, URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Paragraph"))
        self._chapter = chapter
        self._frame_id = self._chapter.create_window(0, 0, anchor="nw", window=self)
        self._first_line_indent = first_line_indent
        self.bind('<Button-1>', self._handle_mouse_button_1)
        chapter.add_child_entity(self)

    @property
    def graph(self) -> Graph:
        return self._chapter.graph

    def _handle_mouse_button_1(self, event: tk.Event) -> None:
        print(f"button 1 {event.x},{event.y}")

    @override
    def layout(self, frame_y_offset: int, canvas_width: int) -> int:
        pos: Position = Position(self._first_line_indent, 0)
        frame_height: int = 0
        for sentence in self.child_entities:
            if not isinstance(sentence, Sentence): raise ArgumentTypeError("sentence must be an instance of Sentence")
            container: Sentence = sentence
            frame_height = container.layout(pos, canvas_width)
        self.place(x=0, y=frame_y_offset, height=frame_height, width=canvas_width)
        return frame_height

    @property
    def frame_id(self) -> int:
        return self._frame_id

    def add_child_entity(self, child: Entity) -> None:
        if not isinstance(child, Sentence): raise ArgumentTypeError("token_container needs to be an instance of Sentence")
        sentence: Sentence = child
        self._children_list.append(EzProperty.HAS_PART, sentence)

    @override
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        for child in self.child_entities:
            if not isinstance(child, Sentence): raise ArgumentTypeError("child needs to be an instance of Sentence")
            sentence: Sentence = child
            sentence.remove_cursor_except(tok)

    @property
    def max_tok_height(self) -> int:
        height: int = 0
        for child in self.child_entities:
            if not isinstance(child, Sentence): raise ArgumentTypeError("child needs to be an instance of Sentence")
            sentence: Sentence = child
            tok_height: int = sentence.max_tok_height
            if tok_height > height:
                height = tok_height
        return height

    @property
    @override
    def parent(self) -> Entity | None:
        return self._chapter

    @property
    @override
    def child_entities(self) -> List[Entity]:
        return self._children_list.list_of(EzProperty.HAS_PART, Sentence)
