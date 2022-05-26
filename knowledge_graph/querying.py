# Queries that use a global storage of kgs. Best avoid and use `querying_raw.py`.
import functools
from typing import Callable, Dict, FrozenSet, Iterable, Optional, Tuple

import gamla

from . import (
    common_relations,
    primitives,
    querying_raw,
    storage,
    triplet,
    triplets_index,
)


class AttributeMissing(Exception):  # noqa
    pass


class NodeTitleMissing(Exception):  # noqa
    pass


get_nodes_by_relations: Callable[
    [Iterable[triplet.Element]], Callable[[storage.Node], storage.Nodes]
] = gamla.compose_left(
    gamla.map(querying_raw.neighbors),
    frozenset,
    gamla.star(gamla.juxtcat),
    storage.run_on_kg_and_node,
)


get_nodes_by_relation: Callable[
    [triplet.Element], Callable[[storage.Node], storage.Nodes]
] = gamla.compose_left(gamla.wrap_tuple, get_nodes_by_relations)

has_instances = storage.run_on_kg_and_node_any_output(
    querying_raw.has_neighbors_with_relation(common_relations.TYPE)
)


def get_nodes_by_reveresed_relation(
    relation: triplet.Element,
) -> Callable[[storage.Node], storage.Nodes]:
    return storage.run_on_kg_and_node(querying_raw.neighbors_reversed(relation))


def get_reveresed_relations_by_object() -> Callable[[storage.Node], storage.Nodes]:
    return storage.run_on_kg_and_node(querying_raw.relations_reversed)


_get_node_display_value = gamla.compose_left(
    get_nodes_by_relation(common_relations.DISPLAY),
    gamla.map(gamla.attrgetter("node_id")),
)
get_node_primitives = gamla.compose_left(
    get_nodes_by_relation(common_relations.TRIGGER),
    gamla.map(gamla.attrgetter("node_id")),
)
get_node_edges = get_nodes_by_relation(common_relations.ASSOCIATION)

get_node_reverse_edges = get_nodes_by_reveresed_relation(common_relations.ASSOCIATION)

get_node_types = get_nodes_by_relation(common_relations.TYPE)

get_node_instances = get_nodes_by_reveresed_relation(common_relations.TYPE)


association_non_directional = gamla.juxtcat(get_node_edges, get_node_reverse_edges)


@gamla.curry
def find_exactly_bare(
    text: str, graph: triplets_index.TripletsWithIndex
) -> storage.Node:
    return find_exactly(graph)(text)


def find_exactly_bare_ignore_capitalization(
    text: str, graph: triplets_index.TripletsWithIndex
) -> storage.Node:
    return storage.make_node_universal_id(
        graph,
        querying_raw.find_unique_by_trigger_or_display_text_custom_kind_ignore_capitalization(
            primitives.TEXTUAL, graph, text
        ),
    )


@gamla.curry
def find_by_trigger_ignore_capitalization(
    text: str, graph: triplets_index.TripletsWithIndex
) -> FrozenSet[Optional[storage.Node]]:
    return gamla.pipe(
        querying_raw.find_by_trigger_ignore_capitalization_custom_kind(
            primitives.TEXTUAL, graph, text
        ),
        gamla.ternary(
            gamla.nonempty,
            gamla.map(lambda node: storage.make_node_universal_id(graph, node)),
            gamla.just(frozenset()),
        ),
        frozenset,
    )


find_exactly_by_trigger_ignore_capitalization_or_raise = gamla.compose_left(
    find_by_trigger_ignore_capitalization,
    gamla.ternary(
        gamla.nonempty,
        gamla.compose_left(
            gamla.check(gamla.len_equals(1), AssertionError), gamla.head
        ),
        lambda x: gamla.just_raise(AssertionError(f"Couldn't find [{x}] in the graph")),
    ),
)


@gamla.curry
def find_exactly_with_custom_kind(
    kind: primitives.Kind, graph: triplets_index.TripletsWithIndex
) -> Callable[[str], storage.Node]:
    def find_exactly(text: str):
        return storage.make_node_universal_id(
            graph,
            querying_raw.find_unique_by_trigger_or_display_text_custom_kind(
                kind, graph, text
            ),
        )

    return find_exactly


