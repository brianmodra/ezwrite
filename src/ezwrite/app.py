import tkinter as tk
from tkinter import Frame, Scrollbar, Tk

from rdflib.graph import Graph

from ezwrite.ui.chapter import Chapter
from ezwrite.ui.paragraph import Paragraph
from ezwrite.ui.sentence import Sentence
from ezwrite.ui.tok import Tok


class App:
    """This is the ezwrite main application."""
    def __init__(self):
        self.root: Tk = tk.Tk()
        self.root.geometry("400x300")
        self._frame: Frame = tk.Frame(self.root)
        self._frame.pack(fill="both", expand=True)
        graph: Graph = Graph()
        self._chapter: Chapter = Chapter(self._frame, graph)
        scrollbar: Scrollbar = tk.Scrollbar(self._frame, orient="vertical", command=self.chapter.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self._chapter.canvas.configure(yscrollcommand=scrollbar.set)
        self._chapter.canvas.config(scrollregion=(0, 0, 400, 2000))  # width=400, height=2000
        # NIF: Namespace = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core")
        paragraph: Paragraph = Paragraph(self._chapter, graph,30)
        sentence: Sentence = Sentence(paragraph)
        Tok(sentence, "Hello")
        Tok(sentence, " ")
        Tok(sentence, "World")
        Tok(sentence, "!")
        Tok(sentence, " ")
        Tok(sentence, "This")
        Tok(sentence, " ")
        Tok(sentence, "is")
        Tok(sentence, " ")
        Tok(sentence, "a")
        Tok(sentence, " ")
        Tok(sentence, "line")
        Tok(sentence, " ")
        Tok(sentence, "of")
        Tok(sentence, " ")
        Tok(sentence, "text")
        Tok(sentence, ".")
        Tok(sentence, " ")
        sentence2: Sentence = Sentence(paragraph)
        Tok(sentence2, "This")
        Tok(sentence2, " ")
        Tok(sentence2, "is")
        Tok(sentence2, " ")
        Tok(sentence2, "another")
        Tok(sentence2, " ")
        Tok(sentence2, "line")
        Tok(sentence2, " ")
        Tok(sentence2, "of")
        Tok(sentence2, " ")
        Tok(sentence2, "text")
        Tok(sentence2, ".")
        Tok(sentence2, " ")
        sentence3: Sentence = Sentence(paragraph)
        Tok(sentence3, "And")
        Tok(sentence3, " ")
        Tok(sentence3, "this")
        Tok(sentence3, " ")
        Tok(sentence3, "is")
        Tok(sentence3, " ")
        Tok(sentence3, "yet")
        Tok(sentence3, " ")
        Tok(sentence3, "another")
        Tok(sentence3, " ")
        Tok(sentence3, "line")
        Tok(sentence3, " ")
        Tok(sentence3, "of")
        Tok(sentence3, " ")
        Tok(sentence3, "text")
        Tok(sentence3, ".")
        Tok(sentence3, "\n")
        paragraph2: Paragraph = Paragraph(self._chapter, graph, 30)
        sentence4: Sentence = Sentence(paragraph2)
        Tok(sentence4, "Hello")
        Tok(sentence4, " ")
        Tok(sentence4, "World")
        Tok(sentence4, "!")
        Tok(sentence4, " ")
        Tok(sentence4, "This")
        Tok(sentence4, " ")
        Tok(sentence4, "is")
        Tok(sentence4, " ")
        Tok(sentence4, "a")
        Tok(sentence4, " ")
        Tok(sentence4, "line")
        Tok(sentence4, " ")
        Tok(sentence4, "of")
        Tok(sentence4, " ")
        Tok(sentence4, "text")
        Tok(sentence4, ".")
        Tok(sentence4, " ")
        sentence5: Sentence = Sentence(paragraph2)
        Tok(sentence5, "This")
        Tok(sentence5, " ")
        Tok(sentence5, "is")
        Tok(sentence5, " ")
        Tok(sentence5, "another")
        Tok(sentence5, " ")
        Tok(sentence5, "line")
        Tok(sentence5, " ")
        Tok(sentence5, "of")
        Tok(sentence5, " ")
        Tok(sentence5, "text")
        Tok(sentence5, ".")
        Tok(sentence5, " ")
        sentence6: Sentence = Sentence(paragraph2)
        Tok(sentence6, "And")
        Tok(sentence6, " ")
        Tok(sentence6, "this")
        Tok(sentence6, " ")
        Tok(sentence6, "is")
        Tok(sentence6, " ")
        Tok(sentence6, "yet")
        Tok(sentence6, " ")
        Tok(sentence6, "another")
        Tok(sentence6, " ")
        Tok(sentence6, "line")
        Tok(sentence6, " ")
        Tok(sentence6, "of")
        Tok(sentence6, " ")
        tok = Tok(sentence6, "text")
        Tok(sentence6, ".")
        Tok(sentence6, "\n")

        tok.place_cursor_at_word_index(0)

        #frame.bind("<Configure>", self.frame_resized)

    def start(self):
        """Start the UI. This is the entrypoint for the application."""
        self.root.mainloop()

    @property
    def frame(self):
        return self._frame

    @property
    def chapter(self):
        return self._chapter

#    def frame_resized(self, event: tk.Event):
#        print(f"Frame resized to {event.width}x{event.height}")
