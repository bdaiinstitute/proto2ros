# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides utilities to work with Protobuf descriptors.

Many of these utilities trade in terms of paths and locations.

Paths are sequences of numbers that refer to an arbitrarily nested value in a Protobuf message.
Each part of a path is one or two numbers: the field number if it is not a repeated field, and
the field number and item index if it is. For example, ``[4, 1, 3]`` can be (but it ultimately
depends on the concrete Protobuf message type) a path to the third item of field number 1 of
the (sub)message that is field number 4 of the message this path applies to. This path can thus
be used to access the target value: take field number 4 of the message, it is a message itself;
then take field number 1 of this (sub)message, it is a repeated field; then take item 3.

Locations refer to portions of a .proto source file. Locations specify a path to the descriptors
of the constructs that are defined in the corresponding portion. See
[``SourceCodeInfo``](https://github.com/protocolbuffers/protobuf/blob/main/benchmarks/descriptor.proto#L710)
message description for further reference.
"""

import itertools
from collections.abc import Sequence
from typing import Any, Dict, Iterable, Optional, Tuple

from google.protobuf.descriptor_pb2 import FieldDescriptorProto, FileDescriptorProto, SourceCodeInfo

from proto2ros.utilities import identity_lru_cache


@identity_lru_cache()
def index_source_code_locations(file_descriptor: FileDescriptorProto) -> Dict[Tuple[int, ...], SourceCodeInfo.Location]:
    """Indexes all source code locations in a source file descriptor by path."""
    info = file_descriptor.source_code_info
    return {tuple(location.path): location for location in info.location}


def walk(proto: Any, path: Sequence[int]) -> Iterable[Any]:
    """Iterates a Protobuf message down a given path.

    Args:
        proto: a Protobuf message instance to visit.
        path: path to iterate along.

    Returns:
        an iterable over Protobuf message members.
    """
    field_descriptor, field_value = next(item for item in proto.ListFields() if item[0].number == path[0])
    if field_descriptor.label == field_descriptor.LABEL_REPEATED:
        field_value = field_value[path[1]]
        path = path[1:]
    yield field_value
    if len(path) > 1:
        yield from walk(field_value, path[1:])


def locate_repeated(member: str, proto: Any) -> Iterable[Tuple[Sequence[int], Any]]:
    """Iterates over items of a repeated Protobuf message member, also yield their local paths.

    Local paths are tuples of member field number and item index.

    Args:
        member: name of the repeated message member field.
        proto: Protobuf message instance to access.

    Returns:
        an iterable over tuples of local path and member field value.
    """
    if member not in proto.DESCRIPTOR.fields_by_name:
        raise ValueError(f"{member} is not a member of the given protobuf")
    member_field_descriptor = proto.DESCRIPTOR.fields_by_name[member]
    if member_field_descriptor.label != FieldDescriptorProto.LABEL_REPEATED:
        raise ValueError(f"{member} is not a repeated member of the given protobuf")
    for i, member_item in enumerate(getattr(proto, member)):
        yield (member_field_descriptor.number, i), member_item


def resolve(
    source: FileDescriptorProto,
    path: Iterable[int],
    root: Optional[SourceCodeInfo.Location] = None,
) -> SourceCodeInfo.Location:
    """Resolves a source path to a location.

    Args:
        source: source file descriptor.
        path: source path to be resolved.
        root: optional root location to resolve against.

    Returns:
        resolved location.
    """
    locations = index_source_code_locations(source)
    if root is not None:
        path = itertools.chain(root.path, path)
    path = tuple(path)
    if path not in locations:
        location = SourceCodeInfo.Location()
        location.path.extend(path)
        return location
    return locations[path]


def protofqn(source: FileDescriptorProto, location: SourceCodeInfo.Location) -> str:
    """Returns the fully qualified name of a Protobuf composite type.

    This type is to be found at a given `location` in a given `source` file.
    """
    name = ".".join(proto.name for proto in walk(source, location.path))
    return f"{source.package}.{name}"
