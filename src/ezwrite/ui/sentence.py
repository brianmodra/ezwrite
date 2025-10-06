import tkinter as tk
from abc import ABC, abstractmethod
from argparse import ArgumentTypeError
from typing import List, override

from rdflib.graph import Graph
from rdflib.term import URIRef

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
        paragraph.add_child_entity(self)

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
        return self._children_list.list_of(EzProperty.HAS_PART, Tok)

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
        self._children_list.append(EzProperty.HAS_PART, token)

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
