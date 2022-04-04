import pytest

from knowledge_graph import common_relations, querying_raw, triplets_index

APPLE = "apple"
ORANGE = "orange"
FRUIT = "fruit"


@pytest.fixture(scope="module")
def kg():
    return triplets_index.from_triplets(
        [
            common_relations.type_triplet(APPLE, FRUIT),
            common_relations.type_triplet(ORANGE, FRUIT),
        ]
    )


def test_instances_of_type(kg):
    assert set(querying_raw.instances_of_type(FRUIT)(kg)) == {APPLE, ORANGE}


def test_triplets_with_relation(kg):
    assert set(querying_raw.triplets_with_relation(common_relations.TYPE)(kg)) == {
        common_relations.type_triplet(APPLE, FRUIT),
        common_relations.type_triplet(ORANGE, FRUIT),
    }
