# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides APIs to write Python conversion code."""

import importlib
import os
import pickle
import sys
from typing import Any, Dict, Iterable, List, Optional, Union

import inflection
import jinja2
from google.protobuf.descriptor import Descriptor
from rosidl_adapter.parser import BaseType, MessageSpecification

from proto2ros.configuration import Configuration
from proto2ros.utilities import fqn, to_ros_base_type


def to_python_module_name(module_path: os.PathLike) -> str:
    """Returns a Python module name given its source file path."""
    basename, _ = os.path.splitext(module_path)
    return basename.replace("/", ".")


def to_python_identifier(string: str) -> str:
    """Transforms an arbitrary string into a valid Python identifier."""
    denormalized_identifier = string.replace("/", "_").replace(".", "_")
    denormalized_identifier = denormalized_identifier.replace("UInt", "uint")
    return inflection.underscore(denormalized_identifier)


def unqualify_python_identifier(identifier: str) -> str:
    """Extracts a Python identifier basename."""
    return identifier.rpartition(".")[-1]


def itemize_python_identifier(identifier: str, prefix: Optional[str] = None) -> str:
    """Derives a loop variable identifier for its iterable variable identifier."""
    basename = unqualify_python_identifier(identifier)
    if prefix and not basename.startswith(prefix):
        basename = prefix + basename
    if not basename.endswith("item"):
        return f"{basename}_item"
    return basename.removesuffix("item") + "subitem"


def to_ros_python_module_name(package_name: str) -> str:
    """Returns the Python module name for a given ROS message package."""
    return f"{package_name}.msg"


def to_ros_python_type(type_name: Union[str, BaseType]) -> str:
    """Returns the Python class name for a given ROS message type."""
    package_name, _, name = str(type_name).rpartition("/")
    if not package_name:
        raise ValueError(f"no package name in {type_name}")
    if not name:
        raise ValueError(f"no message name in {type_name}")
    return f"{to_ros_python_module_name(package_name)}.{name}"


def to_pb2_python_module_name(source_path: os.PathLike) -> str:
    """Returns the Python module name for a given Protobuf source file."""
    basename, _ = os.path.splitext(source_path)
    return to_python_module_name(basename + "_pb2.py")


def build_pb2_python_type_lut(module_names: Iterable[str], inline_module_names: Iterable[str]) -> Dict[str, str]:
    """Builds a lookup table to go from Protobuf message type names to Python class name.

    For instance, if `google.protobuf.any_pb2` is listed as an imported module name and
    `google.protobuf.timestamp_pb2` is listed as an inline imported module name, the
    resulting lookup table will include entries such as:

    ``{"google.protobuf.Any": "google.protobuf.any_pb2.Any", "google.protobuf.timestamp_pb2.Timestamp": "Timestamp"}``

    where Python types for Protobuf messages coming from inline imports are unqualified.

    Args:
        module_names: names of Python modules to traverse in order to map fully qualified
        Protobuf message type names to fully qualified Python class names (assuming these
        modules will be imported like ``import <name>``).
        inline_module_names: names of Python modules to traverse in order to map fully
        qualified Protobuf message type names to unqualified Python class names (assuming
        these modules will be imported like ``from <name> import *``).

    Returns:
        a lookup table as a simple dict.
    """
    pb2_python_type_lut: Dict[str, str] = {}
    module_names = {name for name in module_names if name.endswith("_pb2")}
    inline_module_names = {name for name in inline_module_names if name.endswith("_pb2")}
    for module_name in (*module_names, *inline_module_names):
        module = importlib.import_module(module_name)
        attributes = [
            (fqn(value), value) if module_name in module_names else (name, value)
            for name, value in module.__dict__.items()
            if hasattr(value, "DESCRIPTOR")
        ]
        while attributes:
            name, value = attributes.pop(0)
            if not isinstance(value.DESCRIPTOR, Descriptor):
                continue
            assert name is not None
            proto_name = value.DESCRIPTOR.full_name
            pb2_python_type_lut[proto_name] = name
            attributes.extend(
                (f"{name}.{nested_name}", nested_value)
                for nested_name, nested_value in value.__dict__.items()
                if hasattr(nested_value, "DESCRIPTOR")
            )
        del sys.modules[module.__name__]
    return pb2_python_type_lut


def dump_conversions_python_module(
    message_specifications: List[MessageSpecification],
    known_message_specifications: List[MessageSpecification],
    config: Configuration,
) -> str:
    """Dumps the Python module source for Protobuf <-> ROS conversion APIs.

    Args:
        message_specifications: annotated ROS message specifications,
        as derived from equivalence relations (see `proto2ros.equivalences`).
        known_message_specifications: all annotated ROS message specifications known,
        including those from dependencies. A superset of ``message_specifications``.
        config: a suitable configuration for the procedure.

    Returns:
        the conversion Python module source.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("proto2ros.output"))
    env.globals["to_ros_base_type"] = to_ros_base_type
    env.globals["itemize_python_identifier"] = itemize_python_identifier
    env.filters["as_python_identifier"] = to_python_identifier
    env.filters["python_identifier_name"] = unqualify_python_identifier
    env.filters["as_ros_python_type"] = to_ros_python_type
    pb2_python_type_lut = build_pb2_python_type_lut(config.python_imports, config.inline_python_imports)

    def lookup_pb2_python_type(type_name: str) -> str:
        return pb2_python_type_lut[type_name]

    env.filters["as_pb2_python_type"] = lookup_pb2_python_type
    env.filters["as_ros_base_type"] = to_ros_base_type
    python_conversions_template = env.get_template("conversions.py.jinja")
    return python_conversions_template.render(
        message_specifications=message_specifications,
        known_message_specifications={str(spec.base_type): spec for spec in known_message_specifications},
        config=config,
    )


def dump_specifications_python_module(message_specifications: List[MessageSpecification], config: Configuration) -> str:
    """Dumps the Python module source bearing message specifications.

    This is the mechanism that enables proto2ros generated packages to depend on other proto2ros generated packages.

    Args:
        message_specifications: annotated ROS message specifications,
        as derived from equivalence relations (see `proto2ros.equivalences`).
        config: a suitable configuration for the procedure.

    Returns:
        the specifications Python module source.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("proto2ros.output"))

    def as_pickle_dump(obj: Any) -> str:
        return repr(pickle.dumps(obj))

    env.filters["as_pickle_dump"] = as_pickle_dump
    python_specifications_template = env.get_template("specifications.py.jinja")
    return python_specifications_template.render(message_specifications=message_specifications, config=config)
