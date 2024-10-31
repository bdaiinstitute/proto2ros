// Copyright (c) 2024 Boston Dynamics AI Institute LLC. All rights reserved.

/// This module provides basic conversion APIs, applicable to any proto2ros generated packages.

#pragma once

#include <google/protobuf/any.pb.h>
#include <google/protobuf/duration.pb.h>
#include <google/protobuf/struct.pb.h>
#include <google/protobuf/timestamp.pb.h>
#include <google/protobuf/wrappers.pb.h>

#include <stdexcept>

#include <builtin_interfaces/msg/duration.hpp>
#include <builtin_interfaces/msg/time.hpp>
#include <proto2ros/msg/any.hpp>
#include <proto2ros/msg/any_proto.hpp>
#include <proto2ros/msg/bytes.hpp>
#include <proto2ros/msg/list.hpp>
#include <proto2ros/msg/struct.hpp>
#include <proto2ros/msg/value.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/float32.hpp>
#include <std_msgs/msg/float64.hpp>
#include <std_msgs/msg/int32.hpp>
#include <std_msgs/msg/int64.hpp>
#include <std_msgs/msg/string.hpp>
#include <std_msgs/msg/u_int32.hpp>
#include <std_msgs/msg/u_int64.hpp>

namespace proto2ros::conversions {

/// Unpacks a proto2ros/AnyProto ROS message into any Protobuf message.
///
/// \throws std::runtime_error if the given ROS message cannot be unpacked onto the given Protobuf message.
template <typename T>
void Convert(const proto2ros::msg::AnyProto& ros_msg, T* proto_msg) {
  proto_msg->Clear();
  auto wrapper = google::protobuf::Any();
  wrapper.set_type_url(ros_msg.type_url);
  auto* value = wrapper.mutable_value();
  value->reserve(ros_msg.value.size());
  value->assign(ros_msg.value.begin(), ros_msg.value.end());
  if (!wrapper.UnpackTo(proto_msg)) {
    throw std::runtime_error("failed to unpack AnyProto message");
  }
}

/// Packs any Protobuf message into a proto2ros/AnyProto ROS message.
template <typename T>
void Convert(const T& proto_msg, proto2ros::msg::AnyProto* ros_msg) {
  auto wrapper = google::protobuf::Any();
  wrapper.PackFrom(proto_msg);
  ros_msg->type_url = wrapper.type_url();
  const auto& value = wrapper.value();
  ros_msg->value.reserve(value.size());
  ros_msg->value.assign(value.begin(), value.end());
}

/// Converts from proto2ros/AnyProto ROS message to google.protobuf.Any Protobuf messages.
void Convert(const proto2ros::msg::AnyProto& ros_msg, google::protobuf::Any* proto_msg);

/// Converts from google.protobuf.Any Protobuf messages to proto2ros/AnyProto ROS messages.
void Convert(const google::protobuf::Any& proto_msg, proto2ros::msg::AnyProto* ros_msg);

/// Converts from google.protobuf.Any Protobuf messages to proto2ros/AnyProto ROS messages.
void Convert(const builtin_interfaces::msg::Duration& ros_msg, google::protobuf::Duration* proto_msg);

/// Converts from google.protobuf.Duration Protobuf messages to builtin_interfaces/Duration ROS messages.
void Convert(const google::protobuf::Duration& proto_msg, builtin_interfaces::msg::Duration* ros_msg);

/// Converts from builtin_interfaces/Time ROS messages to google.protobuf.Timestamp Protobuf messages.
void Convert(const builtin_interfaces::msg::Time& ros_msg, google::protobuf::Timestamp* proto_msg);

/// Converts from google.protobuf.Timestamp Protobuf messages to builtin_interfaces/Time ROS messages.
void Convert(const google::protobuf::Timestamp& proto_msg, builtin_interfaces::msg::Time* ros_msg);

/// Converts from std_msgs/Float64 ROS messages to google.protobuf.DoubleValue Protobuf messages.
void Convert(const std_msgs::msg::Float64& ros_msg, google::protobuf::DoubleValue* proto_msg);

/// Converts from google.protobuf.DoubleValue Protobuf messages to std_msgs/Float64 ROS messages.
void Convert(const google::protobuf::DoubleValue& proto_msg, std_msgs::msg::Float64* ros_msg);

/// Converts from std_msgs/Float32 ROS messages to google.protobuf.FloatValue Protobuf messages.
void Convert(const std_msgs::msg::Float32& ros_msg, google::protobuf::FloatValue* proto_msg);

/// Converts from google.protobuf.FloatValue Protobuf messages to std_msgs/Float32 ROS messages.
void Convert(const google::protobuf::FloatValue& proto_msg, std_msgs::msg::Float32* ros_msg);

/// Converts from std_msgs/Int64 ROS messages to google.protobuf.Int64Value Protobuf messages.
void Convert(const std_msgs::msg::Int64& ros_msg, google::protobuf::Int64Value* proto_msg);

/// Converts from google.protobuf.Int64Value Protobuf messages to std_msgs/Int64 ROS messages.
void Convert(const google::protobuf::Int64Value& proto_msg, std_msgs::msg::Int64* ros_msg);

/// Converts from std_msgs/Int32 ROS messages to google.protobuf.Int32Value Protobuf messages.
void Convert(const std_msgs::msg::Int32& ros_msg, google::protobuf::Int32Value* proto_msg);

/// Converts from google.protobuf.Int32Value Protobuf messages to std_msgs/Int32 ROS messages.
void Convert(const google::protobuf::Int32Value& proto_msg, std_msgs::msg::Int32* ros_msg);

/// Converts from std_msgs/UInt64 ROS messages to google.protobuf.UInt64Value Protobuf messages.
void Convert(const std_msgs::msg::UInt64& ros_msg, google::protobuf::UInt64Value* proto_msg);

/// Converts from google.protobuf.UInt64Value Protobuf messages to std_msgs/UInt64 ROS messages.
void Convert(const google::protobuf::UInt64Value& proto_msg, std_msgs::msg::UInt64* ros_msg);

/// Converts from std_msgs/UInt32 ROS messages to google.protobuf.UInt32Value Protobuf messages.
void Convert(const std_msgs::msg::UInt32& ros_msg, google::protobuf::UInt32Value* proto_msg);

/// Converts from google.protobuf.UInt32Value Protobuf messages to std_msgs/UInt32 ROS messages.
void Convert(const google::protobuf::UInt32Value& proto_msg, std_msgs::msg::UInt32* ros_msg);

/// Converts from std_msgs/Bool ROS messages to google.protobuf.BoolValue Protobuf messages.
void Convert(const std_msgs::msg::Bool& ros_msg, google::protobuf::BoolValue* proto_msg);

/// Converts from google.protobuf.BoolValue Protobuf messages to std_msgs/Bool ROS messages.
void Convert(const google::protobuf::BoolValue& proto_msg, std_msgs::msg::Bool* ros_msg);

/// Converts from std_msgs/String ROS messages to google.protobuf.StringValue Protobuf messages.
void Convert(const std_msgs::msg::String& ros_msg, google::protobuf::StringValue* proto_msg);

/// Converts from google.protobuf.StringValue Protobuf messages to std_msgs/String ROS messages.
void Convert(const google::protobuf::StringValue& proto_msg, std_msgs::msg::String* ros_msg);

/// Converts from proto2ros/Bytes ROS messages to google.protobuf.BytesValue Protobuf messages.
void Convert(const proto2ros::msg::Bytes& ros_msg, google::protobuf::BytesValue* proto_msg);

/// Converts from google.protobuf.BytesValue Protobuf messages to proto2ros/Bytes ROS messages.
void Convert(const google::protobuf::BytesValue& proto_msg, proto2ros::msg::Bytes* ros_msg);

/// Converts from proto2ros/Value ROS messages to google.protobuf.Value Protobuf messages.
void Convert(const proto2ros::msg::Value& ros_msg, google::protobuf::Value* proto_msg);

/// Converts from google.protobuf.Value Protobuf messages to proto2ros/Value ROS messages.
void Convert(const google::protobuf::Value& proto_msg, proto2ros::msg::Value* ros_msg);

/// Converts from proto2ros/List ROS messages to google.protobuf.ListValue Protobuf messages.
void Convert(const proto2ros::msg::List& ros_msg, google::protobuf::ListValue* proto_msg);

/// Converts from google.protobuf.ListValue Protobuf messages to proto2ros/List ROS messages.
void Convert(const google::protobuf::ListValue& proto_msg, proto2ros::msg::List* ros_msg);

/// Converts from proto2ros/Struct ROS messages to google.protobuf.Struct Protobuf messages.
void Convert(const proto2ros::msg::Struct& ros_msg, google::protobuf::Struct* proto_msg);

/// Converts from google.protobuf.Struct Protobuf messages to proto2ros/Struct ROS messages.
void Convert(const google::protobuf::Struct& proto_msg, proto2ros::msg::Struct* ros_msg);

}  // namespace proto2ros::conversions