find_exactly = find_exactly_with_custom_kind(primitives.TEXTUAL)


@gamla.curry
def find_exactly_by_trigger_with_custom_kind_ignore_capitalization(
    kind: primitives.Kind, graph: triplets_index.TripletsWithIndex
) -> Callable[[str], storage.Node]:
    def find_exactly(text: str):
        return storage.make_node_universal_id(
            graph,
            querying_raw.find_unique_by_trigger_ignore_capitalization_custom_kind(
                kind, graph, text
            ),
        )

    return find_exactly


find_exactly_trigger_only = (
    find_exactly_by_trigger_with_custom_kind_ignore_capitalization(primitives.TEXTUAL)
)


get_node_title = functools.cache(
    gamla.try_and_excepts(
        StopIteration,
        lambda _, node: gamla.just_raise(
            NodeTitleMissing(
                f"Title is missing in node id: {node.node_id}, graph id: {node.graph_id}"
            )
        ),
        gamla.compose_left(
            _get_node_display_value,
            gamla.sort_by(primitives.text),
            gamla.head,
            primitives.to_str,
        ),
    )
)


title_or_node_id = gamla.first(
    get_node_title, storage.node_id, exception_type=NodeTitleMissing
)


@gamla.curry
def find_attr_display_text(
    node_id: storage.Node, attr_node_id: storage.Node
) -> FrozenSet[str]:
    return gamla.pipe(
        node_id,
        get_entity_attribute(attr_node_id),
        gamla.map(get_node_title),
        frozenset,
    )


@gamla.curry
def get_node_inner_value(
    value_type: primitives.Kind, node_id: storage.Node
) -> FrozenSet[primitives.Primitive]:
    return gamla.pipe(
        node_id,
        get_node_primitives,
        gamla.filter(primitives.kind_equals(value_type)),
        frozenset,
    )


pointing_to: Callable[[storage.Nodes], storage.Nodes] = gamla.compose_left(
    gamla.mapcat(get_node_reverse_edges), frozenset
)


types_of: Callable[[storage.Nodes], storage.Nodes] = gamla.compose_left(
    gamla.mapcat(get_node_types), frozenset
)


pointed_by: Callable[[storage.Nodes], storage.Nodes] = gamla.compose_left(
    gamla.mapcat(get_node_edges), frozenset
)


all_subjects = gamla.prepare_and_apply(
    gamla.compose(
        gamla.before(
            gamla.compose_left(
                triplets_index.triplets, gamla.map(triplet.subject), gamla.unique
            )
        ),
        gamla.map,
        storage.make_node_universal_id,
    )
)


@functools.cache
@gamla.curry
def filter_entities_by_attribute(
    entities: storage.Nodes, attributes: storage.Nodes
) -> storage.Nodes:
    return gamla.pipe(
        entities,
        gamla.filter(
            gamla.compose_left(get_node_edges, gamla.anymap(gamla.contains(attributes)))
        ),
        frozenset,
    )


@gamla.curry
def node_similarity(node1_id: storage.Node, node2_id: storage.Node) -> float:
    edges_union_len = len(get_node_edges(node1_id) | get_node_edges(node2_id))
    if edges_union_len == 0:
        return 0.0
    return len(get_node_edges(node1_id) & get_node_edges(node2_id)) / edges_union_len


def is_instance_of(type_node: storage.Node):
    return gamla.compose_left(get_node_types, gamla.inside(type_node))


def is_super_type(parent: storage.Node, child: storage.Node) -> bool:
    return bool(
        parent != child
        and get_node_instances(parent)
        and get_node_instances(child)
        and all(
            instance in get_node_instances(parent)
            for instance in get_node_instances(child)
        )
    )


nodes_share_type = gamla.compose_left(
    gamla.map(get_node_types), gamla.star(frozenset.intersection), bool
)


def _get_most_specific_type(
    type_to_node_count: Dict[storage.Node, int], required_count: int
):
    return gamla.pipe(
        type_to_node_count,
        gamla.valfilter(gamla.equals(required_count)),
        # Take the most specific of covering types.
        gamla.bottom(
            # Secondary sort for stability.
            key=gamla.juxt(
                gamla.compose(len, get_node_instances),
                lambda node: node.node_id + node.graph_id,
            )
        ),
        next,
    )


