from typing import Any, Callable, FrozenSet, Iterable, List

import gamla

from . import common_relations, primitives, storage, triplet, triplets_index


def has_neighbors_with_relation(relation: triplet.Element):
    return gamla.compose_left(
        triplets_index.retrieve(relation, triplets_index.object_relation_index),
        gamla.nonempty,
    )


@gamla.curry
def neighbors_reversed(
    relation: triplet.Element,
    graph: triplets_index.TripletsWithIndex,
    node: triplet.Element,
) -> FrozenSet[triplet.Element]:
    return gamla.pipe(
        triplets_index.retrieve(relation, triplets_index.object_relation_index)(
            graph, node
        ),
        gamla.map(triplet.subject),
        frozenset,
    )


@gamla.curry
def neighbors(
    relation: triplet.Element,
    graph: triplets_index.TripletsWithIndex,
    node: triplet.Element,
) -> FrozenSet[triplet.Element]:
    return gamla.pipe(
        triplets_index.retrieve(relation, triplets_index.subject_relation_index)(
            graph, node
        ),
        gamla.map(triplet.object),
        frozenset,
    )


@gamla.curry
def relations_reversed(
    graph: triplets_index.TripletsWithIndex, node: triplet.Element
) -> FrozenSet[triplet.Element]:
    return gamla.pipe(
        triplets_index.object_index(graph)(node),
        gamla.map(triplet.relation),
        gamla.unique,
        frozenset,
    )


def trigger_primitives_by_kind(
    kind: primitives.Kind,
) -> Callable[[triplets_index.TripletsWithIndex], Iterable[primitives.Primitive]]:
    return gamla.compose_left(
        _get_all_trigger_primitives,
        gamla.filter(primitives.kind_equals(kind)),
        gamla.unique,
    )


def triplets_with_relation(
    relation: triplet.Element,
) -> Callable[[triplets_index.TripletsWithIndex], Iterable[triplet.Triplet]]:
    return gamla.compose_left(triplets_index.relation_index, gamla.apply(relation))


triplets_with_relations: Callable[
    [Iterable[str]],
    Callable[[triplets_index.TripletsWithIndex], Iterable[triplet.Triplet]],
] = gamla.compose_left(
    gamla.map(triplets_with_relation),
    gamla.star(gamla.juxtcat),
)


_get_all_trigger_primitives: Callable[
    [triplets_index.TripletsWithIndex], Iterable[triplet.Element]
] = gamla.compose_left(
    triplets_with_relation(common_relations.TRIGGER), gamla.map(triplet.object)
)


get_all_trigger_textual_triplets: Callable[
    [triplets_index.TripletsWithIndex],
    Iterable[triplet.Triplet],
] = gamla.compose_left(
    triplets_with_relation(common_relations.TRIGGER),
    gamla.filter(
        gamla.compose_left(triplet.object, primitives.kind_equals(primitives.TEXTUAL))
    ),
)


get_all_trigger_textuals = gamla.compose_left(
    get_all_trigger_textual_triplets, gamla.map(triplet.object)
)


triggers_and_names_from_kg: Callable[
    [triplets_index.TripletsWithIndex], frozenset
] = gamla.compose_left(
    _get_all_trigger_primitives,
    gamla.filter(
        gamla.anyjuxt(
            primitives.kind_equals(primitives.TEXTUAL),
            primitives.kind_equals(primitives.NAME),
        )
    ),
    gamla.map(primitives.text),
)

nodes_with_triggers = gamla.compose_left(
    triplets_with_relation(common_relations.TRIGGER), gamla.map(triplet.subject)
)


is_type_node = gamla.compose_left(
    triplets_with_relation(common_relations.TYPE),
    gamla.map(triplet.object),
    frozenset,
    gamla.contains,
)


def entities_with_trigger(
    f: primitives.Predicate,
) -> Callable[[triplets_index.TripletsWithIndex], Iterable[triplet.Element]]:
    return gamla.compose_left(
        triplets_with_relation(common_relations.TRIGGER),
        gamla.filter(gamla.compose_left(triplet.object, f)),
        gamla.map(triplet.subject),
    )


def instances_of_type(
    type: triplet.Element,
) -> Callable[[triplets_index.TripletsWithIndex], Iterable[triplet.Element]]:
    return gamla.compose_left(
        triplets_index.object_relation_index,
        gamla.apply(type),
        gamla.apply(common_relations.TYPE),
        gamla.map(triplet.subject),
    )


