from abc import ABC, abstractmethod
from typing import List, Optional

from rdflib.resource import Resource


class Entity(Resource, ABC):
    """All entities in the graph inherit from this"""
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
        """self implicitly has property EzProperty.IS_PART_OF"""

    @property
    @abstractmethod
    def child_entities(self) -> List["Entity"]:
        pass

    @property
    @abstractmethod
    def has_children(self) -> bool:
        pass

    @abstractmethod
    def add_child_entity(self, child: "Entity") -> None:
        pass

    @abstractmethod
    def remove_child_entity(self, child: "Entity") -> bool:
        pass

    @abstractmethod
    def mark_dirty(self) -> None:
        pass

    @property
    @abstractmethod
    def dirty(self) -> bool:
        pass

    @abstractmethod
    def zap(self) -> None:
        pass

    @abstractmethod
    def cleanup_empty_containers(self) -> int:
        pass

    def can_have_children(self) -> bool:
        return True