@functools.cache
def get_minimal_type_cover(nodes: storage.Nodes) -> Tuple[storage.Node, ...]:
    if not nodes:
        return ()
    type_to_node_count = get_group_type(nodes)
    if not type_to_node_count:
        return ()
    try:
        return (_get_most_specific_type(type_to_node_count, len(nodes)),)
    except StopIteration:
        # If not all nodes share a type, get the one shared by most.
        selected_type_node = max(type_to_node_count, key=type_to_node_count.get)  # type: ignore
        return gamla.pipe(
            nodes,
            gamla.remove(
                gamla.compose_left(get_node_types, gamla.inside(selected_type_node))
            ),
            frozenset,
            get_minimal_type_cover,
            gamla.prefix(selected_type_node),
            tuple,
        )


get_group_type: Callable[[storage.Nodes], Dict[storage.Node, int]] = gamla.compose_left(
    gamla.mapcat(get_node_types), gamla.count_by(gamla.identity)
)


def possibly_traverse_to_instances(nodes: storage.Nodes) -> storage.Nodes:
    if len(nodes) != 1:
        return nodes
    return get_node_instances(gamla.head(nodes)) or nodes


possibly_traverse_to_node_instances = gamla.compose_left(
    lambda node: frozenset([node]), possibly_traverse_to_instances
)


@gamla.curry
def get_associated_values(
    node: storage.Node, value_type: primitives.Kind
) -> storage.Nodes:
    if has_primitive_type(value_type, node):
        return frozenset([node])
    return frozenset(filter(has_primitive_type(value_type), get_node_edges(node)))


@gamla.curry
def has_primitive_type(primitive_type: primitives.Kind, node: storage.Node) -> bool:
    return bool(get_node_inner_value(primitive_type, node))


def similar(query_node: storage.Node) -> Iterable[storage.Node]:
    return gamla.pipe(
        query_node,
        get_node_edges,
        gamla.filter(lambda node: gamla.count(get_node_reverse_edges(node)) < 100),
        gamla.mapcat(get_node_reverse_edges),
        gamla.filter(
            gamla.compose_left(get_node_types, get_node_types(query_node).intersection)
        ),
        gamla.unique,
        gamla.top(key=node_similarity(query_node)),
        gamla.remove(gamla.equals(query_node)),
    )


node_to_latlng = gamla.compose_left(
    get_associated_values(value_type=primitives.LOCATION),
    gamla.mapcat(get_node_inner_value(primitives.LOCATION)),
    gamla.map(primitives.coordinate),
    gamla.head,
    gamla.check(gamla.identity, AssertionError),
)


get_all_local_nodes_in_graph: Callable[
    [Iterable[storage.Node]],
    storage.Nodes,
] = gamla.compose_left(
    gamla.unique,
    gamla.mapcat(
        gamla.juxtcat(
            gamla.wrap_tuple, get_node_reverse_edges, get_node_edges, get_node_instances
        )
    ),
    frozenset,
)


def instances_of(type_nodes: storage.Nodes) -> storage.Nodes:
    return gamla.pipe(type_nodes, gamla.mapcat(get_node_instances), frozenset)


get_types_of_first_node = gamla.compose_left(gamla.head, get_node_types)

get_node_type = gamla.compose_left(get_node_types, gamla.head, get_node_title)


pointing_to_type_siblings = gamla.compose(
    pointing_to, instances_of, get_types_of_first_node
)


@gamla.curry
def get_attribute_first_value(attribute: str, node: storage.Node) -> str:
    try:
        return gamla.head(
            find_attr_display_text(
                node, find_exactly_bare(attribute, storage.get_graph(node.graph_id))
            )
        )
    except StopIteration:
        raise AttributeMissing(
            f"Attribute: {attribute} is missing in node id: {node.node_id}"
        )


get_node_size_values = gamla.compose_left(
    get_node_primitives,
    gamla.filter(primitives.kind_equals(primitives.SIZE)),
    gamla.map(primitives.extract_number_value),
    tuple,
)

get_node_primitives_values = gamla.compose_left(
    get_node_primitives, gamla.map(primitives.text), frozenset
)