def _neighbors_for_element_and_reversed_relation(
    element: triplet.Element, graph: triplets_index.TripletsWithIndex
) -> Callable[[triplet.Element], FrozenSet[triplet.Element]]:
    def neighbors_for_element_and_reversed_relation(
        relation: triplet.Element,
    ) -> FrozenSet[triplet.Element]:
        return neighbors_reversed(relation, graph, element)

    return neighbors_for_element_and_reversed_relation


def _find_unique_by_relation_custom_kind_and_primitive_search(
    relations: List[str], graph_hash: str
):
    def _find_unique_by_relation_custom_kind_and_primitive_search(
        primitive_search: Callable[[triplet.Element], Iterable[triplet.Element]],
        text: str,
    ) -> triplet.Element:
        result = gamla.pipe(relations, gamla.mapcat(primitive_search), frozenset)
        assert (
            len(result) == 1
        ), f"Found [{text}] {len(result)} times: [{result}] in graph {graph_hash}. Expected 1. Aborting."
        return gamla.head(result)

    return _find_unique_by_relation_custom_kind_and_primitive_search


@gamla.curry
def find_unique_by_trigger_or_display_text_custom_kind(
    kind: primitives.Kind, graph: triplets_index.TripletsWithIndex, text: str
) -> triplet.Element:
    return _find_unique_by_relation_custom_kind_and_primitive_search(
        [common_relations.TRIGGER, common_relations.DISPLAY],
        storage.get_graph_hash(graph),
    )(
        _neighbors_for_element_and_reversed_relation(
            primitives.kind_and_text_to_primitive(kind, text), graph
        ),
        text,
    )


@gamla.curry
def find_unique_by_trigger_or_display_text_custom_kind_ignore_capitalization(
    kind: primitives.Kind, graph: triplets_index.TripletsWithIndex, text: str
) -> triplet.Element:
    return _find_unique_by_relation_custom_kind_and_primitive_search(
        [common_relations.TRIGGER, common_relations.DISPLAY],
        storage.get_graph_hash(graph),
    )(
        _neighbors_for_element_and_reversed_relation_ignore_capitalization(
            kind, graph, text
        ),
        text,
    )


@gamla.curry
def find_unique_by_trigger_ignore_capitalization_custom_kind(
    kind: primitives.Kind, graph: triplets_index.TripletsWithIndex, text: str
) -> triplet.Element:
    return _find_unique_by_relation_custom_kind_and_primitive_search(
        [common_relations.TRIGGER], storage.get_graph_hash(graph)
    )(
        _neighbors_for_element_and_reversed_relation_ignore_capitalization(
            kind, graph, text
        ),
        text,
    )


def _neighbors_for_element_and_reversed_relation_ignore_capitalization(
    kind: str, graph: triplets_index.TripletsWithIndex, text: str
) -> Callable[[triplet.Element], Iterable[triplet.Element]]:
    return gamla.juxtcat(
        _neighbors_for_element_and_reversed_relation(
            primitives.kind_and_text_to_primitive(kind, gamla.capitalize(text)), graph
        ),
        _neighbors_for_element_and_reversed_relation(
            primitives.kind_and_text_to_primitive(kind, text[:1].lower() + text[1:]),
            graph,
        ),
    )


def find_by_trigger_ignore_capitalization_custom_kind(
    kind: str, graph: triplets_index.TripletsWithIndex, text: str
) -> FrozenSet[triplet.Element]:
    return gamla.pipe(
        common_relations.TRIGGER,
        _neighbors_for_element_and_reversed_relation_ignore_capitalization(
            kind, graph, text
        ),
        frozenset,
    )


find_unique_by_trigger_or_display_text = (
    find_unique_by_trigger_or_display_text_custom_kind(primitives.TEXTUAL)
)


def _text_adapter(f: Callable[[triplet.Element], Any]) -> Callable[[str], Any]:
    return lambda text: gamla.prepare_and_apply(
        lambda graph: f(find_unique_by_trigger_or_display_text(graph, text))
    )


instances_of_type_by_text = _text_adapter(instances_of_type)


def get_texts_of_textual_triggers_for_node(
    graph: triplets_index.TripletsWithIndex,
) -> Callable[[triplet.Element], Iterable[str]]:
    return gamla.compose_left(
        neighbors(common_relations.TRIGGER, graph),
        gamla.filter(primitives.kind_equals(primitives.TEXTUAL)),
        gamla.map(primitives.text),
    )


trigger_exists_in_kg = gamla.compose_left(
    get_texts_of_textual_triggers_for_node, gamla.after(gamla.nonempty)
)


@gamla.curry
def is_node_in_graph(graph: triplets_index.TripletsWithIndex, text: str):
    try:
        find_unique_by_trigger_or_display_text(graph, text),
    except AssertionError:
        return False
    return True
