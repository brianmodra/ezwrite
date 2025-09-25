import tkinter as tk
from tkinter import Frame, Scrollbar, Tk

from rdflib.graph import Graph

from ezwrite.ui.chapter import Chapter
from ezwrite.ui.paragraph import Paragraph
from ezwrite.ui.position import Position
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
        scrollbar: Scrollbar = tk.Scrollbar(self._frame, orient="vertical", command=self.chapter.yview)
        scrollbar.pack(side="right", fill="y")
        self._chapter.configure(yscrollcommand=scrollbar.set)
        self._chapter.config(scrollregion=(0, 0, 400, 2000))  # width=400, height=2000
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
        Tok(sentence, "This")
        Tok(sentence, " ")
        Tok(sentence, "is")
        Tok(sentence, " ")
        Tok(sentence, "another")
        Tok(sentence, " ")
        Tok(sentence, "line")
        Tok(sentence, " ")
        Tok(sentence, "of")
        Tok(sentence, " ")
        Tok(sentence, "text")
        Tok(sentence, ".")
        Tok(sentence, " ")
        Tok(sentence, "And")
        Tok(sentence, " ")
        Tok(sentence, "this")
        Tok(sentence, " ")
        Tok(sentence, "is")
        Tok(sentence, " ")
        Tok(sentence, "yet")
        Tok(sentence, " ")
        Tok(sentence, "another")
        Tok(sentence, " ")
        Tok(sentence, "line")
        Tok(sentence, " ")
        Tok(sentence, "of")
        Tok(sentence, " ")
        Tok(sentence, "text")
        Tok(sentence, ".")
        Tok(sentence, "\n")
        paragraph2: Paragraph = Paragraph(self._chapter, graph, 30)
        sentence2: Sentence = Sentence(paragraph2)
        Tok(sentence2, "Hello")
        Tok(sentence2, " ")
        Tok(sentence2, "World")
        Tok(sentence2, "!")
        Tok(sentence2, " ")
        Tok(sentence2, "This")
        Tok(sentence2, " ")
        Tok(sentence2, "is")
        Tok(sentence2, " ")
        Tok(sentence2, "a")
        Tok(sentence2, " ")
        Tok(sentence2, "line")
        Tok(sentence2, " ")
        Tok(sentence2, "of")
        Tok(sentence2, " ")
        Tok(sentence2, "text")
        Tok(sentence2, ".")
        Tok(sentence2, " ")
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
        Tok(sentence2, "And")
        Tok(sentence2, " ")
        Tok(sentence2, "this")
        Tok(sentence2, " ")
        Tok(sentence2, "is")
        Tok(sentence2, " ")
        Tok(sentence2, "yet")
        Tok(sentence2, " ")
        Tok(sentence2, "another")
        Tok(sentence2, " ")
        Tok(sentence2, "line")
        Tok(sentence2, " ")
        Tok(sentence2, "of")
        Tok(sentence2, " ")
        tok = Tok(sentence2, "text")
        Tok(sentence2, ".")
        Tok(sentence2, "\n")

        tok.place_cursor(Position(10,0))

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
