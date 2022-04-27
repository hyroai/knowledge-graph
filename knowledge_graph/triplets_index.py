import dataclasses
import functools
from typing import Callable, FrozenSet

import dataclasses_json
import gamla
import immutables
from gamla import nested_index

from . import common_relations, triplet

_OneLevelIndex = Callable[[triplet.Element], FrozenSet[triplet.Triplet]]
_TwoLevelIndex = Callable[[triplet.Element], _OneLevelIndex]


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class TripletsWithIndex:
    triplets: FrozenSet[triplet.Triplet] = gamla.get_encode_config()

    def __repr__(self):
        return "\n".join(sorted(map(str, self.triplets)))

    @gamla.timeit
    def trigger_cached_properties(self):
        self.subject_index
        self.relation_index
        self.object_index
        self.object_relation_index
        self.subject_relation_and_object_type_index

    @functools.cached_property
    def _subject_index(self) -> nested_index.HierarchicalIndex:
        return nested_index.build([gamla.groupby(triplet.subject)], self.triplets)

    @functools.cached_property
    def subject_index(self) -> _OneLevelIndex:
        return nested_index.to_query(self._subject_index)

    @functools.cached_property
    def _relation_index(self) -> nested_index.HierarchicalIndex:
        return nested_index.build([gamla.groupby(triplet.relation)], self.triplets)

    @functools.cached_property
    def relation_index(self) -> _OneLevelIndex:
        return nested_index.to_query(self._relation_index)

    @functools.cached_property
    def _object_index(self) -> nested_index.HierarchicalIndex:
        return nested_index.build([gamla.groupby(triplet.object)], self.triplets)

    @functools.cached_property
    def object_index(self) -> _OneLevelIndex:
        return nested_index.to_query(self._object_index)

    @functools.cached_property
    def _subject_relation_index(self) -> nested_index.HierarchicalIndex:
        return nested_index.build(
            map(gamla.groupby, [triplet.subject, triplet.relation]), self.triplets
        )

    @functools.cached_property
    def subject_relation_index(self) -> _TwoLevelIndex:
        return nested_index.to_query(self._subject_relation_index)

    @functools.cached_property
    def _object_relation_index(self) -> nested_index.HierarchicalIndex:
        return nested_index.build(
            map(gamla.groupby, [triplet.object, triplet.relation]), self.triplets
        )

    @functools.cached_property
    def object_relation_index(self) -> _TwoLevelIndex:
        return nested_index.to_query(self._object_relation_index)

    @functools.cached_property
    def _subject_relation_and_object_type_index(
        self,
    ) -> nested_index.HierarchicalIndex:
        return nested_index.build(
            [
                gamla.groupby(triplet.subject),
                gamla.groupby(triplet.relation),
                gamla.groupby_many(
                    gamla.compose_left(
                        triplet.object,
                        self.subject_relation_index,
                        gamla.apply(common_relations.TYPE),
                        gamla.map(triplet.object),
                    )
                ),
            ],
            self.triplets,
        )

    @functools.cached_property
    def subject_relation_and_object_type_index(self):
        return nested_index.to_query(self._subject_relation_and_object_type_index)


triplets = gamla.attrgetter("triplets")
subject_relation_index = gamla.attrgetter("subject_relation_index")
object_relation_index = gamla.attrgetter("object_relation_index")
relation_index = gamla.attrgetter("relation_index")
object_index = gamla.attrgetter("object_index")


from_triplets = gamla.ternary(
    gamla.is_instance(immutables.Map),
    TripletsWithIndex,
    gamla.compose_left(
        gamla.map(gamla.pair_right(gamla.just(None))), immutables.Map, TripletsWithIndex
    ),
)


from_triplet: Callable[[triplet.Triplet], TripletsWithIndex] = gamla.compose_left(
    gamla.wrap_tuple, from_triplets
)


def retrieve(
    relation: triplet.Element, index: Callable[[TripletsWithIndex], _TwoLevelIndex]
):
    def retrieve(graph: TripletsWithIndex, node: triplet.Element):
        return index(graph)(node)(relation)

    return retrieve
