from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from rdflib.resource import Resource


@dataclass
class TraversalResult:
    """This class is just a tidier form than a tuple, for handling results of a traversal"""
    count: int
    ent_first: "Entity | None"
    ent_last: "Entity | None"


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

    @abstractmethod
    def is_container(self) -> bool:
        pass

    @property
    @abstractmethod
    def x(self) -> int:
        pass

    @property
    @abstractmethod
    def y(self) -> int:
        pass

    @property
    @abstractmethod
    def root_x(self) -> int:
        pass

    @property
    @abstractmethod
    def root_y(self) -> int:
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        pass

    def inside(self, root_x, root_y) -> bool:
        xmin = self.root_x
        ymin = self.root_y
        xmax = self.root_x + self.width
        ymax = self.root_y + self.height
        return xmin <= root_x < xmax and ymin <= root_y < ymax
