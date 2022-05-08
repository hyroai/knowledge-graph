import pytest

from knowledge_graph import common_relations, querying_raw, triplets_index

_APPLE = "apple"
_ORANGE = "orange"
_FRUIT = "fruit"
_CHAIR = "chair"
_TABLE = "table"


@pytest.fixture(scope="module")
def kg():
    return triplets_index.from_triplets(
        [
            common_relations.type_triplet(_APPLE, _FRUIT),
            common_relations.type_triplet(_ORANGE, _FRUIT),
            common_relations.association_triplet(_CHAIR, _TABLE),
        ]
    )


def test_instances_of_type(kg):
    assert set(querying_raw.instances_of_type(_FRUIT)(kg)) == {_APPLE, _ORANGE}


def test_triplets_with_relation(kg):
    assert set(querying_raw.triplets_with_relation(common_relations.TYPE)(kg)) == {
        common_relations.type_triplet(_APPLE, _FRUIT),
        common_relations.type_triplet(_ORANGE, _FRUIT),
    }


def test_triplets_with_relations(kg):
    assert set(
        querying_raw.triplets_with_relations(
            [common_relations.TYPE, common_relations.ASSOCIATION]
        )(kg)
    ) == {
        common_relations.type_triplet(_APPLE, _FRUIT),
        common_relations.type_triplet(_ORANGE, _FRUIT),
        common_relations.association_triplet(_CHAIR, _TABLE),
    }
