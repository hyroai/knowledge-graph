import random
import timeit

import gamla  # noqa

from knowledge_graph import common_relations, transform, triplets_index

APPLE = "apple"
ORANGE = "orange"
FRUIT = "fruit"


def test_merge_graphs_nodes_by_id():
    kg1 = triplets_index.from_triplet(common_relations.type_triplet(APPLE, FRUIT))
    kg2 = triplets_index.from_triplet(common_relations.type_triplet(ORANGE, FRUIT))
    assert transform.merge_graphs_nodes_by_id(
        [kg1, kg2]
    ) == triplets_index.from_triplets(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
        ]
    )


def test_merge_graphs_nodes_by_id_performance():
    kg_a = triplets_index.from_triplets(_random_triplets(0, 40000, 300, 20000))
    kg_b = triplets_index.from_triplets(_random_triplets(1, 40000, 300, 20000))
    print(len(kg_a.triplets))
    # Make sure merge implementation is better than just concatenating the triplets.
    merge_by_id_time = timeit.timeit(
        "transform.merge_graphs_nodes_by_id",
        setup="graphs = [kg_a, kg_b]",
        globals=locals() | globals(),
    )
    simple_concat_time = timeit.timeit(
        "lambda graphs: gamla.pipe(graphs, gamla.mapcat(triplets_index.triplets), triplets_index.from_triplets)",
        setup="graphs = [kg_a, kg_b]",
        globals=locals() | globals(),
    )
    assert merge_by_id_time < simple_concat_time


def _random_triplets(seed, n_instances_p, n_types_p, n_edges):
    r = random.Random(seed)
    return [
        (
            common_relations.type_triplet(
                r.choice(range(n_instances_p)), r.choice(range(n_types_p))
            )
        )
        for _ in range(n_edges)
    ]
