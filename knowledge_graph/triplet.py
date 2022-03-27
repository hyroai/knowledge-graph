from typing import Callable, Hashable, Iterable, Tuple

import gamla

Element = Hashable
ElementOneToMany = Callable[[Element], Iterable[Element]]
Triplet = Tuple[Element, Element, Element]
OneToOne = Callable[[Triplet], Triplet]
OneToMany = Callable[[Triplet], Iterable[Triplet]]
Predicate = Callable[[Element], bool]

_SUBJECT_POSITION = 0
_RELATION_POSITION = 1
_OBJECT_POSITION = 2


def make_triplet(relation: Element) -> Callable[[Element, Element], Triplet]:
    def make_triplet(subject: Element, obj: Element):
        return (subject, relation, obj)

    return make_triplet


_position = gamla.nth

subject = _position(_SUBJECT_POSITION)
relation = _position(_RELATION_POSITION)
object = _position(_OBJECT_POSITION)

subject_object_pair = gamla.juxt(subject, object)

subject_equals = gamla.compose(gamla.before(subject), gamla.equals)
subject_in = gamla.compose(gamla.before(subject), gamla.contains)
relation_equals = gamla.compose(gamla.before(relation), gamla.equals)
relation_in = gamla.compose(gamla.before(relation), gamla.contains)
object_equals = gamla.compose(gamla.before(object), gamla.equals)
object_in = gamla.compose(gamla.before(object), gamla.contains)


@gamla.curry
def _transform_position(i: int, f: Callable):
    change_by_position = [gamla.identity, gamla.identity, gamla.identity]
    change_by_position[i] = f
    return gamla.stack(change_by_position)


transform_subject = _transform_position(_SUBJECT_POSITION)
transform_object = _transform_position(_OBJECT_POSITION)
transform_relation = _transform_position(_RELATION_POSITION)


ElementSplitter = Callable[[Element], Tuple[Element, ...]]


@gamla.curry
def _triplet_splitter(
    position, splitter: ElementSplitter
) -> Callable[[Triplet], OneToMany]:
    return gamla.compose_left(
        _position(position),
        splitter,
        gamla.map(gamla.compose(_transform_position(position), gamla.just)),
        gamla.star(gamla.juxt),
    )


type_subject_splitter = _triplet_splitter(_SUBJECT_POSITION)
association_object_splitter = _triplet_splitter(_OBJECT_POSITION)
