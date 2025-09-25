from typing import Dict, List, Type

from rdflib.term import URIRef

from ezwrite.graph.entity import Entity
from ezwrite.graph.ezproperty import EzProperty


class PropertyList():
    """An Entity can have a list of properties.
    This conveniently allows them to be quickly searched for by
    predicate and entity type"""
    def __init__(self):
        self.hashtable: Dict[str, Dict[str, List[Entity]]] = {}

    def append(self,
            predicate: str | URIRef | EzProperty,
            entity: Entity):
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        type_key: str = entity.__class__.__name__
        existing: Dict[str, List[Entity]] | None = self.hashtable[pred_key]
        if existing is None:
            self.hashtable[pred_key] = {type_key: [entity]}
            return
        existing_list: List[Entity] = existing[type_key]
        if entity in existing_list:
            return
        existing_list.append(entity)

    def list_of(self,
                predicate: str | URIRef | EzProperty,
                entity_type_key: str | Type[Entity]
                ) -> List[Entity]:
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        type_key: str = entity_type_key if isinstance(entity_type_key, str) else entity_type_key.__name__
        existing: Dict[str, List[Entity]] | None = self.hashtable[pred_key]
        if existing is None:
            return []
        existing_list: List[Entity] = existing[type_key]
        if existing_list is None:
            return []
        return existing_list
