from pylint.exceptions import InvalidArgsError
from typing_extensions import override
from typing import Optional

from ezwrite.editors.ez_editor import EzEditor
from ezwrite.graph.entity import Entity
from ezwrite.ui.sentence import Sentence
from ezwrite.ui.tok import Tok


class TokenEditor(EzEditor):
    """Allows editing of tokens"""
    def __init__(self, parent: EzEditor):
        self._parent = parent

    @override
    def get_token_editor(self) -> EzEditor:
        return self

    @override
    def get_sentence_editor(self) -> EzEditor:
        return self._parent.get_sentence_editor()

    @override
    def get_paragraph_editor(self) -> EzEditor:
        return self._parent.get_paragraph_editor()

    @override
    def delete_character_left(self, ent: Entity) -> bool:
        if not isinstance(ent, Tok):
            raise InvalidArgsError("ent needs to be a Tok")
        tok: Tok = ent
        if tok.cursor_word_index == 0:
            prev_tok = self._get_prev_token(tok)
            if prev_tok is None:
                return False
            prev_tok.place_cursor_at_word_index(-1)
            return self.delete_character_left(prev_tok)
        if tok.cursor_word_index == 1:
            if len(tok.word) == 1:
                parent = tok.parent
                if not isinstance(parent, Sentence):
                    raise ValueError("parent needs to be a Sentence")
                sentence: Sentence = parent
                prev_tok = self._get_prev_token(tok)
                next_tok = self._get_next_token(tok)
                if prev_tok is not None and next_tok is not None:
                    if prev_tok.parent != parent or next_tok.parent != parent:
                        if not isinstance(prev_tok.parent, Sentence):
                            raise ValueError("previous parent must be a sentence")
                        if not isinstance(next_tok.parent, Sentence):
                            raise ValueError("next parent must be a sentence")
                        prev_sentence: Sentence = prev_tok.parent
                        next_sentence: Sentence = next_tok.parent
                        if prev_sentence.parent == next_sentence.parent:
                            tok.zap()
                            tok = prev_sentence.join_tokens(prev_tok, next_tok)
                            new_word_index = len(prev_tok.word)
                            tok.place_cursor_at_word_index(new_word_index)
                            prev_tok.zap()
                            next_tok.zap()
                        else:
                            Tok(prev_sentence, ' ', tok.font)
                        if next_sentence != sentence and sentence != prev_sentence:
                            prev_sentence.append_copy_tokens_from(sentence)
                            sentence.zap()
                        prev_sentence.append_copy_tokens_from(next_sentence)
                        next_sentence.zap()
                        prev_sentence.get_root_container().layout()
                        return True
                    tok.zap()
                    tok = sentence.join_tokens(prev_tok, next_tok)
                    new_word_index = len(prev_tok.word)
                    tok.place_cursor_at_word_index(new_word_index)
                    prev_tok.zap()
                    next_tok.zap()
                    sentence.get_root_container().layout()
                    return True
                tok.zap()
                return True
            new_word = tok.word[1:]
            tok.change_word(new_word)
            return True
        if tok.cursor_word_index < len(tok.word):
            new_word = tok.word[:tok.cursor_word_index - 1] + tok.word[tok.cursor_word_index:]
            tok.change_word(new_word)
            return True
        new_word = tok.word[:tok.cursor_word_index - 1]
        tok.change_word(new_word)
        return True

    def _get_prev_token(self, tok: Tok) -> Optional[Tok]:
        prev = tok.previous_peer()
        if prev is None:
            return None
        if not isinstance(prev, Tok):
            raise TypeError("previous peer needs to be a Tok")
        prev_tok: Tok = prev
        return prev_tok

    def _get_next_token(self, tok: Tok) -> Optional[Tok]:
        next = tok.next_peer()
        if next is None:
            return None
        if not isinstance(next, Tok):
            raise TypeError("next peer needs to be a Tok")
        next_tok: Tok = next
        return next_tok
