from typing import Callable, Dict, Iterable, Optional, Tuple

import gamla

from . import common_relations, primitives, transform, triplet, triplets_index


def primitive_value_to_node(
    primitive: primitives.Primitive, node: triplet.Element
) -> triplets_index.TripletsWithIndex:
    return triplets_index.from_triplets(
        [
            common_relations.display_triplet(node, primitive),
            common_relations.trigger_triplet(node, primitive),
        ]
    )


@gamla.curry
def kind_and_text_to_display_and_trigger_graph(
    kind: primitives.Kind, value: str
) -> triplets_index.TripletsWithIndex:
    """Quick way to create a graph with textual trigger and display value."""
    return primitive_value_to_node(
        primitives.kind_and_text_to_primitive(kind, value), value
    )


value_to_node = kind_and_text_to_display_and_trigger_graph(primitives.TEXTUAL)


def value_to_node_with_type_graph(
    type_node: str,
) -> Callable[[str], triplets_index.TripletsWithIndex]:
    return gamla.compose_left(
        gamla.juxt(value_to_node, lambda node: type_graph(node, type_node)),
        transform.merge_graphs_nodes_by_id,
    )


@gamla.curry
def entity_and_type(entity: str, type: str) -> triplets_index.TripletsWithIndex:
    return transform.merge_graphs_nodes_by_id(
        [
            value_to_node(type),
            value_to_node(entity),
            triplets_index.from_triplet(common_relations.type_triplet(entity, type)),
        ]
    )


def _type_and_primitive_to_triplets(
    the_type: Optional[triplet.Element], primitive: primitives.Primitive
) -> Iterable[triplet.Triplet]:
    base = (
        common_relations.trigger_triplet(primitives.text(primitive), primitive),
        common_relations.display_triplet(primitives.text(primitive), primitive),
    )
    if the_type is None:
        return base
    return [
        *base,
        common_relations.type_triplet(primitives.text(primitive), the_type),
        *value_to_node(the_type).triplets,
    ]


def knowledge_graph_from_type_to_primitives_mapping(
    type_to_instance: Dict[Optional[triplet.Element], Tuple[primitives.Primitive, ...]]
) -> triplets_index.TripletsWithIndex:
    """`None` as key implies creating these nodes without a type."""
    return gamla.pipe(
        type_to_instance,
        gamla.graph_to_edges,
        gamla.mapcat(gamla.star(_type_and_primitive_to_triplets)),
        triplets_index.from_triplets,
    )


knowledge_graph_from_type_to_instance_mapping = gamla.compose_left(
    gamla.valmap(gamla.map(primitives.text_to_textual)),
    knowledge_graph_from_type_to_primitives_mapping,
)


@gamla.curry
def textual_association_map_to_graph(
    key_type: str, value_type: str, association_map: Dict[str, Iterable[str]]
) -> triplets_index.TripletsWithIndex:
    return gamla.pipe(
        association_map,
        gamla.graph_to_edges,
        gamla.map(
            gamla.star(
                build_graph_by_relation(
                    common_relations.ASSOCIATION, key_type, value_type
                )
            )
        ),
        transform.merge_graphs_nodes_by_id,
    )


@gamla.curry
def build_graph_by_relation(
    relation: triplet.Element,
    type1: triplet.Element,
    type2: triplet.Element,
    element1: str,
    element2: str,
) -> triplets_index.TripletsWithIndex:
    return transform.merge_graphs_nodes_by_id(
        [
            value_to_node(type1),
            value_to_node(type2),
            value_to_node(element1),
            value_to_node(element2),
            triplets_index.from_triplets(
                [
                    common_relations.type_triplet(element1, type1),
                    common_relations.type_triplet(element2, type2),
                    triplet.make_triplet(relation)(element1, element2),
                ]
            ),
        ]
    )


# TODO(uri): move to gamla?
deconstruct_dict_with_possibly_iterable_values = gamla.compose_left(
    gamla.valmap(
        gamla.ternary(
            gamla.anyjuxt(*map(gamla.is_instance, (tuple, list, set, frozenset))),
            gamla.identity,
            gamla.wrap_tuple,
        )
    ),
    gamla.graph_to_edges,
)


def _dict_to_graph(
    f: Callable[[triplet.Element, triplet.Element], triplet.Triplet]
) -> Callable[[Dict], triplets_index.TripletsWithIndex]:
    return gamla.compose_left(
        gamla.graph_to_edges, gamla.map(f), triplets_index.from_triplets
    )


node_map_to_knowledge_graph = _dict_to_graph(
    gamla.star(common_relations.association_triplet)
)
from_type_to_instance = _dict_to_graph(
    gamla.compose_left(reversed, gamla.star(common_relations.type_triplet))
)

trigger_graph = gamla.compose_left(
    common_relations.trigger_triplet, triplets_index.from_triplet
)
association_graph = gamla.compose_left(
    common_relations.association_triplet, triplets_index.from_triplet
)
type_graph = gamla.compose_left(
    common_relations.type_triplet, triplets_index.from_triplet
)
display_graph = gamla.compose_left(
    common_relations.display_triplet, triplets_index.from_triplet
)
