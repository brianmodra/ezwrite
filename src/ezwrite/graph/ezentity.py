from abc import ABC
from typing import Optional, override

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.graph.entity import Entity
from ezwrite.graph.ezproperty import EzProperty
from ezwrite.graph.property_list import PropertyList


class EzEntity(Entity, ABC):
    """All entities inherit from this partial implementation of Entity"""
    def __init__(self, graph: Graph, subject: URIRef):
        super().__init__(graph, subject)
        self._property_list = PropertyList()
        self._dirty = False

    def __eq__(self, other) -> bool:
        return self is other

    def __ne__(self, other) -> bool:
        return not self is other

    @override
    def mark_dirty(self) -> None:
        self._dirty = True
        if self.parent is not None:
            self.parent.mark_dirty()

    @property
    @override
    def dirty(self) -> bool:
        return self._dirty

    @override
    def next_peer(self) -> Optional[Entity]:
        parent = self.parent
        if parent is None:
            return None
        peer = parent.get_next_child(self)
        if peer is not None:
            return peer
        # No next peer exists in this parent
        # try the next parent's first child
        next_parent = parent.next_peer()
        while next_parent is not None:
            peer = next_parent.first_child()
            if peer is not None:
                return peer
            # next parent had no children, try the next...
            next_parent = next_parent.next_peer()
        # none found, give up
        return None

    @override
    def previous_peer(self) -> Optional[Entity]:
        parent = self.parent
        if parent is None:
            return None
        peer = parent.get_previous_child(self)
        if peer is not None:
            return peer
        # No previous peer exists in this parent,
        # try the previous parent's last child
        previous_parent = parent.previous_peer()
        while previous_parent is not None:
            peer = previous_parent.last_child()
            if peer is not None:
                return peer
            # previous parent had no children, try the previous one to that...
            previous_parent = previous_parent.previous_peer()
        # none found, give up
        return None

    @override
    def get_next_child(self, child: Entity) -> Optional[Entity]:
        children = self.child_entities
        if children is None or len(children) == 0:
            return None
        found: bool = False
        for this_child in children:
            if found:
                return this_child
            if this_child == child:
                found = True
        return None

    @override
    def get_previous_child(self, child: Entity) -> Optional[Entity]:
        children = self.child_entities
        if children is None or len(children) == 0:
            return None
        prev_child: Entity | None = None
        for this_child in children:
            if this_child == child:
                if prev_child is not None:
                    return prev_child
                break
            prev_child = this_child
        # no previous child found in this parent
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

    @override
    def zap(self) -> None:
        """Remove all linkages to this entity and remove all its children"""
        children = self.child_entities
        composites = self._property_list.all_entities_of(EzProperty.IS_PART_OF)
        for composite in composites:
            composite.remove_child_entity(self)
        if self.parent:
            self.parent.remove_child_entity(self)
        for child in children:
            child.zap()

    @override
    def remove_child_entity(self, child: Entity) -> bool:
        return self._property_list.remove(EzProperty.HAS_PART, child)

    @property
    @override
    def has_children(self) -> bool:
        return self._property_list.has_entities_of(EzProperty.HAS_PART)

    @override
    def cleanup_empty_containers(self) -> int:
        count = 0
        for child in self.child_entities:
            if not child.can_have_children():
                continue
            count += child.cleanup_empty_containers()
            if not child.has_children:
                self.zap()
        return count
