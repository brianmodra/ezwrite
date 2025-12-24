from typing import Optional

from pylint.exceptions import InvalidArgsError
from typing_extensions import override

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
            return self._delete_char_left_of_word(tok)
        if tok.cursor_word_index == 1:
            return self._delete_first_character(tok)
        if tok.cursor_word_index < len(tok.word):
            return self._delete_character_mid_word(tok)
        new_word = tok.word[:tok.cursor_word_index - 1]
        tok.change_word(new_word)
        tok.move_left()
        return True

    @override
    def delete_selected(self, ent: Entity) -> bool:
        if not isinstance(ent, Tok):
            raise InvalidArgsError("ent needs to be a Tok")
        tok: Tok = ent
        selection_start = tok.selection_start
        selection_end = tok.selection_end
        word_len = len(tok.word)
        if selection_start == 0 and selection_end >= word_len:
            tok.zap()
            return True
        if selection_start > 0:
            if selection_end <= word_len:
                new_word = tok.word[:selection_start] + tok.word[selection_end:]
            else:
                new_word = tok.word[:selection_start]
            tok.change_word(new_word)
            tok.place_cursor_at_word_index(selection_start)
            tok.deselect()
            return True
        if selection_end <= word_len:
            new_word = tok.word[selection_end:]
            tok.change_word(new_word)
            tok.place_cursor_at_word_index(0)
            tok.deselect()
            return True
        return False

    def _delete_char_left_of_word(self, tok: Tok) -> bool:
        prev_tok = self._get_prev_token(tok)
        if prev_tok is None:
            return False
        prev_tok.place_cursor_at_word_index(-1)
        return self.delete_character_left(prev_tok)

    def _delete_first_character(self, tok: Tok) -> bool:
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
                        # same paragraph
                        tok.zap()
                        tok = prev_sentence.join_tokens(prev_tok, next_tok)
                        new_word_index = len(prev_tok.word)
                        tok.place_cursor_at_word_index(new_word_index)
                        prev_tok.zap()
                        next_tok.zap()
                    elif prev_sentence.get_root_container() != next_sentence.get_root_container():
                        return False # Don't allow backspace at the start of a chapter to edit the previous chapter
                    else:
                        # different paragraphs
                        # copy all the sentences from the next paragraph to the previous,
                        # and delete the whole next paragraph
                        Tok(prev_sentence, ' ', tok.font)
                        for child in next_sentence.parent.child_entities:
                            if not isinstance(child, Sentence):
                                continue
                            nxt_sen: Sentence = child
                            prev_sentence.append_copy_tokens_from(nxt_sen)
                        next_sentence.parent.zap()
                        return True
                    if sentence not in (next_sentence, prev_sentence):
                        # Three different sentences in play here
                        # A sentence with one token (the one where the cursor was),
                        # The sentence to the right, and the sentence to the left.
                        # Join the two up but remove the middle one
                        prev_sentence.append_copy_tokens_from(sentence)
                        sentence.zap()
                    prev_sentence.append_copy_tokens_from(next_sentence)
                    next_sentence.zap()
                    return True
                tok.zap()
                tok = sentence.join_tokens(prev_tok, next_tok)
                new_word_index = len(prev_tok.word)
                tok.place_cursor_at_word_index(new_word_index)
                prev_tok.zap()
                next_tok.zap()
                return True
            tok.zap()
            return True
        new_word = tok.word[1:]
        tok.change_word(new_word)
        tok.move_left()
        return True

    def _delete_character_mid_word(self, tok: Tok) -> bool:
        new_word = tok.word[:tok.cursor_word_index - 1] + tok.word[tok.cursor_word_index:]
        tok.change_word(new_word)
        tok.move_left()
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
        next_peer = tok.next_peer()
        if next_peer is None:
            return None
        if not isinstance(next_peer, Tok):
            raise TypeError("next peer needs to be a Tok")
        next_tok: Tok = next_peer
        return next_tok
