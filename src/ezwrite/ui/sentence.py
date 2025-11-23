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
from ezwrite.ui.tok import AbstractToken, EzwriteContainer, Tok, TokenContainer


class SentenceContainer(EzwriteContainer, ABC):
    """Just needed to avoid circular dependencies"""
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)

    @property
    @abstractmethod
    def graph(self) -> Graph:
        pass

    @abstractmethod
    def layout(self, frame_y_offset: int, canvas_width: int) -> int:
        pass

    @property
    @abstractmethod
    def frame(self) -> tk.Frame:
        pass


class Sentence(TokenContainer):
    """A sentence is not a UI element, it is just a collection of tokens."""
    def __init__(self, paragraph: SentenceContainer):
        super().__init__(
            paragraph.graph,
            URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Sentence")
        )
        self._paragraph = paragraph
        self._editor: EzEditor | None = None
        paragraph.add_child_entity(self)

    @property
    @override
    def editor(self) -> EzEditor:
        if self._editor is not None:
            return self._editor
        chapter_editor = self.get_root_editor()
        self._editor = chapter_editor.get_sentence_editor()
        return self._editor

    @override
    def is_container(self) -> bool:
        return True

    def widget_inside(self, widget: tk.Misc) -> Entity | None:
        for child in self.child_entities:
            if not isinstance(child, Tok):
                continue
            token: Tok = child
            entity: Entity | None = token.widget_inside(widget)
            if entity is not None:
                return entity
        return None

    @property
    def graph(self) -> Graph:
        return self._paragraph.graph

    @property
    @override
    def parent(self) -> Entity:
        return self._paragraph

    @property
    @override
    def child_entities(self) -> List[Entity]:
        return self._property_list.entities_of(EzProperty.HAS_PART, Tok)

    @override
    def parent_frame(self) -> tk.Frame:
        parent = self.parent
        if parent is None:
            raise ArgumentTypeError("The parent of a sentence must not be None")
        if not isinstance(parent, SentenceContainer):
            raise ArgumentTypeError("The sentence parent must be a SentenceContainer")
        sentence_container: SentenceContainer = parent
        return sentence_container.frame

    @override
    def add_child_entity(self, child: Entity) -> None:
        if not isinstance(child, Tok): raise ArgumentTypeError("label needs to be an instance of Token")
        token: Tok = child
        self._property_list.append(EzProperty.HAS_PART, token)

    @override
    def remove_cursor_except(self, tok: AbstractToken) -> None:
        for ent in self.child_entities:
            if ent != tok:
                if not isinstance(ent, Tok): raise ArgumentTypeError("children need to be instances of Token")
                token: Tok = ent
                token.remove_cursor()

    @override
    def layout(self, pos: Position, frame_width: int) -> int:
        sentence_height: int = 0
        for ent in self.child_entities:
            if not isinstance(ent, Tok): raise ArgumentTypeError("children need to be instances of Token")
            token: Tok = ent
            sentence_height = token.layout(pos, frame_width)
        return sentence_height

    @property
    def max_tok_height(self) -> int:
        height: int = 0
        for ent in self.child_entities:
            if not isinstance(ent, Tok): raise ArgumentTypeError("children need to be instances of Token")
            token: Tok = ent
            tok_height: int = token.height
            height = max(height, tok_height)
        return height

    def join_tokens(self, a: Tok, b: Tok) -> Tok:
        joined_word: str = a.word + b.word
        joined_tok = Tok(self, joined_word, a.font, False)
        self._property_list.insert_before(a, EzProperty.HAS_PART, joined_tok)
        return joined_tok

    def append_copy_tokens_from(self, other_sentence: "Sentence") -> None:
        for child in other_sentence.child_entities:
            if not isinstance(child, Tok):
                continue
            tok: Tok = child
            Tok(self, tok.word, tok.font)

    @override
    def deselect_all(self) -> None:
        for child in self.child_entities:
            if not isinstance(child, Tok):
                continue
            tok: Tok = child
            tok.deselect()

    @override
    @property
    def x(self) -> int:
        first = self.first_child()
        if first is None:
            return self.parent.x
        return first.x

    @override
    @property
    def y(self) -> int:
        first = self.first_child()
        if first is None:
            return self.parent.y
        return first.y

    @override
    @property
    def root_x(self) -> int:
        first = self.first_child()
        if first is None:
            return self.parent.root_x
        return first.root_x

    @override
    @property
    def root_y(self) -> int:
        first = self.first_child()
        if first is None:
            return self.parent.root_y
        return first.root_y

    @override
    @property
    def width(self) -> int:
        last = self.last_child()
        if last is None:
            return 0
        return last.x + last.width - self.x - 1

    @override
    @property
    def height(self) -> int:
        last = self.last_child()
        if last is None:
            return 0
        return last.y + last.height - self.y - 1
