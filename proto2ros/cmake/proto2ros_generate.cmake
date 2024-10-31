# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

# Generates Protobuf <-> ROS 2 interoperability interfaces.
#
# :param target: the target name for the generation process, so it can be depended on.
# :param PACKAGE_NAME: name of the package that will host the generated interfaces.
#   Defaults to the current project name.
# :param PROTOS: Protobuf message files to generate interoperability interfaces for.
#   These are compiled to a single Protobuf descriptor file for further processing.
# :param IMPORT_DIRS: optional import paths to pass to protoc. Only used when PROTOS
#   are provided. If none is given, parent directories of PROTOS are used instead.
# :param PROTO_DESCRIPTORS: Protobuf descriptor files for the Protobuf messages
#   that the generation process will produce interoperability interfaces for.
# :param CONFIG_FILE: optional base configuration file for the generation process.
# :param CONFIG_OVERLAYS: optional configuration file overlays to be applied sequentially
#   over the (provided or default) base configuration file.
# :param INTERFACES_OUT_VAR: the name of the variable to yield ROS 2 interface tuples.
#   Defaults to the target name with an `_interfaces` suffix.
# :param PYTHON_OUT_VAR: the name of the variable to yield generated Python sources.
#   Defaults to the target name with a `_python_sources` suffix.
# :param CPP_OUT_VAR: the name of the variable to yield generated C++ sources
#   (both .cpp and .hpp files). Defaults to the target name with a `_cpp_sources` suffix.
# :param INCLUDE_OUT_VAR: the name of the variable to yield the path to generated
#   C++ includes. Defaults to the target name with a `_cpp_include` suffix.
# :param DEPENDS: optional, additional dependencies to the generation command.
#   This can be useful to depend on earlier protobuf_generate() commands.
# :param APPEND_PYTHONPATH: optional paths to append to the PYTHONPATH that applies
#   to the generation process.
# :param NO_LINT: if provided, no lint tests are added for generated code.
function(proto2ros_generate target)
  cmake_parse_arguments(
    ARG "NO_LINT"
    "PACKAGE_NAME;CONFIG_FILE;INTERFACES_OUT_VAR;PYTHON_OUT_VAR;CPP_OUT_VAR;INCLUDE_OUT_VAR"
    "PROTOS;PROTO_DESCRIPTORS;IMPORT_DIRS;CONFIG_OVERLAYS;APPEND_PYTHONPATH;DEPENDS" ${ARGN})
  if(NOT ARG_PACKAGE_NAME)
    set(ARG_PACKAGE_NAME ${PROJECT_NAME})
  endif()
  if(NOT ARG_INTERFACES_OUT_VAR)
    set(ARG_INTERFACES_OUT_VAR ${target}_interfaces)
  endif()
  if(NOT ARG_PYTHON_OUT_VAR)
    set(ARG_PYTHON_OUT_VAR ${target}_python_sources)
  endif()
  if(NOT ARG_CPP_OUT_VAR)
    set(ARG_CPP_OUT_VAR ${target}_cpp_sources)
  endif()
  if(NOT ARG_INCLUDE_OUT_VAR)
    set(ARG_INCLUDE_OUT_VAR ${target}_cpp_include)
  endif()
  list(APPEND ARG_APPEND_PYTHONPATH "${PROJECT_SOURCE_DIR}")
  string(REPLACE ";" ":" APPEND_PYTHONPATH "${ARG_APPEND_PYTHONPATH}")

  set(BASE_PATH "${CMAKE_CURRENT_BINARY_DIR}/proto2ros_generate")
  set(OUTPUT_PATH "${BASE_PATH}/${ARG_PACKAGE_NAME}")
  file(REMOVE_RECURSE "${OUTPUT_PATH}")
  file(MAKE_DIRECTORY "${OUTPUT_PATH}")

  foreach(path ${ARG_PROTO_DESCRIPTORS})
    get_filename_component(path "${path}" ABSOLUTE)
    list(APPEND PROTO_DESCRIPTORS ${path})
  endforeach()

  if(ARG_PROTOS)
    set(protoc_options --include_source_info)
    set(proto_descriptor "${CMAKE_CURRENT_BINARY_DIR}/${target}.desc")
    foreach(proto ${ARG_PROTOS})
      get_filename_component(proto_path "${proto}" ABSOLUTE)
      if(IS_DIRECTORY "${proto_path}")
        file(GLOB_RECURSE nested_files "${proto_path}" *.proto)
        if(NOT ARG_IMPORT_DIRS)
          list(APPEND protoc_options "-I${proto_path}")
        endif()
        list(APPEND proto_files ${nested_files})
      else()
        get_filename_component(proto_dir "${proto_path}" DIRECTORY)
        if(NOT ARG_IMPORT_DIRS)
          list(APPEND protoc_options "-I${proto_dir}")
        endif()
        list(APPEND proto_files "${proto_path}")
      endif()
    endforeach()
    foreach(path ${ARG_IMPORT_DIRS})
      get_filename_component(path "${path}" ABSOLUTE)
      list(APPEND protoc_options "-I${path}")
    endforeach()
    list(REMOVE_DUPLICATES protoc_options)

    # Generate the implicit descriptor file at configuration time
    # so that configuration code below can run.
    get_executable_path(PROTOC_EXECUTABLE protobuf::protoc CONFIGURE)
    execute_process(
      COMMAND
        ${PROTOC_EXECUTABLE} ${protoc_options} -o${proto_descriptor} ${proto_files}
      COMMAND_ERROR_IS_FATAL ANY
    )

    add_custom_command(
      OUTPUT ${proto_descriptor}
      COMMAND ${PROTOC_EXECUTABLE} ${protoc_options} -o${proto_descriptor} ${proto_files}
      DEPENDS ${proto_files}
      COMMENT "Compile descriptor from .proto files"
      VERBATIM
    )
    list(APPEND PROTO_DESCRIPTORS ${proto_descriptor})
  endif()

  if(NOT PROTO_DESCRIPTORS)
    message(FATAL_ERROR "No Protobuf descriptors to process")
  endif()

  if(ARG_CONFIG_FILE)
    get_filename_component(ARG_CONFIG_FILE "${ARG_CONFIG_FILE}" ABSOLUTE)
    list(APPEND PROTO2ROS_GENERATE_OPTIONS "-c" "${ARG_CONFIG_FILE}")
  endif()
  foreach(overlay ${ARG_CONFIG_OVERLAYS})
    get_filename_component(overlay "${overlay}" ABSOLUTE)
    list(APPEND PROTO2ROS_GENERATE_OPTIONS "-a" "${overlay}")
  endforeach()
  list(APPEND PROTO2ROS_GENERATE_OPTIONS "-m" "${OUTPUT_PATH}/manifest.txt")
  list(APPEND PROTO2ROS_GENERATE_OPTIONS "-O" "${OUTPUT_PATH}")

  # As we cannot deduce what files will result from the generation process ahead of time,
  # we perform a dry run at configuration time to determine these files. Build will be
  # forced to fail until reconfiguration whenever the set of output files changes. Note
  # that messages are also generated, as the rosidl pipeline requires them to exist at
  # configuration time.
  get_executable_path(PYTHON_EXECUTABLE Python3::Interpreter CONFIGURE)
  execute_process(
    COMMAND
      ${CMAKE_COMMAND} -E env
        "PYTHONPATH=${APPEND_PYTHONPATH}:$ENV{PYTHONPATH}"
        "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python"
      ${PYTHON_EXECUTABLE} -m proto2ros.cli.generate --dry --force-message-gen
        ${PROTO2ROS_GENERATE_OPTIONS} ${ARG_PACKAGE_NAME} ${PROTO_DESCRIPTORS}
      COMMAND_ERROR_IS_FATAL ANY
    )
  file(STRINGS "${OUTPUT_PATH}/manifest.txt" output_files)
  file(RENAME "${OUTPUT_PATH}/manifest.txt" "${OUTPUT_PATH}/manifest.orig.txt")

  add_custom_command(
    OUTPUT ${output_files}
    COMMAND
      ${CMAKE_COMMAND} -E env "PYTHONPATH=${APPEND_PYTHONPATH}:$ENV{PYTHONPATH}" "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python"
      ${PYTHON_EXECUTABLE} -m proto2ros.cli.generate ${PROTO2ROS_GENERATE_OPTIONS} ${ARG_PACKAGE_NAME} ${PROTO_DESCRIPTORS}
    COMMAND ${CMAKE_COMMAND} -E compare_files "${OUTPUT_PATH}/manifest.txt" "${OUTPUT_PATH}/manifest.orig.txt"
    COMMENT "Generate Protobuf <-> ROS interop interfaces (must reconfigure if the cardinality of the output set changes)"
    DEPENDS ${PROTO_DESCRIPTORS} ${ARG_DEPENDS}
    VERBATIM
  )
  add_custom_target(${target} DEPENDS ${output_files})

  set(interface_files ${output_files})
  list(FILTER interface_files INCLUDE REGEX ".*\.msg$")
  string(REPLACE "${OUTPUT_PATH}/" "${OUTPUT_PATH}:" interface_tuples "${interface_files}")
  set(python_sources ${output_files})
  list(FILTER python_sources INCLUDE REGEX ".*\.py$")
  set(cpp_sources ${output_files})
  list(FILTER cpp_sources INCLUDE REGEX ".*\.[ch]pp$")

  if(BUILD_TESTING AND NOT ARG_NO_LINT AND ament_cmake_mypy_FOUND)
    set(MYPY_PATH "${APPEND_PYTHONPATH}:$ENV{PYTHONPATH}")
    configure_file(
      "${proto2ros_DIR}/templates/mypy.ini.in"
      "${BASE_PATH}/mypy.ini" @ONLY
    )
    ament_mypy(${python_sources}
      TESTNAME ${target}_mypy
      CONFIG_FILE "${BASE_PATH}/mypy.ini"
    )
  endif()
  set(${ARG_INTERFACES_OUT_VAR} ${interface_tuples} PARENT_SCOPE)
  set(${ARG_PYTHON_OUT_VAR} ${python_sources} PARENT_SCOPE)
  set(${ARG_CPP_OUT_VAR} ${cpp_sources} PARENT_SCOPE)
  set(${ARG_INCLUDE_OUT_VAR} ${BASE_PATH} PARENT_SCOPE)
endfunction()
