import pytest

from knowledge_graph import common_relations, triplets_index

APPLE = "apple"
ORANGE = "orange"
FRUIT = "fruit"
CHAIR = "chair"
TABLE = "table"


@pytest.fixture(scope="session")
def kg():
    return triplets_index.from_triplets(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
            common_relations.association_triplet(CHAIR, TABLE),
        ]
    )
