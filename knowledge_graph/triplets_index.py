import dataclasses
import functools
from typing import Callable, FrozenSet

import dataclasses_json
import gamla

from . import common_relations, triplet

_OneLevelIndex = Callable[[triplet.Element], FrozenSet[triplet.Triplet]]
_TwoLevelIndex = Callable[[triplet.Element], _OneLevelIndex]
_ThreeLevelIndex = Callable[[triplet.Element], _TwoLevelIndex]


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
        self.subject_relation_index

    @functools.cached_property
    def subject_index(self) -> _OneLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.timeit_with_label("building subject_index")(
                gamla.make_index(map(gamla.groupby, [triplet.subject]))
            ),
        )

    @functools.cached_property
    def relation_index(self) -> _OneLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.timeit_with_label("building relation_index")(
                gamla.make_index(map(gamla.groupby, [triplet.relation]))
            ),
        )

    @functools.cached_property
    def object_index(self) -> _OneLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.timeit_with_label("building object_index")(
                gamla.make_index(map(gamla.groupby, [triplet.object]))
            ),
        )

    @functools.cached_property
    def subject_relation_index(self) -> _TwoLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.timeit_with_label("building subject_relation_index")(
                gamla.make_index(
                    map(gamla.groupby, [triplet.subject, triplet.relation])
                )
            ),
        )

        def subject_relation_index(subject: triplet.Element) -> _OneLevelIndex:
            def relation_for_subject(relation):
                return self.subject_index(subject) & self.relation_index(relation)

            return relation_for_subject

        return subject_relation_index

    @functools.cached_property
    def object_relation_index(self) -> _TwoLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.timeit_with_label("building object_relation_index")(
                gamla.make_index(
                    map(gamla.groupby, [triplet.object, triplet.relation])
                )
            ),
        )

        def object_relation_index(object: triplet.Element) -> _OneLevelIndex:
            def relation_for_object(relation):
                return self.object_index(object) & self.relation_index(relation)

            return relation_for_object

        return object_relation_index

    @functools.cached_property
    def subject_relation_and_object_type_index(self) -> _ThreeLevelIndex:
        return gamla.pipe(
            self,
            triplets,
            gamla.timeit_with_label(
                "building subject_relation_and_object_type_index"
            )(
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
                )
            ),
        )

        def subject_relation_and_object_type_index(
            subject: triplet.Element,
        ) -> _TwoLevelIndex:
            def relation_and_object_type(relation: triplet.Element):
                def object_type(type_: triplet.Element):
                    objects_of_type = self.object_relation_index(type_)(
                        common_relations.TYPE
                    )
                    return frozenset(
                        {
                            t
                            for t in self.subject_relation_index(subject)(relation)
                            if self.subject_relation_index(triplet.object(t))(
                                common_relations.TYPE
                            )
                            & objects_of_type
                        }
                    )

                return object_type

            return relation_and_object_type

        return subject_relation_and_object_type_index


triplets = gamla.attrgetter("triplets")
subject_relation_and_object_type_index = gamla.attrgetter(
    "subject_relation_and_object_type_index"
)
subject_relation_index = gamla.attrgetter("subject_relation_index")
object_relation_index = gamla.attrgetter("object_relation_index")
relation_index = gamla.attrgetter("relation_index")
object_index = gamla.attrgetter("object_index")

from_triplets = gamla.compose_left(frozenset, TripletsWithIndex)

from_triplet = gamla.compose_left(gamla.wrap_frozenset, TripletsWithIndex)


def retrieve(
    relation: triplet.Element, index: Callable[[TripletsWithIndex], _TwoLevelIndex]
):
    def retrieve(graph: TripletsWithIndex, node: triplet.Element):
        return index(graph)(node)(relation)

    return retrieve
