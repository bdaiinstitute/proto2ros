# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.
find_package(Protobuf REQUIRED)

file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/api")
file(TOUCH "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/__init__.py")
file(TOUCH "${CMAKE_CURRENT_BINARY_DIR}/bosdyn/api/__init__.py")

protobuf_generate(
  LANGUAGE python
  OUT_VAR bosdyn_proto_py_sources
  PROTOS bosdyn/api/geometry.proto
)
protobuf_generate(
  LANGUAGE python
  OUT_VAR proto_py_sources
  PROTOS test.proto
)

protobuf_generate(
  LANGUAGE cpp
  OUT_VAR bosdyn_proto_cpp_sources
  PROTOS bosdyn/api/geometry.proto
)
protobuf_generate(
  LANGUAGE cpp
  OUT_VAR proto_cpp_sources
  PROTOS test.proto
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
