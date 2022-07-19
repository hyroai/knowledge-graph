from typing import Callable

import gamla

from . import primitives, triplet

ASSOCIATION = "concept/association"
TYPE = "concept/type"
TRIGGER = "concept/trigger"
DISPLAY = "concept/display"
MIN = "range/min"
MAX = "range/max"
SUBSPECIALTY_SPECIALTY = "subspecialty/specialty"

COMMON_RELATIONS = frozenset({ASSOCIATION, TYPE, TRIGGER, DISPLAY, MIN, MAX})

CONCEPT_ACTION = "concept/action"
ACTION_TEXT = "action/text"
ACTION_SUGGESTIONS = "action/suggestions"
AGENT_ORDER = "agent/order"
GOAL_COMBINE = "goal/combine"
GOAL_MISUNDERSTANDINGS = "goal/misunderstandings"
# TODO(jonathanschwartz): change relation to action/switch_commands to have ordered switch commands
ACTION_SWITCH_COMMAND = "action/switch_command"
ACTION_EXPLICIT_CONTEXT_DROP = "action/explicit_context_drop"
ACTION_EVENT = "action/event"
SWITCH_COMMAND_TYPE = "switch_command/type"
SWITCH_COMMAND_DATA = "switch_command/data"
SUGGESTION_TEXT = "suggestion/display_text"
EVENT_DATA = "event/data"
EVENT_TYPE = "event/type"
ACTION_TEXT_VALIDATION = "action/text_validation"
CONCEPT_DISPLAY = "concept/display"
ACTION_APPENDABLE_SIDE = "action/appendable_side"
SUGGESTION_SAY_TEXT = "suggestion/say_text"
SUGGESTION_URL = "suggestion/url"
SUGGESTION_PHONE = "suggestion/phone"
CONDITION_ALL = "condition/all"
CONDITION_ANY = "condition/any"
PRIORITY_GROUP_RELATION = "concept/priority_group"
LOCATION_CONTEXT_SEARCH_RADIUS = "location_context/search_radius"
LOCATION_CONTEXT_SOUTHWEST_LONGITUDE = "location_context/southwest_longitude"
LOCATION_CONTEXT_SOUTHWEST_LATITUDE = "location_context/southwest_latitude"
LOCATION_CONTEXT_NORTHEAST_LONGITUDE = "location_context/northeast_longitude"
LOCATION_CONTEXT_NORTHEAST_LATITUDE = "location_context/northeast_latitude"
ATTRIBUTE_NAME = "attribute/name"
ATTRIBUTE_TEMPLATE = "attribute/template"
ATTRIBUTE_CUSTOMIZED = "attribute/customized_code"
DATA_SOURCE_FILE_HASH = "data_source/file_hash"
RENDER_TITLE = "render/title"
RENDER_TEXT = "render/text"
RENDER_TAGS = "render/tags"
RENDER_SUGGESTIONS = "render/suggestions"
RENDER_CTA_TEXT = "render/cta_text"
RENDER_RAW_TEXT = "render element/raw text"
RENDER_DATA_FIELD = "render element/data field"
DO_MANDATORY = "do/mandatory"
DO_OPTIONAL = "do/optional"
FUNCTION_MANDATORY = "function/mandatory"
FUNCTION_OPTIONAL = "function/optional"
AGENT_MISUNDERSTANDINGS = "agent/misunderstandings"
FUNCTION_PARAMETERS = "function/parameters"
QUESTION_REQUIREMENTS = "question/requirements"
CONDITION_COMPLEMENT = "condition/complement"
QUESTION_ACTION = "question/action"
QUESTION_LISTENER = "question/listener"
LISTENER_CONCEPT = "listener/concepts"
LISTENER_TYPE = "listener/type"
DO_CONDITION = "do/condition"
DO_MULTIPLE = "do/multiple"
GOAL_CONDITION = "goal/condition"
GOAL_DO = "goal/do"
CONDITION_GREATER_THAN = "condition/gt"
CONDITION_LOWER_THAN = "condition/lt"
CONDITION_QUESTION = "condition/question"
CONDITION_IS_TRUE = "condition/is_true"
DO_REQUEST = "do/request"
REQUEST_KEY_VALUE = "request/key_value"
PHONE_SOURCE = "phone/source"
CONDITION_IS_EVENT_TYPE = "condition/is_event_type"
CONDITION_IS_CONCEPT_TYPE = "condition/is_concept_type"
CONDITION_IS_ELEMENT_TYPE = "condition/is_element_type"
CONDITION_CONCEPT_EQUALS = "condition/concept_equals"
MODULE_PATH = "module/path"
ORDER_GOAL = "order/goal"
ORDER_PRIORITY = "order/priority"
DO_IMPLEMENTATION = "do/implementation"
FUNCTION_IMPLEMENTATION = "function/implementation"
IMPLEMENTATION_MODULE = "implementation/module"
IMPLEMENTATION_NAME = "implementation/name"
REQUIREMENT_KEY = "requirement/key"
REQUIREMENT_VALUE = "requirement/value"
BOT_MEDIUM = "bot/medium"
BOT_VERTICAL = "bot/vertical"
DO_PARAMETERS = "do/parameters"

display_triplet = triplet.make_triplet(DISPLAY)
trigger_triplet = triplet.make_triplet(TRIGGER)
association_triplet = triplet.make_triplet(ASSOCIATION)
type_triplet = triplet.make_triplet(TYPE)


def split_trigger_or_display(
    splitter: triplet.ElementSplitter,
) -> Callable[[triplet.Triplet], triplet.OneToMany]:
    return gamla.compose_left(
        triplet.subject,
        splitter,
        gamla.map(
            lambda new_node: gamla.compose_left(
                triplet.transform_object(
                    gamla.just(primitives.text_to_textual(new_node))
                ),
                triplet.transform_subject(gamla.just(new_node)),
            )
        ),
        gamla.star(gamla.juxt),
    )
