// Copyright (c) 2024 Boston Dynamics AI Institute LLC. All rights reserved.

#include "proto2ros_tests/manual_conversions.hpp"

#include <cmath>

namespace proto2ros_tests::conversions {

void Convert(const geometry_msgs::msg::Vector3& ros_msg, bosdyn::api::Vec3* proto_msg) {
  proto_msg->set_x(ros_msg.x);
  proto_msg->set_y(ros_msg.y);
  proto_msg->set_z(ros_msg.z);
}

void Convert(const bosdyn::api::Vec3& proto_msg, geometry_msgs::msg::Vector3* ros_msg) {
  ros_msg->x = proto_msg.x();
  ros_msg->y = proto_msg.y();
  ros_msg->z = proto_msg.z();
}

void Convert(const geometry_msgs::msg::Point& ros_msg, bosdyn::api::Vec3* proto_msg) {
  proto_msg->set_x(ros_msg.x);
  proto_msg->set_y(ros_msg.y);
  proto_msg->set_z(ros_msg.z);
}

void Convert(const bosdyn::api::Vec3& proto_msg, geometry_msgs::msg::Point* ros_msg) {
  ros_msg->x = proto_msg.x();
  ros_msg->y = proto_msg.y();
  ros_msg->z = proto_msg.z();
}

void Convert(const geometry_msgs::msg::Quaternion& ros_msg, bosdyn::api::Quaternion* proto_msg) {
  proto_msg->set_x(ros_msg.x);
  proto_msg->set_y(ros_msg.y);
  proto_msg->set_z(ros_msg.z);
  proto_msg->set_w(ros_msg.w);
}

void Convert(const bosdyn::api::Quaternion& proto_msg, geometry_msgs::msg::Quaternion* ros_msg) {
  ros_msg->x = proto_msg.x();
  ros_msg->y = proto_msg.y();
  ros_msg->z = proto_msg.z();
  ros_msg->w = proto_msg.w();
}

void Convert(const geometry_msgs::msg::Pose& ros_msg, bosdyn::api::SE3Pose* proto_msg) {
  Convert(ros_msg.position, proto_msg->mutable_position());
  Convert(ros_msg.orientation, proto_msg->mutable_rotation());
}

void Convert(const bosdyn::api::SE3Pose& proto_msg, geometry_msgs::msg::Pose* ros_msg) {
  Convert(proto_msg.position(), &ros_msg->position);
  Convert(proto_msg.rotation(), &ros_msg->orientation);
}

void Convert(const geometry_msgs::msg::Pose& ros_msg, bosdyn::api::SE2Pose* proto_msg) {
  // NOLINTBEGIN(readability-magic-numbers)
  proto_msg->Clear();
  proto_msg->mutable_position()->set_x(ros_msg.position.x);
  proto_msg->mutable_position()->set_y(ros_msg.position.y);
  proto_msg->set_angle(2.0 * std::acos(ros_msg.orientation.w));
  const double angle = 2.0 * std::asin(ros_msg.orientation.z);
  if (std::abs(proto_msg->angle() - angle) > std::numeric_limits<double>::epsilon()) {
    throw std::domain_error("geometry_msgs/Pose does not represent a bosdyn.api.SE2Pose");
  }
  // NOLINTEND(readability-magic-numbers)
}

void Convert(const bosdyn::api::SE2Pose& proto_msg, geometry_msgs::msg::Pose* ros_msg) {
  // NOLINTBEGIN(readability-magic-numbers)
  ros_msg->position.x = proto_msg.position().x();
  ros_msg->position.y = proto_msg.position().y();
  ros_msg->position.z = 0.0;
  ros_msg->orientation.w = std::cos(proto_msg.angle() / 2.0);
  ros_msg->orientation.z = std::sin(proto_msg.angle() / 2.0);
  ros_msg->orientation.y = 0.0;
  ros_msg->orientation.x = 0.0;
  // NOLINTEND(readability-magic-numbers)
}

void Convert(const geometry_msgs::msg::Polygon& ros_msg, bosdyn::api::Polygon* proto_msg) {
  proto_msg->Clear();
  auto* vertices = proto_msg->mutable_vertexes();
  vertices->Reserve(static_cast<int>(ros_msg.points.size()));
  for (const auto& point : ros_msg.points) {
    auto* vertex = vertices->Add();
    vertex->set_x(point.x);
    vertex->set_y(point.y);
  }
}

void Convert(const bosdyn::api::Polygon& proto_msg, geometry_msgs::msg::Polygon* ros_msg) {
  ros_msg->points.clear();
  ros_msg->points.reserve(proto_msg.vertexes_size());
  for (const auto& vertex : proto_msg.vertexes()) {
    auto& point = ros_msg->points.emplace_back();
    point.x = static_cast<float>(vertex.x());
    point.y = static_cast<float>(vertex.y());
  }
}

void Convert(const geometry_msgs::msg::Vector3& ros_msg, bosdyn::api::Circle* proto_msg) {
  auto* center = proto_msg->mutable_center_pt();
  center->set_x(ros_msg.x);
  center->set_y(ros_msg.y);
  proto_msg->set_radius(ros_msg.z);
}

void Convert(const bosdyn::api::Circle& proto_msg, geometry_msgs::msg::Vector3* ros_msg) {
  const auto& center = proto_msg.center_pt();
  ros_msg->x = center.x();
  ros_msg->y = center.y();
  ros_msg->z = proto_msg.radius();
}

void Convert(const geometry_msgs::msg::Twist& ros_msg, bosdyn::api::SE3Velocity* proto_msg) {
  Convert(ros_msg.linear, proto_msg->mutable_linear());
  Convert(ros_msg.angular, proto_msg->mutable_angular());
}

void Convert(const bosdyn::api::SE3Velocity& proto_msg, geometry_msgs::msg::Twist* ros_msg) {
  Convert(proto_msg.linear(), &ros_msg->linear);
  Convert(proto_msg.angular(), &ros_msg->angular);
}

void Convert(const geometry_msgs::msg::Wrench& ros_msg, bosdyn::api::Wrench* proto_msg) {
  Convert(ros_msg.force, proto_msg->mutable_force());
  Convert(ros_msg.torque, proto_msg->mutable_torque());
}

void Convert(const bosdyn::api::Wrench& proto_msg, geometry_msgs::msg::Wrench* ros_msg) {
  Convert(proto_msg.force(), &ros_msg->force);
  Convert(proto_msg.torque(), &ros_msg->torque);
}

void Convert(const sensor_msgs::msg::Temperature& ros_msg, Temperature* proto_msg) {
  proto_msg->set_scale(Temperature::CELSIUS);
  proto_msg->set_value(static_cast<float>(ros_msg.temperature));
}

void Convert(const Temperature& proto_msg, sensor_msgs::msg::Temperature* ros_msg) {
  // NOLINTBEGIN(readability-magic-numbers)
  switch (proto_msg.scale()) {
    case Temperature::KELVIN:
      ros_msg->temperature = proto_msg.value() + 273.0;
      break;
    case Temperature::FAHRENHEIT:
      ros_msg->temperature = (proto_msg.value() - 32.0) * 5.0 / 9.0;
      break;
    case Temperature::CELSIUS:
    default:
      ros_msg->temperature = proto_msg.value();
      break;
  }
  // NOLINTEND(readability-magic-numbers)
}

}  // namespace proto2ros_tests::conversions
