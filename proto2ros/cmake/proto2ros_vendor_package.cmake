# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

# Vendors a package providing Protobuf messages, adding ROS 2 interoperability interfaces.
#
# :param target: the target name for the process, so it can be depended on.
# :param PACKAGE_NAME: name of the package that will host the generated interfaces.
#   Defaults to the current project name.
# :param PROTOS: Protobuf message files to generate interoperability interfaces for.
#   These are compiled to a single Protobuf descriptor file for further processing.
# :param IMPORT_DIRS: optional import paths to pass to protoc. Only used when PROTOS
#   are provided. If none is given, parent directories of PROTOS are used instead.
# :param CONFIG_OVERLAYS: optional configuration file overlays to be applied sequentially
#   over the default base configuration file.
# :param ROS_DEPENDENCIES: optional ROS package name to depend on for message generation and builds.
# :param CPP_DEPENDENCIES: optional C++ targets to depend on for library builds.
# :param CPP_INCLUDES: optional, additional C++ includes to use when building C++ sources.
#   If none is provided and ${CMAKE_CURRENT_SOURCE_DIR}/include/${ARG_PACKAGE_NAME} exists
#   as a directory, then it will be picked up by default.
# :param CPP_SOURCES: optional, additional C++ sources to build alongside generated C++ sources.
#   If none is provided and both ${CMAKE_CURRENT_SOURCE_DIR}/include/${ARG_PACKAGE_NAME} and
#   ${CMAKE_CURRENT_SOURCE_DIR}/src exist as directories, then source files matching either
#   ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cc or ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp glob
#   expressions will be picked up by default.
# :param PYTHON_MODULES: optional, additional Python module sources to install
#   alongside generated Python modules.
# :param PYTHON_PACKAGES: optional, additional Python packages to install alongside
#   generated Python packages. If none is provided and one is found under the
#   ${CMAKE_CURRENT_SOURCE_DIR}/${PACKAGE_NAME}, it will be picked up by default.
# :param DEPENDS: optional, additional dependencies to the generation command.
#   This can be useful to depend on earlier protobuf_generate() commands.
# :param NO_LINT: if provided, no lint tests are added for generated code.
macro(proto2ros_vendor_package target)
  set(options NO_LINT)
  set(one_value_keywords PACKAGE_NAME)
  set(
    multi_value_keywords
    PROTOS IMPORT_DIRS CONFIG_OVERLAYS ROS_DEPENDENCIES CPP_DEPENDENCIES
    CPP_INCLUDES CPP_SOURCES PYTHON_MODULES PYTHON_PACKAGES DEPENDS
  )
  cmake_parse_arguments(ARG "${options}" "${one_value_keywords}" "${multi_value_keywords}" ${ARGN})

  if(NOT ARG_PACKAGE_NAME)
    set(ARG_PACKAGE_NAME ${PROJECT_NAME})
  endif()

  get_filename_component(package_path "${ARG_PACKAGE_NAME}" ABSOLUTE)
  if(EXISTS "${package_path}/__init__.py")
    list(APPEND ARG_PYTHON_PACKAGES ${ARG_PACKAGE_NAME})
  endif()

  if(NOT ARG_CPP_INCLUDES)
    if(IS_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include/${ARG_PACKAGE_NAME}")
      list(APPEND ARG_CPP_INCLUDES "${CMAKE_CURRENT_SOURCE_DIR}/include")
    endif()
  endif()

  if(NOT ARG_CPP_SOURCES)
    if(IS_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/include/${ARG_PACKAGE_NAME}" AND IS_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src")
      file(GLOB ARG_CPP_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp" "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cc")
    endif()
  endif()

  set(proto2ros_generate_OPTIONS)
  if(ARG_NO_LINT)
    list(APPEND proto2ros_generate_OPTIONS NO_LINT)
  endif()
  if(ARG_DEPENDS)
    list(APPEND proto2ros_generate_OPTIONS DEPENDS ${ARG_DEPENDS})
  endif()

  proto2ros_generate(
    ${target}_messages_gen
    PROTOS ${ARG_PROTOS}
    IMPORT_DIRS ${ARG_IMPORT_DIRS}
    PACKAGE_NAME ${ARG_PACKAGE_NAME}
    CONFIG_OVERLAYS ${ARG_CONFIG_OVERLAYS}
    INTERFACES_OUT_VAR ros_messages
    PYTHON_OUT_VAR py_sources
    CPP_OUT_VAR generated_cpp_sources
    INCLUDE_OUT_VAR generated_cpp_include_dir
    ${proto2ros_generate_OPTIONS}
  )

  rosidl_generate_interfaces(
    ${target} ${ros_messages}
    DEPENDENCIES ${ARG_ROS_DEPENDENCIES} builtin_interfaces proto2ros
  )
  add_dependencies(${target} ${target}_messages_gen)

  rosidl_generated_python_package_add(
    ${target}_additional_modules
    MODULES ${ARG_PYTHON_MODULES} ${py_sources}
    PACKAGES ${ARG_PYTHON_PACKAGES}
    DESTINATION ${target}
  )

  add_library(${target}_conversions SHARED ${generated_cpp_sources} ${ARG_CPP_SOURCES})
  target_compile_features(${target}_conversions PRIVATE cxx_std_17)
  # NOTE: conversion APIs cannot ignore deprecated fields, so deprecation warnings must be disabled
  target_compile_options(${target}_conversions PRIVATE -Wno-deprecated -Wno-deprecated-declarations)
  list(APPEND build_include_directories "$<BUILD_INTERFACE:${generated_cpp_include_dir}>")
  foreach(cpp_include_dir ${ARG_CPP_INCLUDES})
    list(APPEND build_include_directories "$<BUILD_INTERFACE:${cpp_include_dir}>")
  endforeach()
  target_include_directories(${target}_conversions PUBLIC
    ${build_include_directories} "$<INSTALL_INTERFACE:include/${PROJECT_NAME}>"
  )
  rosidl_get_typesupport_target(cpp_interfaces ${target} "rosidl_typesupport_cpp")
  target_link_libraries(${target}_conversions ${cpp_interfaces} ${ARG_CPP_DEPENDENCIES})
  ament_target_dependencies(${target}_conversions
    ${ARG_ROS_DEPENDENCIES} builtin_interfaces proto2ros rclcpp)

  find_program(CLANG_TIDY_EXECUTABLE NAMES "clang-tidy")
  if(BUILD_TESTING AND NOT ARG_NO_LINT AND CLANG_TIDY_EXECUTABLE)
    list(APPEND clang_tidy_header_regexes "${generated_cpp_include_dir}/.*hpp")
    foreach(cpp_include_dir ARG_CPP_INCLUDES)
      list(APPEND clang_tidy_header_regexes "${cpp_include_dir}/.*hpp")
    endforeach()
    list(JOIN clang_tidy_header_regexes "|" clang_tidy_header_filter)
    set(CXX_CLANG_TIDY "${CLANG_TIDY_EXECUTABLE}"
      "-header-filter='^(${clang_tidy_header_filter})$'"
      "-checks=-clang-diagnostic-ignored-optimization-argument")
    set_target_properties(${target}_conversions PROPERTIES
      CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON CXX_CLANG_TIDY "${CXX_CLANG_TIDY}")
  endif()

  set(generated_header_files ${generated_cpp_sources})
  list(FILTER generated_header_files INCLUDE REGEX ".*\.hpp$")
  install(
    FILES ${generated_header_files}
    DESTINATION include/${PROJECT_NAME}/${ARG_PACKAGE_NAME}/
  )
  foreach(cpp_include_dir ${ARG_CPP_INCLUDES})
    install(
      DIRECTORY ${cpp_include_dir}/
      DESTINATION include/${PROJECT_NAME}/
    )
  endforeach()

  install(
    TARGETS ${target}_conversions
    EXPORT ${PROJECT_NAME}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
  )
  ament_export_dependencies(builtin_interfaces proto2ros rclcpp)
  ament_export_targets(${PROJECT_NAME})
endmacro()
