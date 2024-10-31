# Copyright (c) 2024 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides APIs to write C++ conversion code."""

import os
import re
from typing import List, Optional, Tuple, Union

import inflection
import jinja2
from rosidl_adapter.parser import BaseType, MessageSpecification

from proto2ros.configuration import Configuration
from proto2ros.utilities import rreplace, to_protobuf_field_name, to_ros_base_type


def to_pb2_cpp_header(source_path: os.PathLike) -> str:
    """Returns the C++ header for a given Protobuf source file."""
    basename, _ = os.path.splitext(source_path)
    return basename + ".pb.h"


def itemize_cpp_identifier(identifier: str, prefix: Optional[str] = None) -> str:
    """Derives a loop variable identifier for its iterable variable identifier."""
    basename = identifier.rpartition(".")[-1]
    basename = basename.rpartition("->")[-1]
    basename = basename.partition("(")[0]
    if prefix and not basename.startswith(prefix):
        basename = prefix + basename
    if not basename.endswith("item"):
        return f"{basename}_item"
    return basename.removesuffix("item") + "subitem"


def to_ros_cpp_header(spec: MessageSpecification) -> str:
    """Returns the C++ header for a given ROS message specification."""
    basename = inflection.underscore(spec.base_type.type)
    return f"{spec.base_type.pkg_name}/msg/{basename}.hpp"


def to_ros_cpp_namespace(package_name: str) -> str:
    """Returns the C++ namespace for a given ROS message package."""
    return f"{package_name}::msg"


def to_ros_cpp_type(type_name: Union[str, BaseType]) -> str:
    """Returns the C++ class name for a given ROS message type."""
    package_name, _, name = str(type_name).rpartition("/")
    if not package_name:
        raise ValueError(f"no package name in {type_name}")
    if not name:
        raise ValueError(f"no message name in {type_name}")
    return f"{to_ros_cpp_namespace(package_name)}::{name}"


def to_pb2_cpp_type(type_name: str) -> str:
    """Returns the C++ class name for a given Protobuf message type."""
    return type_name.replace(".", "::")


def to_hungarian_notation(name: str) -> str:
    """Transforms the given valid C++ name to hungarian notation.

    E.g. some_name_of_mine translates to kSomeNameOfMine.
    """
    return "k" + inflection.camelize(re.sub(r"([0-9])([a-z])", r"\1_\2", name))


def dump_conversions_cpp_sources(
    package_name: str,
    message_specifications: List[MessageSpecification],
    known_message_specifications: List[MessageSpecification],
    config: Configuration,
) -> Tuple[str, str]:
    """Dumps the C++ sources for Protobuf <-> ROS conversion APIs.

    Args:
        package_name: name of the package that will host the APIs.
        message_specifications: annotated ROS message specifications,
        as derived from equivalence relations (see `proto2ros.equivalences`).
        known_message_specifications: all annotated ROS message specifications known,
        including those from dependencies. A superset of ``message_specifications``.
        config: a suitable configuration for the procedure.

    Returns:
        the conversion C++ header and source files' content, in that order.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("proto2ros.output"))
    env.globals["to_pb2_cpp_name"] = to_protobuf_field_name
    env.globals["itemize_cpp_identifier"] = itemize_cpp_identifier
    env.globals["to_ros_base_type"] = to_ros_base_type
    env.globals["rreplace"] = rreplace
    env.filters["as_ros_base_type"] = to_ros_base_type
    env.filters["as_ros_cpp_type"] = to_ros_cpp_type
    env.filters["as_pb2_cpp_type"] = to_pb2_cpp_type
    env.filters["as_pb2_cpp_name"] = to_protobuf_field_name
    env.filters["to_hungarian_notation"] = to_hungarian_notation
    env.filters["rreplace"] = rreplace
    cpp_conversions_header_template = env.get_template("conversions.hpp.jinja")
    cpp_conversions_header_content = cpp_conversions_header_template.render(
        package_name=package_name,
        message_specifications=message_specifications,
        config=config,
    )
    cpp_conversions_source_template = env.get_template("conversions.cpp.jinja")
    cpp_conversions_source_content = cpp_conversions_source_template.render(
        package_name=package_name,
        message_specifications=message_specifications,
        known_message_specifications={str(spec.base_type): spec for spec in known_message_specifications},
        config=config,
    )
    return cpp_conversions_header_content, cpp_conversions_source_content
