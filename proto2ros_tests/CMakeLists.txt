# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.
cmake_minimum_required(VERSION 3.12)
if(POLICY CMP0148)
  cmake_policy(SET CMP0148 OLD)  # to accommodate rosidl pipeline
endif()
project(proto2ros_tests)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
  set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
endif()

set(DEFAULT_BUILD_TYPE "Release")
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${DEFAULT_BUILD_TYPE}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${DEFAULT_BUILD_TYPE}" CACHE STRING "Choose the type of the build." FORCE)
  # Set the possible values of the build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(rclcpp REQUIRED)

find_package(proto2ros REQUIRED)

find_package(rosidl_default_generators REQUIRED)

add_subdirectory(proto)

proto2ros_generate(
  ${PROJECT_NAME}_messages_gen
  PROTOS proto/test.proto
  CONFIG_OVERLAYS config/overlay.yaml
  INTERFACES_OUT_VAR ros_messages
  PYTHON_OUT_VAR py_sources
  CPP_OUT_VAR cpp_sources
  INCLUDE_OUT_VAR cpp_include_dir
  APPEND_PYTHONPATH "${PROTO_OUT_DIR}"
  DEPENDS ${PROJECT_NAME}_proto_gen
)

rosidl_generate_interfaces(
  ${PROJECT_NAME} ${ros_messages}
  DEPENDENCIES geometry_msgs sensor_msgs builtin_interfaces proto2ros
  SKIP_INSTALL
)
add_dependencies(${PROJECT_NAME} ${PROJECT_NAME}_messages_gen)

add_library(${PROJECT_NAME}_conversions SHARED ${cpp_sources} src/manual_conversions.cpp)
set_target_properties(${PROJECT_NAME}_conversions PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
target_compile_options(${PROJECT_NAME}_conversions PUBLIC "$<$<CONFIG:DEBUG>:-O0>")
target_compile_definitions(${PROJECT_NAME}_conversions
  PUBLIC
  "$<$<CONFIG:DEBUG>:DEBUG>"
  "$<$<OR:$<CONFIG:RELWITHDEBINFO>,$<CONFIG:RELEASE>>:NDEBUG>"
)
target_include_directories(${PROJECT_NAME}_conversions PUBLIC
  "$<BUILD_INTERFACE:${cpp_include_dir}>"
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include/${PROJECT_NAME}>"
)
rosidl_get_typesupport_target(${PROJECT_NAME}_cpp_msgs ${PROJECT_NAME} "rosidl_typesupport_cpp")
target_link_libraries(${PROJECT_NAME}_conversions
  ${${PROJECT_NAME}_cpp_msgs} ${PROJECT_NAME}_proto protobuf::libprotobuf)
ament_target_dependencies(${PROJECT_NAME}_conversions
  builtin_interfaces geometry_msgs sensor_msgs proto2ros rclcpp)

rosidl_generated_python_package_add(
  ${PROJECT_NAME}_additional_modules
  MODULES ${proto_py_sources} ${py_sources}
  PACKAGES ${PROJECT_NAME}
  DESTINATION ${PROJECT_NAME}
)

find_program(CLANG_TIDY_EXECUTABLE NAMES "clang-tidy" REQUIRED)
set(CXX_CLANG_TIDY "${CLANG_TIDY_EXECUTABLE}" "-header-filter=.*proto2ros.*/.*conversions.hpp")
set_target_properties(${PROJECT_NAME}_conversions PROPERTIES CXX_CLANG_TIDY "${CXX_CLANG_TIDY}")

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)

  get_rosidl_generated_interfaces_test_setup(
    LIBRARY_DIRS additional_library_dirs
    ENV additional_env
  )
  list(APPEND additional_env "PYTHONPATH=${PROTO_OUT_DIR}")

  ament_add_pytest_test(
    regression_py_tests test
    APPEND_LIBRARY_DIRS ${additional_library_dirs}
    APPEND_ENV ${additional_env}
    ENV CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}
    PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
  )

  ament_add_gtest(
    regression_cpp_tests test/test_proto2ros.cpp
    APPEND_LIBRARY_DIRS ${additional_library_dirs}
    ENV CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}
  )
  target_link_libraries(regression_cpp_tests
    ${${PROJECT_NAME}_cpp_msgs} ${PROJECT_NAME}_proto
    ${PROJECT_NAME}_conversions proto2ros::proto2ros_conversions
  )
  set_target_properties(regression_cpp_tests PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
  set_target_properties(regression_cpp_tests PROPERTIES CXX_CLANG_TIDY "${CXX_CLANG_TIDY}")
endif()

ament_package()
