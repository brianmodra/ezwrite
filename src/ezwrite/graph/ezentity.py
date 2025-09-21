from typing import Dict, List, override, Optional
from abc import ABC, abstractmethod
from rdflib.resource import Resource
from ezwrite.graph.property_list import PropertyList
from rdflib.graph import Graph
from rdflib.resource import Resource
from rdflib.term import URIRef

class Entity(Resource, ABC):
    @abstractmethod
    def next_peer(self) -> Optional["Entity"]:
        pass

    @abstractmethod
    def previous_peer(self) -> Optional["Entity"]:
        pass

    @abstractmethod
    def get_next_child(self, child: "Entity") -> Optional["Entity"]:
        pass

    @abstractmethod
    def get_previous_child(self, child: "Entity") -> Optional["Entity"]:
        pass

    @abstractmethod
    def first_child(self) -> Optional["Entity"]:
        pass

    @abstractmethod
    def last_child(self) -> Optional["Entity"]:
        pass

    @property
    @abstractmethod
    def parent(self) -> Optional["Entity"]:
        pass

    @property
    @abstractmethod
    def child_entities(self) -> List["Entity"]:
        pass

    @abstractmethod
    def add_child_entity(self, child: "Entity") -> None:
        pass

class EzEntity(Entity, ABC):
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)
        self._children_list = PropertyList()

    @override
    def next_peer(self) -> Optional[Entity]:
        parent = self.parent
        if parent is None:
            return None
        return parent.get_next_child(self)

    @override
    def previous_peer(self) -> Optional[Entity]:
        parent = self.parent
        if parent is None:
            return None
        return parent.get_previous_child(self)

    @override
    def get_next_child(self, ref_child: Entity) -> Optional[Entity]:
        children = self.child_entities
        if children is None or len(children) == 0:
            return None
        found: bool = False
        for child in children:
            if found:
                return child
            if child == ref_child:
                found = True
        if not found:
            return None
        parent = self.parent
        if parent is None:
            return None
        next_parent_peer = parent.next_peer()
        while next_parent_peer is not None:
            next_peer = next_parent_peer.first_child()
            while next_peer is not None:
                next_child = next_peer.first_child()
                if next_child is not None:
                    return next_child
                next_peer = next_peer.next_peer()
            next_parent_peer = next_parent_peer.next_peer()
        return None

    @override
    def get_previous_child(self, ref_child: Entity) -> Optional[Entity]:
        children = self.child_entities
        if children is None or len(children) == 0:
            return None
        prev_child: Entity | None = None
        for child in children:
            if child == ref_child:
                if prev_child is not None:
                    return prev_child
                parent = self.parent
                if parent is None:
                    return None
                prev_parent_peer = parent.previous_peer()
                while prev_parent_peer is not None:
                    prev_peer = prev_parent_peer.last_child()
                    while prev_peer is not None:
                        prev_child = prev_peer.last_child()
                        if prev_child is not None:
                            return prev_child
                        prev_peer = prev_peer.previous_peer()
                    prev_parent_peer = prev_parent_peer.previous_peer()
                return None
            prev_child = child
        return None

    @override
    def first_child(self) -> Optional[Entity]:
        children = self.child_entities
        if children is None or len(children) == 0:
            return None
        return children[0]

    @override
    def last_child(self) -> Optional[Entity]:
        children = self.child_entities
        if children is None or len(children) == 0:
            return None
        return children[-1]
