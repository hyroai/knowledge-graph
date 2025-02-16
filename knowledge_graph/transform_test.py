import timeit

import gamla  # noqa

from knowledge_graph import common_relations, transform, triplets_index

APPLE = "apple"
ORANGE = "orange"
FRUIT = "fruit"
COLOR = "color"
RED = "red"
YELLOW = "yellow"


def test_merge_graphs_nodes_by_id():
    kg1 = triplets_index.from_triplets(
        (
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.association_triplet(APPLE, RED),
            common_relations.type_triplet(RED, COLOR),
        )
    )
    kg2 = triplets_index.from_triplets(
        (
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.association_triplet(ORANGE, YELLOW),
            common_relations.type_triplet(YELLOW, COLOR),
        )
    )
    assert kg1.relation_index(common_relations.TYPE) == frozenset(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(RED, COLOR),
        ]
    )

    merged = transform.merge_graphs_nodes_by_id([kg1, kg2])
    assert merged == triplets_index.from_triplets(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.association_triplet(APPLE, RED),
            common_relations.association_triplet(ORANGE, YELLOW),
            common_relations.type_triplet(RED, COLOR),
            common_relations.type_triplet(YELLOW, COLOR),
        ]
    )

    # make sure merged indices are correct
    assert merged.subject_index(ORANGE) == frozenset(
        [
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.association_triplet(ORANGE, YELLOW),
        ]
    )
    assert merged.subject_index(APPLE) == frozenset(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.association_triplet(APPLE, RED),
        ]
    )
    assert merged.object_index(FRUIT) == frozenset(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
        ]
    )
    assert merged.object_index(COLOR) == frozenset(
        [
            common_relations.type_triplet(RED, COLOR),
            common_relations.type_triplet(YELLOW, COLOR),
        ]
    )
    assert merged.relation_index(common_relations.TYPE) == frozenset(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.type_triplet(RED, COLOR),
            common_relations.type_triplet(YELLOW, COLOR),
        ]
    )
    assert merged.subject_relation_index(APPLE)(common_relations.TYPE) == frozenset(
        [common_relations.type_triplet(APPLE, FRUIT)]
    )
    assert merged.subject_relation_index(ORANGE)(common_relations.TYPE) == frozenset(
        [common_relations.type_triplet(ORANGE, FRUIT)]
    )
    assert merged.object_relation_index(FRUIT)(common_relations.TYPE) == frozenset(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
        ]
    )
    assert merged.subject_relation_and_object_type_index(APPLE)(
        common_relations.ASSOCIATION
    )(COLOR) == frozenset([common_relations.association_triplet(APPLE, RED)])
    assert merged.subject_relation_and_object_type_index(ORANGE)(
        common_relations.ASSOCIATION
    )(COLOR) == frozenset([common_relations.association_triplet(ORANGE, YELLOW)])

    # make sure two merging a merged graph is the same as merging all three
    kg3 = triplets_index.from_triplets((common_relations.type_triplet("peach", FRUIT),))
    merged2 = transform.merge_graphs_nodes_by_id([merged, kg3])
    assert merged2 == triplets_index.from_triplets(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.association_triplet(APPLE, RED),
            common_relations.association_triplet(ORANGE, YELLOW),
            common_relations.type_triplet(RED, COLOR),
            common_relations.type_triplet(YELLOW, COLOR),
            common_relations.type_triplet("peach", FRUIT),
        ]
    )
    assert merged2.subject_index("peach") == frozenset(
        [common_relations.type_triplet("peach", FRUIT)]
    )
    assert merged2.object_index(FRUIT) == frozenset(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.type_triplet("peach", FRUIT),
        ]
    )
    assert merged2.relation_index(common_relations.TYPE) == frozenset(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.type_triplet(RED, COLOR),
            common_relations.type_triplet(YELLOW, COLOR),
            common_relations.type_triplet("peach", FRUIT),
        ]
    )
    assert merged2.relation_index("bla") == frozenset()

    # Make sure merge implementation is better than just concatenating the triplets.
    assert timeit.timeit(
        "transform.merge_graphs_nodes_by_id",
        setup="graphs = [kg1, kg2]",
        globals=globals() | locals(),
    ) < timeit.timeit(
        "lambda graphs: gamla.pipe(graphs, gamla.mapcat(triplets_index.triplets), triplets_index.from_triplets)",
        setup="graphs = [kg1, kg2]",
        globals=globals() | locals(),
    )
