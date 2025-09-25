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
        pass

    @property
    @abstractmethod
    def child_entities(self) -> List["Entity"]:
        pass

    @abstractmethod
    def add_child_entity(self, child: "Entity") -> None:
        pass
