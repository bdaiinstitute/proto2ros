# Copyright (c) 2023 Robotics and AI Institute LLC dba RAI Institute. All rights reserved.

"""This module defines configuration data structures for proto2ros generation."""

import dataclasses
import os
from typing import Any, Dict, Set, Union

import yaml
from rosidl_adapter.parser import MessageSpecification


@dataclasses.dataclass
class Configuration:
    """Mutable Protobuf <-> ROS configuration.

    Attributes:

        drop_deprecated: whether to drop deprecated fields on conversion or not.
          If not dropped, deprecated fields are annotated with a comment.
        passthrough_unknown: whether to forward Protobuf messages for which no
          equivalent ROS message is known as a type erased, ``proto2ros/AnyProto``
          field or not.
        message_mapping: a mapping from fully qualified Protobuf message type names
          to fully qualified ROS message type names. This mapping comes first during
          composite type translation.
        package_mapping: a mapping from Protobuf package names to ROS package names,
          to tell where a ROS equivalent for a Protobuf construct will be found. Note
          that no checks for package existence are performed. This mapping comes
          second during composite type translation (i.e. when direct message mapping
          fails).
        any_expansions: a mapping from fully qualified Protobuf field names (i.e. a
          fully qualified Protobuf message type name followed by a dot "." followed by
          the field name) of ``google.protobuf.Any`` type to Protobuf message type sets
          that these fields are expected to pack. A single Protobuf message type may also
          be specified in lieu of a single element set. All Protobuf message types must be
          fully qualified.
        allow_any_casts: when a single Protobuf message type is specified in an any expansion,
          allowing any casts means to allow using the equivalent ROS message type instead of a
          a type erased, ``proto2ros/Any`` field.
        package_specifications: set of Python modules to gather message specifications from.
          Necessary to cascade message generation for interdependent packages.
        cpp_headers: set of C++ headers to be included (as ``#include <{header}>``) in generated
          C++ conversion headers. Typically, Protobuf and ROS message C++ headers.
        inline_cpp_namespaces: set of C++ namespaces bearing conversion overloads, for which
          unqualified lookup (``using {namespace}::Convert;``) is necessary in generated C++
          conversion sources.
        python_imports: set of Python modules to be imported (as ``import <module-name>``) in
          generated Python conversion modules. Typically, Protobuf and ROS message Python modules.
        inline_python_imports: set of Python modules to be imported into moodule scope
          (as ``from <module-name> import *``) in generated conversion modules. Typically,
          conversion Python modules.
        skip_implicit_imports: whether to skip importing Python modules for Protobuf and ROS
          packages known in generated conversion modules or not.
    """

    drop_deprecated: bool = False
    passthrough_unknown: bool = True
    package_mapping: Dict[str, str] = dataclasses.field(default_factory=dict)
    message_mapping: Dict[str, str] = dataclasses.field(default_factory=dict)

    any_expansions: Dict[str, Union[Set[str], str]] = dataclasses.field(default_factory=dict)
    allow_any_casts: bool = True

    package_specifications: Set[str] = dataclasses.field(default_factory=set)

    cpp_headers: Set[str] = dataclasses.field(default_factory=set)
    inline_cpp_namespaces: Set[str] = dataclasses.field(default_factory=set)

    python_imports: Set[str] = dataclasses.field(default_factory=set)
    inline_python_imports: Set[str] = dataclasses.field(default_factory=set)

    skip_implicit_imports: bool = False

    def __post_init__(self) -> None:
        """Enforces attribute types."""
        self.any_expansions = {
            key: set(value) if not isinstance(value, str) else value for key, value in self.any_expansions.items()
        }
        self.cpp_headers = set(self.cpp_headers)
        self.inline_cpp_namespaces = set(self.inline_cpp_namespaces)
        self.python_imports = set(self.python_imports)
        self.inline_python_imports = set(self.inline_python_imports)
        self.package_specifications = set(self.package_specifications)

    def update(self, **attributes: Any) -> None:
        """Updates configuration attributes with a shallow merge."""
        for name, value in attributes.items():
            old_value = getattr(self, name)
            if hasattr(old_value, "update"):
                old_value.update(value)
            elif hasattr(old_value, "extend"):
                old_value.extend(value)
            else:
                setattr(self, name, value)

    @classmethod
    def updates_from_file(cls, path: os.PathLike) -> Dict[str, Any]:
        """Reads configuration attribute updates from a file."""
        with open(path, "r") as f:
            return yaml.safe_load(f)

    @classmethod
    def from_file(cls, path: os.PathLike) -> "Configuration":
        """Reads configuration from a file."""
        return cls(**cls.updates_from_file(path))
