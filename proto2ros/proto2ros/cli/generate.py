# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.
import argparse
import collections
import importlib
import importlib.resources
import os
import pathlib
import sys
import textwrap
from typing import List

from google.protobuf.descriptor_pb2 import FileDescriptorProto

from proto2ros.configuration import Configuration
from proto2ros.dependencies import fix_dependency_cycles
from proto2ros.descriptors.sources import read_source_descriptors
from proto2ros.equivalences import Equivalence, all_message_specifications, extract_equivalences
from proto2ros.output.cpp import dump_conversions_cpp_sources, to_pb2_cpp_header, to_ros_cpp_header
from proto2ros.output.interfaces import dump_message_specification, which_message_specification
from proto2ros.output.python import (
    dump_conversions_python_module,
    dump_specifications_python_module,
    to_pb2_python_module_name,
    to_ros_python_module_name,
)


def do_generate(args: argparse.Namespace) -> int:
    """Primary function to execute conversion of protobufs to ros msgs."""
    # Fetch baseline configuration.
    config = Configuration.from_file(args.config_file)

    # Read source descriptors for processing.
    source_descriptors: List[FileDescriptorProto] = []
    for descriptor_file in args.descriptor_files:
        for source_descriptor in read_source_descriptors(descriptor_file):
            # Map all Protobuf packages in source descriptors to target ROS package.
            config.package_mapping[source_descriptor.package] = args.package_name
            if not config.skip_implicit_imports:
                # Collect all .proto source files (including those imported).
                source_paths = [source_descriptor.name, *source_descriptor.dependency]
                # Add corresponding *_pb2 Python modules to configured Python imports.
                config.python_imports.update(map(to_pb2_python_module_name, source_paths))
                # Add corresponding *.pb.h C++ headers to configured C++ headers.
                config.cpp_headers.update(map(to_pb2_cpp_header, source_paths))
            source_descriptors.append(source_descriptor)

    # Apply overlays to configuration.
    for overlay_file in args.config_overlay_files:
        config.update(**Configuration.updates_from_file(overlay_file))

    # Compute Protobuf <-> ROS equivalences.
    equivalences: List[Equivalence] = []
    for source_descriptor in source_descriptors:
        equivalences.extend(extract_equivalences(source_descriptor, config))

    # Extract annotated message specifications from equivalences.
    message_specifications = list(all_message_specifications(equivalences))
    fix_dependency_cycles(message_specifications, quiet=args.dry)

    if not config.skip_implicit_imports:
        # Add target ROS package to configured Python imports.
        config.python_imports.add(to_ros_python_module_name(args.package_name))
        # Add target ROS package to configured C++ headers.
        for spec in message_specifications:
            config.cpp_headers.add(to_ros_cpp_header(spec))

    # Collect all known message specifications.
    known_message_specifications = list(message_specifications)
    for module_name in config.package_specifications:
        module = importlib.import_module(module_name)
        known_message_specifications.extend(module.messages)

    # Ensure no name clashes between message specifications.
    message_types = [spec.base_type for spec in known_message_specifications]
    message_type_instances = collections.Counter(message_types)
    if len(message_type_instances) != len(message_types):
        unique_message_type_instances = collections.Counter(set(message_type_instances))
        message_type_duplicates = list(message_type_instances - unique_message_type_instances)
        print("Found duplicate message types (name clashes?):", file=sys.stderr)
        print(
            textwrap.indent(
                "\n".join(
                    sorted(
                        [
                            f"{spec.annotations['proto-type']} maps to {spec.base_type}"
                            for spec in known_message_specifications
                            if spec.base_type in message_type_duplicates
                        ],
                    ),
                ),
                "    ",
            ),
            file=sys.stderr,
        )
        return 1

    files_written: List[os.PathLike] = []

    # Write message specifications to .py file.
    specifications_python_file = args.output_directory / "specifications.py"
    if not args.dry:
        specifications_python_file.write_text(dump_specifications_python_module(message_specifications, config) + "\n")
    files_written.append(specifications_python_file)

    messages_output_directory = args.output_directory / "msg"
    if args.force_message_gen or not args.dry:
        messages_output_directory.mkdir(exist_ok=True)

    # Write message specifications to .msg files.
    for message_specification in message_specifications:
        message_output_file = which_message_specification(message_specification, messages_output_directory)
        if args.force_message_gen or not args.dry:
            message_output_file.write_text(dump_message_specification(message_specification) + "\n")
        files_written.append(message_output_file)

    # Write Python conversion APIs .py file.
    conversions_python_file = args.output_directory / "conversions.py"
    if not args.dry:
        conversions_python_file.write_text(
            dump_conversions_python_module(message_specifications, known_message_specifications, config) + "\n",
        )
    files_written.append(conversions_python_file)

    # Write C++ conversion APIs source files.
    conversions_hpp_file = args.output_directory / "conversions.hpp"
    conversions_cpp_file = args.output_directory / "conversions.cpp"
    if not args.dry:
        hpp_content, cpp_content = dump_conversions_cpp_sources(
            args.package_name,
            message_specifications,
            known_message_specifications,
            config,
        )
        conversions_hpp_file.write_text(hpp_content + "\n")
        conversions_cpp_file.write_text(cpp_content + "\n")
    files_written.append(conversions_hpp_file)
    files_written.append(conversions_cpp_file)

    if args.manifest_file:
        # Write generation manifest file.
        args.manifest_file.write_text("\n".join(map(str, files_written)) + "\n")
    return 0


def main() -> int:
    """Entrypoint for proto2ros"""
    parser = argparse.ArgumentParser(description="Generate Protobuf <-> ROS 2 interoperability interfaces")
    parser.add_argument(
        "-O",
        "--output-directory",
        type=pathlib.Path,
        default=".",
        help="Output directory for all generated files.",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        type=pathlib.Path,
        default=importlib.resources.path("proto2ros.configuration", "default.yaml"),
        help="Base configuration file for the generation procedure.",
    )
    parser.add_argument(
        "-a",
        "--config-overlay-file",
        dest="config_overlay_files",
        type=pathlib.Path,
        action="append",
        default=[],
        help="Optional configuration overlay files.",
    )
    parser.add_argument(
        "-m",
        "--manifest-file",
        type=pathlib.Path,
        default=None,
        help="Optional manifest file to track generated files.",
    )
    parser.add_argument(
        "-d",
        "--dry",
        action="store_true",
        default=False,
        help="Whether to perform a dry run or not (manifest is still written)",
    )
    parser.add_argument(
        "--force-message-gen",
        action="store_true",
        default=False,
        help="Whether to generate message files regardless of other flags.",
    )
    parser.add_argument("package_name", help="Name of the ROS package that will bear generated messages.")
    parser.add_argument(
        "descriptor_files",
        type=pathlib.Path,
        nargs="+",
        help="Protobuf descriptor files to process, as generated by protoc.",
    )
    args = parser.parse_args()
    return do_generate(args)


if __name__ == "__main__":
    sys.exit(main())
