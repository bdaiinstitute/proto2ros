// Copyright (c) 2024 Boston Dynamics AI Institute LLC. All rights reserved.

#pragma once

#include <bosdyn/api/geometry.pb.h>
#include <test.pb.h>

#include <geometry_msgs/msg/polygon.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/quaternion.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <geometry_msgs/msg/wrench.hpp>
#include <sensor_msgs/msg/temperature.hpp>

namespace proto2ros_tests::conversions {

/// Converts from geometry_msgs/Vector3 ROS messages to bosdyn.api.Vec3 Protobuf messages.
void Convert(const geometry_msgs::msg::Vector3& ros_msg, bosdyn::api::Vec3* proto_msg);

/// Converts from bosdyn.api.Vec3 Protobuf messages to geometry_msgs/Vector3 ROS messages.
void Convert(const bosdyn::api::Vec3& proto_msg, geometry_msgs::msg::Vector3* ros_msg);

/// Converts from geometry_msgs/Point ROS messages to bosdyn.api.Vec3 Protobuf messages.
void Convert(const geometry_msgs::msg::Point& ros_msg, bosdyn::api::Vec3* proto_msg);

/// Converts from bosdyn.api.Vec3 Protobuf messages to geometry_msgs/Point ROS messages.
void Convert(const bosdyn::api::Vec3& proto_msg, geometry_msgs::msg::Point* ros_msg);

/// Converts from geometry_msgs/Quaternion ROS messages to bosdyn.api.Quaternion Protobuf messages.
void Convert(const geometry_msgs::msg::Quaternion& ros_msg, bosdyn::api::Quaternion* proto_msg);

/// Converts from bosdyn.api.Quaternion Protobuf messages to geometry_msgs/Quaternion ROS messages.
void Convert(const bosdyn::api::Quaternion& proto_msg, geometry_msgs::msg::Quaternion* ros_msg);

/// Converts from geometry_msgs/Pose ROS messages to bosdyn.api.SE3Pose Protobuf messages.
void Convert(const geometry_msgs::msg::Pose& ros_msg, bosdyn::api::SE3Pose* proto_msg);

/// Converts from bosdyn.api.SE3Pose Protobuf messages to geometry_msgs/Pose ROS messages.
void Convert(const bosdyn::api::SE3Pose& proto_msg, geometry_msgs::msg::Pose* ros_msg);

/// Converts from geometry_msgs/Pose ROS messages to bosdyn.api.SE2Pose Protobuf messages.
void Convert(const geometry_msgs::msg::Pose& ros_msg, bosdyn::api::SE2Pose* proto_msg);

/// Converts from bosdyn.api.SE2Pose Protobuf messages to geometry_msgs/Pose ROS messages.
void Convert(const bosdyn::api::SE2Pose& proto_msg, geometry_msgs::msg::Pose* ros_msg);

/// Converts from geometry_msgs/Polygon ROS messages to bosdyn.api.Polygon Protobuf messages.
void Convert(const geometry_msgs::msg::Polygon& ros_msg, bosdyn::api::Polygon* proto_msg);

/// Converts from bosdyn.api.Polygon Protobuf messages to geometry_msgs/Polygon ROS messages.
void Convert(const bosdyn::api::Polygon& proto_msg, geometry_msgs::msg::Polygon* ros_msg);

/// Converts from geometry_msgs/Vector3 ROS messages to bosdyn.api.Circle Protobuf messages.
void Convert(const geometry_msgs::msg::Vector3& ros_msg, bosdyn::api::Circle* proto_msg);

/// Converts from bosdyn.api.Circle Protobuf messages to geometry_msgs/Vector3 ROS messages.
void Convert(const bosdyn::api::Circle& proto_msg, geometry_msgs::msg::Vector3* ros_msg);

/// Converts from geometry_msgs/Twist ROS messages to bosdyn.api.SE3Velocity Protobuf messages.
void Convert(const geometry_msgs::msg::Twist& ros_msg, bosdyn::api::SE3Velocity* proto_msg);

/// Converts from bosdyn.api.SE3Velocity Protobuf messages to geometry_msgs/Twist ROS messages.
void Convert(const bosdyn::api::SE3Velocity& proto_msg, geometry_msgs::msg::Twist* ros_msg);

/// Converts from geometry_msgs/Wrench ROS messages to bosdyn.api.Wrench Protobuf messages.
void Convert(const geometry_msgs::msg::Wrench& ros_msg, bosdyn::api::Wrench* proto_msg);

/// Converts from bosdyn.api.Wrench Protobuf messages to geometry_msgs/Wrench ROS messages.
void Convert(const bosdyn::api::Wrench& proto_msg, geometry_msgs::msg::Wrench* ros_msg);

/// Converts from sensor_msgs/Temperature ROS messages to proto2ros_tests.Temperature Protobuf messages.
void Convert(const sensor_msgs::msg::Temperature& ros_msg, Temperature* proto_msg);

/// Converts from proto2ros_tests.Temperature Protobuf messages to sensor_msgs/Temperature ROS messages.
void Convert(const Temperature& proto_msg, sensor_msgs::msg::Temperature* ros_msg);

}  // namespace proto2ros_tests::conversions
