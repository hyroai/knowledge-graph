import itertools
from typing import Callable, Iterable, Tuple

import gamla
import immutables

from . import common_relations, primitives, triplet, triplets_index

OneToOne = Callable[
    [triplets_index.TripletsWithIndex],
    triplets_index.TripletsWithIndex,
]


def map_primitives(f: primitives.OneToOne) -> OneToOne:
    return map_triplets(
        gamla.when(
            triplet.relation_in([common_relations.TRIGGER, common_relations.DISPLAY]),
            triplet.transform_object(f),
        )
    )


def transform_triplets(
    f: Callable[[Iterable[triplet.Triplet]], Iterable[triplet.Triplet]]
):
    return gamla.compose_left(triplets_index.triplets, f, triplets_index.from_triplets)


def merge_graphs_nodes_by_id(
    graphs: Iterable[triplets_index.TripletsWithIndex],
) -> triplets_index.TripletsWithIndex:
    graph_triplets = tuple(map(triplets_index.triplets, graphs))
    if not graph_triplets:
        return triplets_index.from_triplets(())
    max_graph = max(graph_triplets, key=len)
    return gamla.pipe(
        graph_triplets,
        gamla.filter(gamla.not_equals(max_graph)),
        gamla.reduce(immutables.Map.update, max_graph),
        triplets_index.from_triplets,
    )


mapcat_triplets: Callable[[triplet.OneToMany], OneToOne] = gamla.compose(
    transform_triplets, gamla.mapcat
)
map_triplets: Callable[[triplet.OneToOne], OneToOne] = gamla.compose(
    transform_triplets, gamla.map
)
_filter_triplets: Callable[[triplet.Predicate], OneToOne] = gamla.compose(
    transform_triplets, gamla.filter
)


def _filter_pairs(condition: Callable[[Tuple[triplet.Element, triplet.Element]], bool]):
    return _filter_triplets(gamla.compose_left(triplet.subject_object_pair, condition))


remove_pairs = gamla.compose(_filter_pairs, gamla.complement)


@gamla.curry
def expand_triplets_by_object(
    predicate: triplet.Predicate, one_to_many: triplet.ElementOneToMany
) -> OneToOne:
    return transform_and_merge(
        mapcat_triplets(
            gamla.ternary(
                predicate,
                gamla.compose_left(
                    gamla.packstack(itertools.repeat, itertools.repeat, one_to_many),
                    gamla.star(zip),
                ),
                gamla.just(()),
            )
        )
    )


def expand_triggers(f: primitives.OneToMany) -> OneToOne:
    return expand_triplets_by_object(
        triplet.relation_equals(common_relations.TRIGGER), f
    )


def filter_primitives(predicate: primitives.Predicate) -> OneToOne:
    return _filter_triplets(
        gamla.anyjuxt(
            gamla.complement(triplet.relation_equals(common_relations.TRIGGER)),
            gamla.compose_left(triplet.object, predicate),
        )
    )


remove_primitives = gamla.compose_left(gamla.complement, filter_primitives)


def transform_and_merge(f: OneToOne) -> OneToOne:
    return gamla.compose_left(gamla.pair_with(f), merge_graphs_nodes_by_id)


def remove_entities(is_bad_id: triplet.Predicate) -> OneToOne:
    return transform_triplets(gamla.remove(gamla.anymap(is_bad_id)))


def merge_with(*graphs: triplets_index.TripletsWithIndex) -> OneToOne:
    return lambda graph: merge_graphs_nodes_by_id([graph, *graphs])
