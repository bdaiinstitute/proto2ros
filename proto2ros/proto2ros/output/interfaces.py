# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides APIs to write ROS message specifications."""

import os
import pathlib
from typing import List, Optional, Union

from rosidl_adapter.parser import BaseType, Field, MessageSpecification, Type


def dump_as_comments(content: str) -> str:
    """Dumps the given content as ROS message comment."""
    return "\n".join("#" + line for line in content.splitlines())


def dump_message_specification(message_spec: MessageSpecification) -> str:
    """Dumps a ROS message specification back to a string."""
    output = []
    if "comment" in message_spec.annotations:
        comment = message_spec.annotations["comment"]
        output.append(dump_as_comments(comment))
    if message_spec.constants:
        output.append("")  # blank line
        for constant in message_spec.constants:
            if "comment" in constant.annotations:
                comment = constant.annotations["comment"]
                output.append(dump_as_comments(comment))
            output.append(str(constant))
    if message_spec.fields:
        output.append("")  # blank line
        for field in message_spec.fields:
            qualifiers: List[str] = []
            if "comment" in field.annotations:
                comment = field.annotations["comment"]
                output.append(dump_as_comments(comment))
            if field.annotations.get("deprecated"):
                qualifiers.append("deprecated")
            if field.annotations.get("type-erased"):
                qualifiers.append(f"is {field.type} (type-erased)")
                any_type = Type(str(field.type).replace(BaseType.__str__(field.type), "proto2ros/Any"))
                field = Field(any_type, field.name)
            line = str(field)
            if qualifiers:
                line += "  # " + ", ".join(qualifiers)
            output.append(line)
    return "\n".join(output)


def which_message_specification(
    message_spec: MessageSpecification,
    root: Optional[Union[str, os.PathLike[str]]] = None,
) -> pathlib.Path:
    """Returns an .msg file path for a given ROS message specification.

    ROS .msg file name conversions are observed in the process.

    Args:
        message_spec: source ROS message specification.
        root: optional root directory for .msg file.

    Returns:
        the full .msg file path.
    """
    if root is None:
        root = "."
    return pathlib.Path(root) / f"{message_spec.msg_name}.msg"
