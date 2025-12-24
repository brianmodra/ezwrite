from abc import ABC, abstractmethod

from ezwrite.graph.entity import Entity


class EzEditor(ABC):
    """interface for all editors"""
    @abstractmethod
    def delete_character_left(self, ent: Entity) -> bool:
        pass

    @abstractmethod
    def get_token_editor(self) -> "EzEditor":
        pass

    @abstractmethod
    def get_sentence_editor(self) -> "EzEditor":
        pass

    @abstractmethod
    def get_paragraph_editor(self) -> "EzEditor":
        pass

    def delete_selected(self, ent: Entity) -> bool: # pylint: disable=unused-argument
        return False
