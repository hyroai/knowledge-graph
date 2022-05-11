## Setup

Install knowledge-graph using these commands:

```
git clone https://github.com/hyroai/knowledge-graph.git
pip install -e ./knowledge-graph
pip install cloud-utils@https://github.com/hyroai/cloud-utils/tarball/master
```

## Publish to PyPI

In order to publish a new version to PyPI you need to release a new version on github with semantic version that follows the rules here: https://semver.org/

## When to use `querying.py` vs `querying_raw.py`

Both modules provide querying abilities, but `querying.py` relies on a global store of kgs, storred by their hash value. The code retrieves the kg instance from this map ad hoc. This was built so we can have a serializable representation of a node in the kg, `Node`, which has `graph_id` and `node_id`, and not have to serialize the entire kg any time we serialize an object containing them (e.g. if we're serializing or hashing a `NounPhrase` for some reason).

The global store is an impure component that can make some code have different behaviours depending on what happened before (whether or not the kg was loaded).

Consequently, in contexts where you have a `Element` and `KnowledgeGraph`, prefer using `querying_raw.py`, giving the graph instance explicitly. This is mainly when creating graphs or enriching them.

In contexts where all you have is `Node`, use `querying.py`.

If you implement new querying functions, you can implement them in `querying_raw.py`, and lift them to `querying.py` using `storage.run_on_kg_and_node`.

## Do not use the internal modules inside the `knowledge_graph` directory

Instead, rely on the imports in `knowledge_graph/__init__.py`, possibly add what you need there (in rare cases this is required).

## Relations naming conventions

Relation are the middle part of the triplet. Although they can safely be named anything, we use a naming convention that serves as mnemonic device. For example the relation `person/gender` implies the left hand side is an entity representing a person, whereas the right hand side is a gender, so we can expect a triplet like `Alice,person/gender,female`.
