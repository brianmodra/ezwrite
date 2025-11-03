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
               entity: Entity
               ) -> None:
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        type_key: str = entity.__class__.__name__
        if pred_key not in self.hashtable:
            self.hashtable[pred_key] = {type_key: [entity]}
            return
        existing: Dict[str, List[Entity]] = self.hashtable[pred_key]
        existing_list: List[Entity] = existing[type_key]
        if entity in existing_list:
            return
        existing_list.append(entity)

    def insert_before(self,
                      reference: Entity,
                      predicate: str | URIRef | EzProperty,
                      entity: Entity
                      ) -> None:
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        type_key: str = entity.__class__.__name__
        if pred_key not in self.hashtable:
            raise ValueError("reference not found, no matching predicate in the list")
        existing: Dict[str, List[Entity]] = self.hashtable[pred_key]
        existing_list: List[Entity] = existing[type_key]
        if not reference in existing_list:
            raise ValueError("reference not found in the list")
        if entity in existing_list:
            return
        ind = existing_list.index(reference)
        existing_list.insert(ind, entity)

    def remove(self,
               predicate: str | URIRef | EzProperty,
               entity: Entity
               ) -> bool:
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        type_key: str = entity.__class__.__name__
        if pred_key not in self.hashtable:
            return False
        existing: Dict[str, List[Entity]] = self.hashtable[pred_key]
        existing_list: List[Entity] = existing[type_key]
        if entity in existing_list:
            existing_list.remove(entity)
            return True
        return False

    def all_entities_of(self,
                predicate: str | URIRef | EzProperty,
                ) -> List[Entity]:
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        if pred_key not in self.hashtable:
            return []
        existing: Dict[str, List[Entity]] = self.hashtable[pred_key]
        return_list: List[Entity] = []
        for val_list in existing.values():
            return_list.extend(val_list)
        return return_list

    def has_entities_of(self,
                        predicate: str | URIRef | EzProperty,
                        ) -> bool:
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        if pred_key not in self.hashtable:
            return False
        existing: Dict[str, List[Entity]] = self.hashtable[pred_key]
        return len(existing.values()) > 0

    def entities_of(self,
                    predicate: str | URIRef | EzProperty,
                    entity_type_key: str | Type[Entity]
                    ) -> List[Entity]:
        pred_key: str = predicate.uri.lower() if isinstance(predicate, EzProperty) else predicate.lower()
        type_key: str = entity_type_key if isinstance(entity_type_key, str) else entity_type_key.__name__
        if pred_key not in self.hashtable:
            return []
        existing: Dict[str, List[Entity]] = self.hashtable[pred_key]
        existing_list: List[Entity] = existing[type_key]
        if existing_list is None:
            return []
        return existing_list
