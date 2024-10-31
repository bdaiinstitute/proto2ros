# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.
include("${proto2ros_DIR}/rosidl_helpers.cmake")
if(POLICY CMP0148)
  cmake_policy(SET CMP0148 OLD)  # to accommodate rosidl pipeline
endif()

find_package(Python3 REQUIRED)
find_package(PythonInterp REQUIRED)
find_package(Protobuf REQUIRED)
if(BUILD_TESTING)
  find_package(ament_cmake_mypy QUIET)
endif()
include("${proto2ros_DIR}/proto2ros_generate.cmake")

find_package(rclcpp REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)
include("${proto2ros_DIR}/proto2ros_vendor_package.cmake")
