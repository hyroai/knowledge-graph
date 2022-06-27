# flake8: noqa
from . import triplets_index

from .storage import (  # isort:skip
    Node,
    Nodes,
    load_to_kg,
    make_node_universal_id,
    node_id,
    to_json,
)

from .triplets_index import from_triplet, from_triplets, triplets  # isort:skip

from .minigraph_builders import *  # isort:skip
from .querying import *  # isort:skip
from .querying_raw import *  # isort:skip
from .common_relations import *  # isort:skip


from .transform import *  # isort:skip
from .triplet import (  # isort:skip
    Element,
    make_triplet,
    object,
    relation_equals,
    relation_in,
    relation,
    subject_object_pair,
    subject,
    subject_in,
    object_equals,
    object_in,
    transform_object,
    transform_subject,
    Triplet,
    association_object_splitter,
    type_subject_splitter,
    ElementSplitter,
)


TripletToTriplet = triplet.OneToOne
TripletToTriplets = triplet.OneToMany
PrimitiveToPrimitive = primitives.OneToOne
PrimitiveToPrimitives = primitives.OneToMany


KnowledgeGraph = triplets_index.TripletsWithIndex
EMPTY_GRAPH = triplets_index.from_triplets(())
