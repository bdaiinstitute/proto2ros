# Copyright (c) 2023 Robotics and AI Institute LLC dba RAI Institute. All rights reserved.
find_package(Protobuf REQUIRED)

get_executable_path(PROTOC_EXECUTABLE protobuf::protoc CONFIGURE)

set(protoc_options -I${CMAKE_CURRENT_SOURCE_DIR})
if(Protobuf_VERSION VERSION_GREATER_EQUAL "3.12" AND Protobuf_VERSION VERSION_LESS "3.15")
  list(APPEND protoc_options --experimental_allow_proto3_optional)
endif()

file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/api")
file(TOUCH "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/__init__.py")
file(TOUCH "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/api/__init__.py")

set(bosdyn_proto_py_sources "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/api/geometry_pb2.py")
set(proto_py_sources "${CMAKE_CURRENT_BINARY_DIR}/test_pb2.py")
set(bosdyn_proto_cpp_sources
  "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/api/geometry.pb.cc"
  "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/api/geometry.pb.h"
)
set(proto_cpp_sources
  "${CMAKE_CURRENT_BINARY_DIR}/test.pb.cc"
  "${CMAKE_CURRENT_BINARY_DIR}/test.pb.h"
)

add_custom_command(
  OUTPUT ${bosdyn_proto_py_sources}
  COMMAND ${PROTOC_EXECUTABLE} ${protoc_options} --python_out=${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/bosdyn/api/geometry.proto
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/bosdyn/api/geometry.proto
  COMMENT "Generate Python protobuf for bosdyn/api/geometry.proto"
  VERBATIM
)

add_custom_command(
  OUTPUT ${proto_py_sources}
  COMMAND ${PROTOC_EXECUTABLE} ${protoc_options} --python_out=${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/test.proto
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/test.proto
  COMMENT "Generate Python protobuf for test.proto"
  VERBATIM
)

add_custom_command(
  OUTPUT ${bosdyn_proto_cpp_sources}
  COMMAND ${PROTOC_EXECUTABLE} ${protoc_options} --cpp_out=${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/bosdyn/api/geometry.proto
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/bosdyn/api/geometry.proto
  COMMENT "Generate C++ protobuf for bosdyn/api/geometry.proto"
  VERBATIM
)

add_custom_command(
  OUTPUT ${proto_cpp_sources}
  COMMAND ${PROTOC_EXECUTABLE} ${protoc_options} --cpp_out=${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/test.proto
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/test.proto
  COMMENT "Generate C++ protobuf for test.proto"
  VERBATIM
)

add_library(${PROJECT_NAME}_proto SHARED ${proto_cpp_sources} ${bosdyn_proto_cpp_sources})
target_include_directories(${PROJECT_NAME}_proto PUBLIC "${CMAKE_CURRENT_BINARY_DIR}")
target_compile_options(${PROJECT_NAME}_proto PUBLIC -Wno-deprecated-declarations)
target_link_libraries(${PROJECT_NAME}_proto protobuf::libprotobuf)

add_custom_target(
  ${PROJECT_NAME}_proto_gen ALL DEPENDS
  ${proto_py_sources} ${bosdyn_proto_py_sources}
  ${proto_cpp_sources} ${bosdyn_proto_cpp_sources}
)

set(PROTO_OUT_DIR "${CMAKE_CURRENT_BINARY_DIR}" PARENT_SCOPE)
