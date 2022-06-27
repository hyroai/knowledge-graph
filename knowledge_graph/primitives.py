import datetime
import logging
import re
from typing import Callable, Iterable, Mapping, Optional

import gamla
import phonenumbers

URL = "url"
DATE = "date"
PHONE = "phone"
IDENTIFIER = "identifier"
LOCATION = "location"
NAME = "name"
TEXTUAL = "textual"
SIZE = "unit_size"
Kind = str

Primitive = Mapping

Predicate = Callable[[Primitive], bool]
OneToMany = Callable[[Primitive], Iterable[Primitive]]
OneToOne = Callable[[Primitive], Primitive]

kind = gamla.itemgetter("kind")
kind_equals = gamla.compose(gamla.before(kind), gamla.equals)
text = gamla.itemgetter("text")
coordinate = gamla.itemgetter("coordinate")
city_name = gamla.itemgetter("city_name")

ISO_8601_DATE_FORMAT = "%Y-%m-%d"
ISO_8601_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

_UNIT_NAMES = [
    "v",
    "w",
    "in.",
    "mm",
    "MAH",
    "hr.",
    "VAC",
    "KWH",
    "Hrs",
    "lumens",
    "a",
    "hz",
    "AWG",
    "AH",
    "K",
]
_UNIT_GROUP_NAME = "UNIT"


def _get_unit_match(text: str) -> str:
    match = re.match(
        f"^(([\\d]+(\\.[\\d]+)?)[\\s|x]*)+(?P<{_UNIT_GROUP_NAME}>{'|'.join(_UNIT_NAMES)})$",
        text,
        re.IGNORECASE,
    )
    if match is None:
        raise ValueError
    return match.group(_UNIT_GROUP_NAME)


def extract_float(text: str) -> Optional[float]:
    floats = re.findall("[\\d]+(?:\\.[\\d]+)?", text)
    if floats:
        return float(floats[0])
    return None


def parse_unit_size(text: str) -> str:
    try:
        return text[: text.index(_get_unit_match(text))].strip()
    except (TypeError, ValueError):
        return text


def _format_phone_number(
    number: str, country: str, format: phonenumbers.PhoneNumberFormat
) -> str:
    # Numbers with digits are not well formatted by the phonenumbers lib.
    if any(c.isalpha() for c in number):
        return number
    try:
        return phonenumbers.format_number(phonenumbers.parse(number, country), format)
    except phonenumbers.NumberParseException:
        return number


def to_str(value: Primitive) -> str:
    if kind(value) == PHONE:
        return _format_phone_number(
            text(value), "US", phonenumbers.PhoneNumberFormat.NATIONAL
        )
    return text(value)


def extract_number_value(value: Primitive) -> float:
    if kind(value) == SIZE:
        result = extract_float(parse_unit_size(text(value)))
        if result is None:
            logging.error(f"Bad graph text for size: {value}")
            return 0.0
        return result
    return float(text(value))


def get_date(value: Primitive) -> datetime.datetime:
    for date_format in (ISO_8601_DATE_FORMAT, ISO_8601_DATETIME_FORMAT, "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(text(value), date_format)
        except ValueError:
            continue
    raise ValueError


@gamla.curry
def kind_and_text_to_primitive(kind: Kind, text: str) -> Primitive:
    return gamla.frozendict({"text": text, "kind": kind})


text_to_textual = kind_and_text_to_primitive(TEXTUAL)
text_to_size = kind_and_text_to_primitive(SIZE)
text_to_identifier = kind_and_text_to_primitive(IDENTIFIER)
text_to_url = kind_and_text_to_primitive(URL)
text_to_name = kind_and_text_to_primitive(NAME)
