import dataclasses
import functools
from typing import Callable, FrozenSet

import dataclasses_json
import gamla
import immutables

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
    def subject_index(self) -> _OneLevelIndex:
        return gamla.pipe(
            self, triplets, gamla.make_index(map(gamla.groupby, [triplet.subject]))
        )

    @functools.cached_property
    def relation_index(self) -> _OneLevelIndex:
        return gamla.pipe(
            self, triplets, gamla.make_index(map(gamla.groupby, [triplet.relation]))
        )

    @functools.cached_property
    def object_index(self) -> _OneLevelIndex:
        return gamla.pipe(
            self, triplets, gamla.make_index(map(gamla.groupby, [triplet.object]))
        )

    @functools.cached_property
    def subject_relation_index(self) -> _TwoLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.make_index(map(gamla.groupby, [triplet.subject, triplet.relation])),
        )

    @functools.cached_property
    def object_relation_index(self) -> _TwoLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.make_index(map(gamla.groupby, [triplet.object, triplet.relation])),
        )

    @functools.cached_property
    def subject_relation_and_object_type_index(self):
        return gamla.pipe(
            self,
            triplets,
            gamla.make_index(
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
                ]
            ),
        )


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
