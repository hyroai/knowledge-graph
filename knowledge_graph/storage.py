import dataclasses
import json
from typing import Callable, Dict, FrozenSet

import dataclasses_json
import gamla
from cloud_utils.cache import file_store

from . import triplet, triplets_index

GraphHash = str


_REGISTERED_GRAPHS: Dict[GraphHash, triplets_index.TripletsWithIndex] = {}


# TODO(Noah): should be make_raise once we no longer cache empty graphs
# class _EmptyGraphLoaded(Exception):
#     pass


def register_graph(hash: GraphHash, graph: triplets_index.TripletsWithIndex):
    _REGISTERED_GRAPHS[hash] = graph


def get_graph_hash(graph: triplets_index.TripletsWithIndex) -> GraphHash:
    try:
        return next(k for (k, v) in _REGISTERED_GRAPHS.items() if v is graph)
    except StopIteration:
        return gamla.pipe(
            graph,
            gamla.pair_with(
                gamla.compose_left(to_json, gamla.compute_stable_json_hash)
            ),
            gamla.side_effect(gamla.star(register_graph)),
            gamla.head,
        )


def get_graph(graph_id: GraphHash) -> triplets_index.TripletsWithIndex:
    return _REGISTERED_GRAPHS[graph_id]


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Node:
    graph_id: GraphHash
    node_id: triplet.Element

    def __repr__(self):
        return f"Node:{self.node_id[:20]}"


Nodes = FrozenSet[Node]

node_id = gamla.attrgetter("node_id")


@gamla.curry
def make_node_universal_id(
    graph: triplets_index.TripletsWithIndex, node: triplet.Element
) -> Node:
    return Node(get_graph_hash(graph), node)


def run_on_kg_and_node_any_output(f):
    def inner(node: Node):
        return f(get_graph(node.graph_id), node.node_id)

    return inner


def run_on_kg_and_node(f):
    def inner(node: Node) -> Nodes:
        return gamla.pipe(
            node,
            run_on_kg_and_node_any_output(f),
            gamla.map(lambda result_node: Node(node.graph_id, result_node)),
            frozenset,
        )

    return inner


_from_json = gamla.compose_left(
    gamla.itemgetter("triplets"),
    gamla.map(
        triplet.transform_object(gamla.when(gamla.is_instance(dict), gamla.freeze_deep))
    ),
    triplets_index.from_triplets,
)

to_json: Callable[[triplets_index.TripletsWithIndex], Dict] = gamla.compose_left(
    triplets_index.triplets, sorted, gamla.wrap_dict("triplets")
)


def load_to_kg(
    environment: str, environment_local: str, bucket_name: str
) -> Callable[[GraphHash], triplets_index.TripletsWithIndex]:
    return gamla.compose_left(
        gamla.pair_right(
            gamla.first(
                get_graph,
                gamla.compose_left(
                    file_store.load_by_hash(
                        environment == environment_local, bucket_name
                    ),
                    _from_json,
                ),
                exception_type=KeyError,
            )
        ),
        gamla.side_effect(gamla.star(register_graph)),
        gamla.second,
        gamla.when(
            gamla.compose_left(triplets_index.triplets, gamla.empty),
            # TODO(Noah): should be make_raise once we no longer cache empty graphs
            gamla.log_text("_EmptyGraphLoaded"),
        ),
    )


load_knowledge_graph_from_file = gamla.compose_left(json.load, _from_json)
