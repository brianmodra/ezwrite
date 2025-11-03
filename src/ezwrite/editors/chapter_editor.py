from typing import override

from ezwrite.editors.ez_editor import EzEditor
from ezwrite.editors.paragraph_editor import ParagraphEditor
from ezwrite.editors.sentence_editor import SentenceEditor
from ezwrite.editors.token_editor import TokenEditor
from ezwrite.graph.entity import Entity


class ChapterEditor(EzEditor):
    """This editor class handled key events to edit the chapter.
    In many cases this will be delegated to the paragraph (which may delegate to a Tok),
    but in some cases, e.g. deleting white space between paragraphs, it will operate
    on the paragraphs contained in the chapter, in this example, joining them."""

    def __init__(self):
        self._paragraph_editor = ParagraphEditor(self)
        self._sentence_editor = SentenceEditor(self._paragraph_editor)
        self._token_editor = TokenEditor(self._sentence_editor)

    @override
    def get_token_editor(self) -> EzEditor:
        return self._token_editor

    @override
    def get_sentence_editor(self) -> EzEditor:
        return self._sentence_editor

    @override
    def get_paragraph_editor(self) -> EzEditor:
        return self._paragraph_editor

    @override
    def delete_character_left(self, ent: Entity) -> bool:
        return False
