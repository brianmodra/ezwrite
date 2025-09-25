import tkinter as tk
from argparse import ArgumentTypeError
from typing import List, override

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.graph.ezentity import Entity
from ezwrite.graph.ezproperty import EzProperty
from ezwrite.ui.paragraph import Paragraph, ParagraphContainer
from ezwrite.ui.tok import AbstractToken
from ezwrite.utils.lock import Lock


class Chapter(ParagraphContainer, tk.Canvas):
    """The entire canvas of the editor is (at one point in time) a chapter of the book.
    It contains the paragraphs, and the canvas is scrollable."""
    def __init__(self, frame: tk.Frame, graph: Graph):
        tk.Canvas.__init__(self, frame, bg="white", cursor="arrow")
        super().__init__(graph, URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Chapter"))
        self._lock: Lock = Lock()
        self._laying_out: bool = True
        self._frame = frame
        self.pack(side="left", fill="both", expand=True)
        self.bind("<Configure>", self.on_resize)
        self.bind_all('<KeyPress>', self._handle_key_press)
        self._laying_out = False
        self._graph = graph

    @property
    @override
    def canvas(self) -> tk.Canvas:
        return self

    @property
    def graph(self) -> Graph:
        return self._graph

    def _handle_key_press(self, event: tk.Event) -> None:
        print(f"key press {event.char}, {event.keycode}, {event.keysym}")

    @override
    def add_child_entity(self, child: Entity) -> None:
        if not isinstance(child, Paragraph):
            raise ArgumentTypeError("token_container needs to be an instance of Sentence")
        paragraph: Paragraph = child
        self._children_list.append(EzProperty.HAS_PART, paragraph)

    @override
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        for child in self.child_entities:
            if not isinstance(child, Paragraph): raise ArgumentTypeError("children need to be instances of Paragraph")
            paragraph: Paragraph = child
            paragraph.remove_cursor_except(tok)

    def on_resize(self, event: tk.Event) -> None:
        """Called when the canvas is resized."""
        print(f"Canvas resized to {event.width}x{event.height} width = {self.winfo_width()}")

        self.layout()

    def layout(self) -> None:
        with self._lock:
            if self._laying_out:
                return
            self._laying_out = True

        canvas_width: int = self.winfo_width()
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
        return self._children_list.list_of(EzProperty.HAS_PART, Paragraph)
