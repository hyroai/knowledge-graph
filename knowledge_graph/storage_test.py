import gamla

from knowledge_graph import storage


def test_serialize_and_load(kg):
    assert kg == gamla.pipe(kg, storage.to_json, storage.from_json)
