import timeit

import gamla  # noqa

from knowledge_graph import common_relations, conftest, transform, triplets_index

conftest.APPLE = "conftest.APPLE"
conftest.ORANGE = "conftest.ORANGE"
conftest.FRUIT = "conftest.FRUIT"


def test_merge_graphs_nodes_by_id():
    kg1 = triplets_index.from_triplet(
        common_relations.type_triplet(conftest.APPLE, conftest.FRUIT)
    )
    kg2 = triplets_index.from_triplet(
        common_relations.type_triplet(conftest.ORANGE, conftest.FRUIT)
    )
    assert transform.merge_graphs_nodes_by_id(
        [kg1, kg2]
    ) == triplets_index.from_triplets(
        [
            common_relations.type_triplet(conftest.APPLE, conftest.FRUIT),
            common_relations.type_triplet(conftest.ORANGE, conftest.FRUIT),
        ]
    )
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
