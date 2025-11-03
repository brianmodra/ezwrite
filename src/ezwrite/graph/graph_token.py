from abc import ABC

from rdflib.graph import Graph
from rdflib.term import URIRef

from ezwrite.graph.ezentity import EzEntity


class GraphToken(EzEntity, ABC):
    """This provides an interface to manipulate a token, without specifying
    the actual implementation of the token"""
    def __init__(self, graph: Graph):
        super().__init__(graph, URIRef("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#Token"))