def query_by_primitive(kg: triplets_index.TripletsWithIndex):
    return gamla.compose_left(
        querying_raw.neighbors_reversed(common_relations.TRIGGER, kg),
        gamla.map(storage.make_node_universal_id(kg)),
    )


@gamla.curry
def get_entity_attribute(
    type: storage.Node, node: storage.Node
) -> Iterable[storage.Node]:
    graph = storage.get_graph(node.graph_id)
    return gamla.pipe(
        graph.subject_relation_and_object_type_index(node.node_id)(
            common_relations.ASSOCIATION
        )(type.node_id),
        gamla.map(
            gamla.compose_left(triplet.object, storage.make_node_universal_id(graph))
        ),
    )


@gamla.curry
def get_entity_attribute_with_text(
    type: str, node: storage.Node
) -> Iterable[storage.Node]:
    return gamla.pipe(
        node,
        gamla.pair_with(
            gamla.compose_left(
                gamla.attrgetter("graph_id"), storage.get_graph, find_exactly_bare(type)
            )
        ),
        gamla.star(get_entity_attribute),
    )


@gamla.curry
def is_neighbor_by_id(
    kg: triplets_index.TripletsWithIndex, text: str
) -> Callable[[storage.Node], bool]:
    return gamla.compose_left(get_node_edges, gamla.inside(find_exactly_bare(text, kg)))


def is_instance_by_id(
    kg: triplets_index.TripletsWithIndex,
) -> Callable[[str], Callable[[storage.Node], bool]]:
    return gamla.compose_left(find_exactly(kg), is_instance_of)


def is_instance_of_element(element: triplet.Element) -> Callable[[storage.Node], bool]:
    return gamla.compose_left(
        get_node_types, gamla.map(get_node_title), gamla.inside(element)
    )


def all_graph_connectivity(
    graph: triplets_index.TripletsWithIndex,
    triplets_predicate: Callable[[triplet.Element], bool],
) -> Iterable[FrozenSet]:
    return gamla.pipe(
        graph,
        triplets_index.triplets,
        gamla.sync.filter(triplets_predicate),
        gamla.mapcat(
            gamla.juxt(
                gamla.juxt(triplet.subject, triplet.object),
                gamla.juxt(triplet.object, triplet.subject),
            )
        ),
        gamla.edges_to_graph,
        gamla.get_connectivity_components,
        gamla.sync.remove(gamla.len_equals(1)),  # Reduce size.
        gamla.sync.map(
            gamla.sync.compose_left(
                gamla.sync.map(storage.make_node_universal_id(graph)), tuple
            )
        ),
        tuple,
    )


@gamla.curry
def all_related_nodes_in_connectivity(
    connectivity_group, node: storage.Node
) -> FrozenSet[storage.Node]:
    return gamla.pipe(
        connectivity_group,
        gamla.filter(gamla.inside(node)),
        tuple,
        gamla.ternary(
            gamla.empty,
            # Handle the single node case.
            gamla.just((node,)),
            gamla.head,
        ),
    )


def bidirectional_associations_between_types(
    type_node1: storage.Node, type_node2: storage.Node
) -> Iterable[Tuple[str, str]]:
    return gamla.pipe(
        type_node1,
        get_node_instances,
        gamla.mapcat(
            gamla.compose_left(
                gamla.juxt(
                    storage.node_id,
                    gamla.compose_left(
                        association_non_directional,
                        gamla.filter(is_instance_of(type_node2)),
                        gamla.map(storage.node_id),
                    ),
                ),
                gamla.explode(1),
            )
        ),
    )


find_and_get_node_id = gamla.compose_left(
    find_exactly_bare, gamla.attrgetter("node_id")
)


def nodes_from_texts(kg: triplets_index.TripletsWithIndex):
    return gamla.compose_left(gamla.map(find_exactly(kg)), frozenset)


def nodes_of_type_related_to_node(
    kg_node: storage.Node, nodes_type: str
) -> storage.Nodes:
    return get_node_reverse_edges(kg_node) & gamla.pipe(
        kg_node.graph_id,
        storage.get_graph,
        find_exactly_bare(nodes_type),
        get_node_instances,
    )
