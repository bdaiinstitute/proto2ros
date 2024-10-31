# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides various utilities used across the proto2ros package."""

import collections
import functools
import itertools
import keyword
from typing import Any, Callable, Iterable, Optional, Tuple, Union

from rosidl_adapter.parser import BaseType, Type


def identity_lru_cache(maxsize: int = 128) -> Callable[[Callable], Callable]:
    """A `functools.lru_cache` equivalent that uses objects' id() for result caching."""

    def _decorator(user_function: Callable) -> Callable:
        cache: collections.OrderedDict = collections.OrderedDict()

        @functools.wraps(user_function)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal cache
            if len(cache) + 1 >= maxsize:
                cache.popitem(last=False)
            key = (tuple(id(arg) for arg in args), tuple((key, id(value)) for key, value in kwargs.items()))
            if key not in cache:
                cache[key] = user_function(*args, **kwargs)
            return cache[key]

        return _wrapper

    return _decorator


def fqn(obj: Any) -> Optional[str]:
    """Computes the fully qualified name of a given object, if any."""
    if not hasattr(obj, "__qualname__"):
        return None
    name = obj.__qualname__
    if not hasattr(obj, "__module__"):
        return name
    module = obj.__module__
    return f"{module}.{name}"


def pairwise(iterable: Iterable[Any]) -> Iterable[Tuple[Any, Any]]:
    """Yields an iterable over consecutive pairs."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def rreplace(s: str, old: str, new: str, count: int) -> str:
    """Replaces a number of string occurrences in reverse."""
    return s[::-1].replace(old[::-1], new[::-1], count)[::-1]


def to_ros_base_type(type_: Union[str, BaseType]) -> str:
    """Returns base type name for a given ROS type."""
    return BaseType.__str__(Type(str(type_)))


PYTHON_RESERVED_KEYWORD_SET = set(keyword.kwlist)
CPP_RESERVED_KEYWORD_SET = {
    "NULL",
    "alignas",
    "alignof",
    "and",
    "and_eq",
    "asm",
    "assert",
    "auto",
    "bitand",
    "bitor",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    "class",
    "compl",
    "const",
    "constexpr",
    "const_cast",
    "continue",
    "decltype",
    "default",
    "delete",
    "do",
    "double",
    "dynamic_cast",
    "else",
    "enum",
    "explicit",
    "export",
    "extern",
    "false",
    "float",
    "for",
    "friend",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "mutable",
    "namespace",
    "new",
    "noexcept",
    "not",
    "not_eq",
    "nullptr",
    "operator",
    "or",
    "or_eq",
    "private",
    "protected",
    "public",
    "register",
    "reinterpret_cast",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "static_assert",
    "static_cast",
    "struct",
    "switch",
    "template",
    "this",
    "thread_local",
    "throw",
    "true",
    "try",
    "typedef",
    "typeid",
    "typename",
    "union",
    "unsigned",
    "using",
    "virtual",
    "void",
    "volatile",
    "wchar_t",
    "while",
    "xor",
    "xor_eq",
    "char8_t",
    "char16_t",
    "char32_t",
    "concept",
    "consteval",
    "constinit",
    "co_await",
    "co_return",
    "co_yield",
    "requires",
}
RESERVED_KEYWORD_SET = PYTHON_RESERVED_KEYWORD_SET | CPP_RESERVED_KEYWORD_SET


def to_protobuf_field_name(name: str) -> str:
    """Transform a given name to be a valid Protobuf message field name."""
    if name in RESERVED_KEYWORD_SET:
        return name + "_"
    return name


def to_ros_field_name(name: str) -> str:
    """Transform a given name to be a valid ROS message field name."""
    name = name.lower()
    if name in RESERVED_KEYWORD_SET:
        name = name + "_field"
    return name
