from rdflib.term import URIRef


class EzProperty():
    """Models a property of an Entity"""
    HAS_PART = URIRef("http://purl.org/dc/terms/hasPart")
    IS_PART_OF = URIRef("http://purl.org/dc/terms/isPartOf")

    def __init__(self, uri: str | URIRef):
        self._uri = URIRef(uri)

    @property
    def uri(self) -> URIRef:
        return self._uri
