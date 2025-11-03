from typing_extensions import override

from ezwrite.editors.ez_editor import EzEditor
from ezwrite.graph.entity import Entity


class SentenceEditor(EzEditor):
    """Allows editing of sentences"""
    def __init__(self, parent: EzEditor):
        self._parent = parent

    @override
    def get_token_editor(self) -> EzEditor:
        return self._parent.get_token_editor()

    @override
    def get_sentence_editor(self) -> EzEditor:
        return self

    @override
    def get_paragraph_editor(self) -> EzEditor:
        return self._parent.get_paragraph_editor()

    @override
    def delete_character_left(self, ent: Entity) -> bool:
        return False
