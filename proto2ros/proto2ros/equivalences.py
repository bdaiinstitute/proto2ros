# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides APIs to extract Protobuf <-> ROS message equivalences.

These equivalences are defined in terms of Protobuf composite descriptors
and ROS message specifications. See Protobuf descriptor messages and ROS 2
``MessageSpecification`` class definition and documentation in
https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/descriptor.proto
and https://github.com/ros2/rosidl/blob/rolling/rosidl_adapter/rosidl_adapter/parser.py
respectively for further reference.
"""

import dataclasses
import functools
import math
from collections.abc import Sequence
from typing import Any, Iterable, List, Optional, Set, Union

import inflection
from google.protobuf.descriptor_pb2 import (
    DescriptorProto,
    EnumDescriptorProto,
    FieldDescriptorProto,
    FileDescriptorProto,
    SourceCodeInfo,
)
from rosidl_adapter.parser import Constant, Field, MessageSpecification, Type

from proto2ros.configuration import Configuration
from proto2ros.descriptors.types import COMPOSITE_TYPES, PRIMITIVE_TYPE_NAMES
from proto2ros.descriptors.utilities import locate_repeated, protofqn, resolve, walk
from proto2ros.utilities import to_ros_base_type, to_ros_field_name


@dataclasses.dataclass
class Equivalence:
    """An equivalence relation between a Protobuf composite (message or enum) and a ROS message.

    More than one ROS message specification may be required to represent a single Protobuf
    composite. Auxiliary message specifications may be listed in that case.

    Attributes:
        proto_spec: a Protobuf composite type descriptor (either a message or an enum).
        message_spec: an equivalent ROS message specification.
        auxiliary_message_specs: additional ROS message specifications necessary to define
        an equivalence (e.g. one-of equivalents, enum equivalents, etc.).
    """

    proto_spec: Union[DescriptorProto, EnumDescriptorProto]
    message_spec: MessageSpecification
    auxiliary_message_specs: Optional[Sequence[MessageSpecification]] = None


def all_message_specifications(eqs: List[Equivalence]) -> Iterable[MessageSpecification]:
    """Yields all message specifications to be found in the given equivalence relations."""
    for eq in eqs:
        yield eq.message_spec
        if eq.auxiliary_message_specs:
            yield from eq.auxiliary_message_specs


def equivalent_ros_name(source: FileDescriptorProto, location: SourceCodeInfo.Location) -> str:
    """Returns an equivalent ROS message name for a Protobuf composite type in a given location."""
    return "".join(inflection.camelize(proto.name) for proto in walk(source, location.path))


def extract_leading_comments(location: SourceCodeInfo.Location) -> str:
    """Returns leading comments for construct at the given location."""
    comments = [*location.leading_detached_comments, location.leading_comments]
    # Remove backslashes as it causes issues further down the line within rosidl.
    comments = [comment.strip("\n").replace("\\", "") for comment in comments]
    return "\n\n".join(comment for comment in comments if comment)


@functools.singledispatch
def compute_equivalence(
    descriptor: Any,
    source: FileDescriptorProto,
    location: SourceCodeInfo.Location,
    config: Configuration,
) -> Equivalence:
    """Computes a suitable equivalence relation for some Protobuf composite type.

    Note this function operates as the entrypoint to all corresponding overloads (via single dispatch).

    Args:
        descriptor: the descriptor of the Protobuf composite type of interest.
        source: the descriptor of the Protobuf source file where the Protobuf composite type is defined.
        location: the location of the Protobuf composite type in the aforementioned source file.
        config: a suitable configuration for the procedure.

    Returns:
        an equivalence relation.
    """
    raise NotImplementedError(f"not implemented for {descriptor}")


@compute_equivalence.register
def compute_equivalence_for_enum(
    descriptor: EnumDescriptorProto,
    source: FileDescriptorProto,
    location: SourceCodeInfo.Location,
    config: Configuration,
) -> Equivalence:
    """Computes a suitable equivalence relation for a Protobuf enum type.

    Args:
        descriptor: the descriptor of the Protobuf enum of interest.
        source: the descriptor of the Protobuf source file where the Protobuf enum type is defined.
        location: the location of the Protobuf enum type in the aforementioned source file.
        config: a suitable configuration for the procedure.

    Returns:
        an equivalence relation.
    """
    constants: List[Constant] = []
    for value_path, value_descriptor in locate_repeated("value", descriptor):
        constant = Constant("int32", value_descriptor.name.upper(), value_descriptor.number)
        value_location = resolve(source, value_path, location)
        leading_comments = extract_leading_comments(value_location)
        if leading_comments:
            constant.annotations["comment"] = leading_comments
        constants.append(constant)
    fields = [Field(Type("int32"), "value")]
    fields[-1].annotations["optional"] = False
    package_name = config.package_mapping[source.package]
    name = equivalent_ros_name(source, location)
    message_spec = MessageSpecification(package_name, name, fields, constants)
    leading_comments = extract_leading_comments(location)
    if leading_comments:
        message_spec.annotations["comment"] = leading_comments
    message_spec.annotations["proto-type"] = protofqn(source, location)
    message_spec.annotations["proto-class"] = "enum"
    return Equivalence(proto_spec=descriptor, message_spec=message_spec)


def translate_type_name(name: str, config: Configuration) -> str:
    """Translates a Protobuf type name to its ROS equivalent.

    Args:
        name: fully qualified Protobuf type name.
        config: a suitable configuration for the procedure.

    Returns:
        an fully qualified ROS message type name.

    Raises:
        ValueError: when `name` is not fully qualified or
        when it cannot be resolved to a ROS message type name.
    """
    if not name.startswith("."):
        raise ValueError(f"'{name}' is not a fully qualified type name")
    proto_type_name = name[1:]

    if proto_type_name == "google.protobuf.Any":
        return "proto2ros/AnyProto"

    if proto_type_name in config.message_mapping:
        return config.message_mapping[proto_type_name]

    matching_proto_packages = [
        proto_package for proto_package in config.package_mapping if proto_type_name.startswith(proto_package + ".")
    ]
    if matching_proto_packages:
        proto_package = max(matching_proto_packages, key=len)
        ros_package = config.package_mapping[proto_package]
        proto_type_name = proto_type_name.removeprefix(proto_package + ".")
        ros_type_name = inflection.camelize(proto_type_name.replace(".", "_"))
        return f"{ros_package}/{ros_type_name}"

    if not config.passthrough_unknown:
        raise ValueError(f"cannot resolve '{name}' type name")
    return "proto2ros/AnyProto"


PRIMITIVE_TYPES_MAPPING = {
    "bool": "bool",
    "double": "float64",
    "fixed32": "uint32",
    "fixed64": "uint64",
    "float": "float32",
    "int32": "int32",
    "int64": "int64",
    "sfixed32": "int32",
    "sfixed64": "int64",
    "sint32": "int32",
    "sint64": "int64",
    "uint32": "uint32",
    "uint64": "uint64",
    "string": "string",
}


def translate_type(name: str, repeated: bool, config: Configuration) -> Type:
    """Translates a Protobuf type to its ROS equivalent.

    Args:
        name: Protobuf type name.
        repeated: whether the Protobuf type applies to a repeated field.
        config: a suitable configuration for the procedure.

    Returns:
        a ROS message type.
    """
    if name != "bytes":
        if name not in PRIMITIVE_TYPES_MAPPING:
            ros_type_name = translate_type_name(name, config)
        else:
            ros_type_name = PRIMITIVE_TYPES_MAPPING[name]
        if repeated:
            ros_type_name += "[]"
    else:
        ros_type_name = "proto2ros/Bytes[]" if repeated else "uint8[]"
    return Type(ros_type_name)


def translate_any_type(any_expansion: Union[Set[str], str], repeated: bool, config: Configuration) -> Type:
    """Translates a ``google.protobuf.Any`` type to its ROS equivalent given an any expansion.

    Args:
        any_expansion: a Protobuf message type set that the given ``google.protobuf.Any``
        is expected to pack. A single Protobuf message type may also be specified in lieu
        of a single element set. All Protobuf message types must be fully qualified.
        repeated: whether the Protobuf type applies to a repeated field.
        config: a suitable configuration for the procedure.

    Returns:
        a ROS message type.
    """
    if config.allow_any_casts and isinstance(any_expansion, str):
        # Type name is expected to be fully qualified, thus the leading dot. See
        # https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/descriptor.proto#L265-L270
        # for further reference.
        return translate_type(f".{any_expansion}", repeated, config)
    ros_type_name = "proto2ros/Any"
    if repeated:
        ros_type_name += "[]"
    return Type(ros_type_name)


def translate_field(
    descriptor: FieldDescriptorProto,
    source: FileDescriptorProto,
    location: SourceCodeInfo.Location,
    config: Configuration,
) -> Field:
    """Translates a Protobuf field descriptor to its ROS equivalent.

    Args:
        descriptor: a Protobuf field descriptor.
        source: the descriptor of the Protobuf source file where the Protobuf field is defined.
        location: the location of the Protobuf field in the aforementioned source file.
        config: a suitable configuration for the procedure.

    Returns:
        an fully qualified ROS message type name.

    Raises:
        ValueError: when the given field is of an unsupported or unknown type.
        ValueError: when an any expansion is specified for a fully typed field.
    """
    repeated = descriptor.label == FieldDescriptorProto.LABEL_REPEATED
    any_expansion = config.any_expansions.get(protofqn(source, location))
    if any_expansion:
        if descriptor.type_name != ".google.protobuf.Any":
            raise ValueError(f"any expansion specified for '{descriptor.name}' field of {descriptor.type_name} type")
        type_name = descriptor.type_name

        field_type = translate_any_type(any_expansion, repeated, config)
    else:
        if descriptor.type in PRIMITIVE_TYPE_NAMES:
            type_name = PRIMITIVE_TYPE_NAMES[descriptor.type]
        elif descriptor.type in COMPOSITE_TYPES:
            type_name = descriptor.type_name
        else:
            raise ValueError(f"unsupported field type: {descriptor.type}")
        field_type = translate_type(type_name, repeated, config)
    field = Field(field_type, to_ros_field_name(descriptor.name))
    if any_expansion:
        if not config.allow_any_casts or not isinstance(any_expansion, str):
            # Annotate field with paired Protobuf and ROS message type names,
            # so that any expansions can be resolved in conversion code.
            field.annotations["type-casts"] = [
                (proto_type, translate_type_name(f".{proto_type}", config)) for proto_type in any_expansion
            ]
        else:
            type_name = f".{any_expansion}"
            field.annotations["type-casted"] = True
    if source.syntax == "proto3":
        field.annotations["optional"] = descriptor.proto3_optional or (
            descriptor.label != FieldDescriptorProto.LABEL_REPEATED
            and descriptor.type == FieldDescriptorProto.TYPE_MESSAGE
        )
    elif source.syntax == "proto2":
        field.annotations["optional"] = descriptor.label != FieldDescriptorProto.LABEL_REPEATED
    else:
        raise ValueError(f"unknown proto syntax: {source.syntax}")
    field.annotations["proto-cpp-name"] = descriptor.name.lower()
    field.annotations["proto-py-name"] = descriptor.name
    ros_type_name = to_ros_base_type(field_type)
    if type_name != ".google.protobuf.Any" and ros_type_name == "proto2ros/AnyProto":
        type_name = "some"
    field.annotations["proto-type"] = type_name.strip(".")
    leading_comments = extract_leading_comments(location)
    if leading_comments:
        field.annotations["comment"] = leading_comments
    field.annotations["deprecated"] = descriptor.options.deprecated
    return field


@compute_equivalence.register
def compute_equivalence_for_message(
    descriptor: DescriptorProto,
    source: FileDescriptorProto,
    location: SourceCodeInfo.Location,
    config: Configuration,
) -> Equivalence:
    """Computes a suitable equivalence relation for a Protobuf message type.

    Currently, this function supports optional, repeated, and oneof fields of primitive, enum,
    map, message, and `google.protobuf.Any` type. Recursive or cyclic type dependencies may ensue
    if these are present in the Protobuf message type (see `proto2ros.dependencies` on how to cope
    with this).

    Args:
        descriptor: the descriptor of the Protobuf message of interest.
        source: the descriptor of the Protobuf source file where the Protobuf message is defined.
        location: the location of the Protobuf message in the aforementioned source file.
        config: a suitable configuration for the procedure.

    Returns:
        an equivalence relation.

    Raises:
        ValueError: when there are too many fields (more than 64) and
        their availability cannot be encoded in the equivalent ROS message.
    """
    ros_package_name = config.package_mapping[source.package]
    name = equivalent_ros_name(source, location)
    auxiliary_message_specs: List[MessageSpecification] = []

    fields: List[Field] = []
    constants: List[Constant] = []
    oneof_field_sets: List[List[Field]] = [list() for _ in descriptor.oneof_decl]

    if not descriptor.options.map_entry:
        if len(descriptor.field) > 0:
            options_mask_size = max(2 ** math.ceil(math.log2(len(descriptor.field))), 8)
            if options_mask_size > 64:
                raise ValueError("too many fields (> 64)")
            options_mask_type = Type(f"uint{options_mask_size}")

        # Iterate over all message fields, as listed by the given descriptor. See
        # https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/descriptor.proto#L127
        # for further reference.
        for i, (field_path, field_descriptor) in enumerate(locate_repeated("field", descriptor)):
            if field_descriptor.options.deprecated and config.drop_deprecated:
                continue

            field_location = resolve(source, field_path, location)
            field = translate_field(field_descriptor, source, field_location, config)
            if field_descriptor.HasField("oneof_index"):
                oneof_field_sets[field_descriptor.oneof_index].append(field)
                continue

            if field.annotations["optional"]:
                mask_name = field.name.upper() + "_FIELD_SET"
                mask_constant = Constant(str(options_mask_type), mask_name, 1 << i)
                constants.append(mask_constant)
            fields.append(field)

        for (oneof_path, oneof_decl), oneof_fields in zip(
            locate_repeated("oneof_decl", descriptor),
            oneof_field_sets,
            strict=True,
        ):
            oneof_name = inflection.underscore(oneof_decl.name)
            oneof_type_name = inflection.camelize(f"{name}_one_of_{oneof_name}")
            oneof_type = Type(f"{ros_package_name}/{oneof_type_name}")

            oneof_constants: List[Constant] = []
            oneof_constants.append(Constant("int8", f"{oneof_name}_not_set".upper(), 0))
            for i, field in enumerate(oneof_fields, start=1):
                tag_name = f"{oneof_name}_{field.name}_set".upper()
                oneof_constants.append(Constant("int8", tag_name, i))
            choice_field = Field(Type("int8"), f"{oneof_name}_choice")
            choice_field.annotations["deprecated"] = True
            oneof_fields.append(choice_field)
            which_field = Field(Type("int8"), "which")
            which_field.annotations["alias"] = choice_field.name
            oneof_fields.append(which_field)

            oneof_message_spec = MessageSpecification(
                oneof_type.pkg_name,
                oneof_type.type,
                oneof_fields,
                oneof_constants,
            )
            oneof_message_spec.annotations["proto-type"] = protofqn(source, location) + f"[one-of {oneof_decl.name}]"
            oneof_message_spec.annotations["proto-class"] = "one-of"
            oneof_message_spec.annotations["tagged"] = list(zip(oneof_constants[1:], oneof_fields[:-2], strict=True))
            oneof_message_spec.annotations["tag"] = which_field
            auxiliary_message_specs.append(oneof_message_spec)

            field = Field(oneof_type, oneof_name)
            # oneof wrapper field cannot itself be optional
            field.annotations["optional"] = False
            field.annotations["proto-cpp-name"] = oneof_decl.name
            field.annotations["proto-py-name"] = oneof_decl.name
            oneof_location = resolve(source, oneof_path, location)
            leading_comments = extract_leading_comments(oneof_location)
            if leading_comments:
                field.annotations["comment"] = leading_comments
            fields.append(field)

        if len(constants) > 0:
            field = Field(options_mask_type, "has_field", 2**options_mask_size - 1)
            field.annotations["optional"] = False  # field presence mask must always be present
            fields.append(field)
    else:
        for field_path, field_descriptor in locate_repeated("field", descriptor):
            if field_descriptor.options.deprecated and config.drop_deprecated:
                continue
            field_location = resolve(source, field_path, location)
            field = translate_field(field_descriptor, source, field_location, config)
            field.annotations["optional"] = False  # map key-value pairs must always be present
            if field.name == "value":
                map_inplace = field_descriptor.type == FieldDescriptorProto.TYPE_MESSAGE
            fields.append(field)

    message_spec = MessageSpecification(ros_package_name, name, fields, constants)
    leading_comments = extract_leading_comments(location)
    if leading_comments:
        message_spec.annotations["comment"] = leading_comments
    message_spec.annotations["proto-type"] = protofqn(source, location)
    message_spec.annotations["proto-class"] = "message"
    message_spec.annotations["has-optionals"] = len(constants) > 0
    message_spec.annotations["map-entry"] = descriptor.options.map_entry
    if descriptor.options.map_entry:
        message_spec.annotations["map-inplace"] = map_inplace
    for spec in auxiliary_message_specs:
        spec.annotations["parent-spec"] = message_spec
    return Equivalence(
        proto_spec=descriptor,
        message_spec=message_spec,
        auxiliary_message_specs=auxiliary_message_specs,
    )


@functools.singledispatch
def extract_equivalences(descriptor: Any, *args: Any) -> Iterable[Equivalence]:
    """Extracts equivalence relations for all Protobuf composite types in some Protobuf descriptor.

    Note this function operates as the entrypoint to all corresponding overloads (via single dispatch).

    Args:
        descriptor: the descriptor bearing Protobuf composite types.
        args: place holder for arguments

    Returns:
        an iterable over equivalence relations.
    """
    raise NotImplementedError(f"not implemented for {descriptor}")


@extract_equivalences.register
def extract_equivalences_from_message(
    message_descriptor: DescriptorProto,
    source_descriptor: FileDescriptorProto,
    location: SourceCodeInfo.Location,
    config: Configuration,
) -> Iterable[Equivalence]:
    """Extracts equivalence relations for a Protobuf message type and all nested composite types (if any).

    Args:
        message_descriptor: the descriptor of the Protobuf message of interest.
        source_descriptor: the descriptor of the Protobuf source file where the Protobuf message is defined.
        location: the location of the Protobuf message in the aforementioned source file.
        config: a suitable configuration for the procedure.

    Returns:
        an iterable over equivalence relations.
    """
    yield compute_equivalence_for_message(message_descriptor, source_descriptor, location, config)
    for enum_path, enum_descriptor in locate_repeated("enum_type", message_descriptor):
        enum_location = resolve(source_descriptor, enum_path, location)
        yield compute_equivalence_for_enum(enum_descriptor, source_descriptor, enum_location, config)
    for nested_path, nested_descriptor in locate_repeated("nested_type", message_descriptor):
        nested_location = resolve(source_descriptor, nested_path, location)
        if protofqn(source_descriptor, nested_location) in config.message_mapping:
            continue  # skip mapped messages
        yield from extract_equivalences_from_message(nested_descriptor, source_descriptor, nested_location, config)


@extract_equivalences.register
def extract_equivalences_from_source(
    source_descriptor: FileDescriptorProto,
    config: Configuration,
) -> Iterable[Equivalence]:
    """Extracts all equivalence relations from a Protobuf source descriptor.

    Args:
        source_descriptor: the descriptor of the Protobuf source file.
        config: a suitable configuration for the procedure.

    Returns:
        an iterable over equivalence relations.
    """
    for enum_path, enum_type in locate_repeated("enum_type", source_descriptor):
        enum_location = resolve(source_descriptor, enum_path)
        yield compute_equivalence_for_enum(enum_type, source_descriptor, enum_location, config)
    for message_path, message_type in locate_repeated("message_type", source_descriptor):
        message_location = resolve(source_descriptor, message_path)
        if protofqn(source_descriptor, message_location) in config.message_mapping:
            continue  # skip mapped messages
        yield from extract_equivalences_from_message(message_type, source_descriptor, message_location, config)
