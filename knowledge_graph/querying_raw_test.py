from knowledge_graph import common_relations, conftest, querying_raw


def test_instances_of_type(kg):
    assert set(querying_raw.instances_of_type(conftest.FRUIT)(kg)) == {
        conftest.APPLE,
        conftest.ORANGE,
    }


def test_triplets_with_relation(kg):
    assert set(querying_raw.triplets_with_relation(common_relations.TYPE)(kg)) == {
        common_relations.type_triplet(conftest.APPLE, conftest.FRUIT),
        common_relations.type_triplet(conftest.ORANGE, conftest.FRUIT),
    }


def test_triplets_with_relations(kg):
    assert set(
        querying_raw.triplets_with_relations(
            [common_relations.TYPE, common_relations.ASSOCIATION]
        )(kg)
    ) == {
        common_relations.type_triplet(conftest.APPLE, conftest.FRUIT),
        common_relations.type_triplet(conftest.ORANGE, conftest.FRUIT),
        common_relations.association_triplet(conftest.CHAIR, conftest.TABLE),
    }


def test_neighbors(kg):
    assert querying_raw.neighbors(
        common_relations.TYPE, kg, conftest.APPLE
    ) == frozenset([conftest.FRUIT])


def test_neighbors_doesnt_exist(kg):
    assert (
        querying_raw.neighbors(common_relations.TYPE, kg, conftest.CHAIR) == frozenset()
    )
