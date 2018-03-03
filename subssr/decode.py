from base64 import urlsafe_b64decode
from collections import OrderedDict
from typing import Any, Dict, Tuple

from six.moves.urllib_parse import parse_qs, urlparse, ParseResult
from toolz import itemmap, valmap, first, memoize, merge
from toolz.functoolz import compose, curry, juxt

from subssr.download import load
from subssr.ssrconfig import BASE64_FIELDS, REQUIRED_FIELDS_POSITION


@memoize
def base64_part(s: str) -> str:
    return s.replace('ssr://', '', 1)


@memoize
def padding(s: str) -> str:
    return s + ('=' * (4 - (len(s) % 4)) if len(s) % 4 else '')


@memoize
def to_link(s: str) -> ParseResult:
    s = ('ssr://' if not s.startswith('ssr://') else '') + s
    return urlparse(s)


@memoize
def get_required_fields(link: ParseResult) -> Dict[str, str]:
    fields = link.netloc.split(':')
    return itemmap(
        lambda i: decode_field(i[0], fields[i[1]]),
        REQUIRED_FIELDS_POSITION,
        OrderedDict
    )


def get_required_field(fields: Dict[str, str], field: str) -> str:
    return fields[field]


@memoize
def required_fields_getter(link: ParseResult):
    return curry(
        get_required_field,
        get_required_fields(link)
    )


@memoize
def get_extra_params(link: ParseResult) -> Dict[str, str]:
    return itemmap(
        lambda i: decode_field(*i),
        valmap(first, parse_qs(link.query))
    )


def get_extra_param(params: Dict[str, str], field: str, default: Any = None):
    return params.get(field, default)


@memoize
def extra_param_getter(link: ParseResult):
    return curry(get_extra_param, get_extra_params(link))


@memoize
def decode_field(field: str, value: str) -> Tuple[str, str]:
    if value and field in BASE64_FIELDS:
        value = ssr_base64_decode(value)
    return field, value


ssr_base64_decode = compose(
    bytes.decode,
    urlsafe_b64decode,
    padding,
    base64_part
)
ssr_url_parse = compose(to_link, ssr_base64_decode)
ssr_required_fields = compose(get_required_fields, ssr_url_parse)
ssr_required_field_getter = compose(required_fields_getter, ssr_url_parse)
ssr_extra_params = compose(get_extra_params, ssr_url_parse)
ssr_extra_param_getter = compose(extra_param_getter, ssr_url_parse)


def ssr_config(s: str):
    return merge(
        *juxt(ssr_required_fields, ssr_extra_params)(s)
    )


def ssr_config_from_url(url: str):
    return map(
        ssr_config,
        filter(
            lambda s: s.startswith('ssr://'),
            ssr_base64_decode(load(url)).split()
        )
    )
