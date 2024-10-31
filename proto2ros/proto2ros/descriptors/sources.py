# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides APIs to work with Protobuf definition sources."""

import functools
import os
from typing import Any, Iterable

from google.protobuf.descriptor_pb2 import FileDescriptorProto, FileDescriptorSet


@functools.singledispatch
def read_source_descriptors(source: Any) -> Iterable[FileDescriptorProto]:
    """Reads Protobuf file source descriptors.

    Note this function operates as the entrypoint to all corresponding overloads (via single dispatch).

    Args:
        source: a source to be read for descriptors.

    Returns:
        an iterable over all file source descriptors found.
    """
    raise NotImplementedError(f"not implemented for {source}")


@read_source_descriptors.register
def read_source_descriptors_from_bytes(blob: bytes) -> Iterable[FileDescriptorProto]:
    """Reads Protobuf file source descriptors from a binary blob.

    Args:
        blob: a binary blob, typically read from a .desc file.

    Returns:
        an iterable over all file source descriptors found.
    """
    descriptor = FileDescriptorSet()
    descriptor.ParseFromString(blob)
    yield from descriptor.file


@read_source_descriptors.register
def read_source_descriptors_from_file(path: os.PathLike) -> Iterable[FileDescriptorProto]:
    """Reads Protobuf file source descriptors from binary file.

    Args:
        path: path to binary file, typically a .desc file.

    Returns:
        an iterable over all file source descriptors found.
    """
    with open(path, "rb") as f:
        yield from read_source_descriptors_from_bytes(f.read())
