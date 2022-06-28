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
from .querying_raw import (  # isort:skip
    neighbors_reversed,
    neighbors,
    relations_reversed,
    trigger_primitives_by_kind,
    triplets_with_relation,
    triplets_with_relations,
    get_all_trigger_textual_triplets,
    get_all_trigger_textuals,
    triggers_and_names_from_kg,
    nodes_with_triggers,
    is_type_node,
    entities_with_trigger,
    instances_of_type,
    find_unique_by_trigger_or_display_text_custom_kind,
    find_unique_by_trigger_or_display_text,
    instances_of_type_by_text,
    get_texts_of_textual_triggers_for_node,
    trigger_exists_in_kg,
    is_node_in_graph,
)
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
    subject_equals,
    object_equals,
    object_in,
    transform_object,
    transform_subject,
    transform_relation,
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
