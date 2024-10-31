// Copyright (c) 2024 Boston Dynamics AI Institute LLC. All rights reserved.

#include "proto2ros/conversions.hpp"

#include <sstream>

#include <rclcpp/serialization.hpp>
#include <rclcpp/serialized_message.hpp>

namespace proto2ros::conversions {

void Convert(const proto2ros::msg::AnyProto& ros_msg, google::protobuf::Any* proto_msg) {
  proto_msg->Clear();
  proto_msg->set_type_url(ros_msg.type_url);
  auto* value = proto_msg->mutable_value();
  value->reserve(ros_msg.value.size());
  value->assign(ros_msg.value.begin(), ros_msg.value.end());
}

void Convert(const google::protobuf::Any& proto_msg, proto2ros::msg::AnyProto* ros_msg) {
  ros_msg->type_url = proto_msg.type_url();
  const auto& value = proto_msg.value();
  ros_msg->value.reserve(value.size());
  ros_msg->value.assign(value.begin(), value.end());
}

void Convert(const builtin_interfaces::msg::Duration& ros_msg, google::protobuf::Duration* proto_msg) {
  proto_msg->set_seconds(ros_msg.sec);
  if (ros_msg.nanosec > static_cast<unsigned int>(std::numeric_limits<int>::max())) {
    throw std::range_error("builtin_interfaces/Duration does not fit in google.protobuf.Duration");
  }
  proto_msg->set_nanos(static_cast<int>(ros_msg.nanosec));
}

void Convert(const google::protobuf::Duration& proto_msg, builtin_interfaces::msg::Duration* ros_msg) {
  if (proto_msg.seconds() > static_cast<google::protobuf::int64>(std::numeric_limits<int>::max())) {
    throw std::range_error("google.protobuf.Durationdoes not fit in builtin_interfaces/Duration");
  }
  ros_msg->sec = static_cast<int>(proto_msg.seconds());
  ros_msg->nanosec = proto_msg.nanos();
}

void Convert(const builtin_interfaces::msg::Time& ros_msg, google::protobuf::Timestamp* proto_msg) {
  proto_msg->set_seconds(ros_msg.sec);
  if (ros_msg.nanosec > static_cast<unsigned int>(std::numeric_limits<int>::max())) {
    throw std::range_error("builtin_interfaces/Time does not fit in google.protobuf.Timestamp");
  }
  proto_msg->set_nanos(static_cast<int>(ros_msg.nanosec));
}

void Convert(const google::protobuf::Timestamp& proto_msg, builtin_interfaces::msg::Time* ros_msg) {
  if (proto_msg.seconds() > static_cast<google::protobuf::int64>(std::numeric_limits<int>::max())) {
    throw std::range_error("google.protobuf.Timestamp does not fit in builtin_interfaces/Time");
  }
  ros_msg->sec = static_cast<int>(proto_msg.seconds());
  ros_msg->nanosec = proto_msg.nanos();
}

void Convert(const std_msgs::msg::Float64& ros_msg, google::protobuf::DoubleValue* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

void Convert(const google::protobuf::DoubleValue& proto_msg, std_msgs::msg::Float64* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const std_msgs::msg::Float32& ros_msg, google::protobuf::FloatValue* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

void Convert(const google::protobuf::FloatValue& proto_msg, std_msgs::msg::Float32* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const std_msgs::msg::Int64& ros_msg, google::protobuf::Int64Value* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

void Convert(const google::protobuf::Int64Value& proto_msg, std_msgs::msg::Int64* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const std_msgs::msg::Int32& ros_msg, google::protobuf::Int32Value* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

void Convert(const google::protobuf::Int32Value& proto_msg, std_msgs::msg::Int32* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const std_msgs::msg::UInt64& ros_msg, google::protobuf::UInt64Value* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

void Convert(const google::protobuf::UInt64Value& proto_msg, std_msgs::msg::UInt64* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const std_msgs::msg::UInt32& ros_msg, google::protobuf::UInt32Value* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

/// Converts from google.protobuf.UInt32Value Protobuf messages to std_msgs/UInt32 ROS messages.
void Convert(const google::protobuf::UInt32Value& proto_msg, std_msgs::msg::UInt32* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const std_msgs::msg::Bool& ros_msg, google::protobuf::BoolValue* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

void Convert(const google::protobuf::BoolValue& proto_msg, std_msgs::msg::Bool* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const std_msgs::msg::String& ros_msg, google::protobuf::StringValue* proto_msg) {
  proto_msg->set_value(ros_msg.data);
}

void Convert(const google::protobuf::StringValue& proto_msg, std_msgs::msg::String* ros_msg) {
  ros_msg->data = proto_msg.value();
}

void Convert(const proto2ros::msg::Bytes& ros_msg, google::protobuf::BytesValue* proto_msg) {
  auto* value = proto_msg->mutable_value();
  value->reserve(ros_msg.data.size());
  value->assign(ros_msg.data.begin(), ros_msg.data.end());
}

void Convert(const google::protobuf::BytesValue& proto_msg, proto2ros::msg::Bytes* ros_msg) {
  const auto& value = proto_msg.value();
  ros_msg->data.reserve(value.size());
  ros_msg->data.assign(value.begin(), value.end());
}

void Convert(const proto2ros::msg::Value& ros_msg, google::protobuf::Value* proto_msg) {
  proto_msg->Clear();
  switch (ros_msg.kind) {
    case proto2ros::msg::Value::NUMBER_VALUE_SET:
      proto_msg->set_number_value(ros_msg.number_value);
      break;
    case proto2ros::msg::Value::STRING_VALUE_SET:
      proto_msg->set_string_value(ros_msg.string_value);
      break;
    case proto2ros::msg::Value::BOOL_VALUE_SET:
      proto_msg->set_bool_value(ros_msg.bool_value);
      break;
    case proto2ros::msg::Value::STRUCT_VALUE_SET: {
      if (ros_msg.struct_value.type_name != "proto2ros/Struct") {
        std::ostringstream message{"expected proto2ros/Struct message for struct_value member"};
        message << ", got " << ros_msg.struct_value.type_name;
        throw std::runtime_error(message.str());
      }
      rclcpp::SerializedMessage serialized_message;
      const auto& value = ros_msg.struct_value.value;
      serialized_message.reserve(value.size());
      auto& rcl_serialized_message = serialized_message.get_rcl_serialized_message();
      std::copy(value.begin(), value.end(), rcl_serialized_message.buffer);
      rcl_serialized_message.buffer_length = value.size();
      const auto serde = rclcpp::Serialization<proto2ros::msg::Struct>{};
      auto typed_ros_message = proto2ros::msg::Struct();
      serde.deserialize_message(&serialized_message, &typed_ros_message);
      Convert(typed_ros_message, proto_msg->mutable_struct_value());
    } break;
    case proto2ros::msg::Value::LIST_VALUE_SET: {
      if (ros_msg.list_value.type_name != "proto2ros/List") {
        std::ostringstream message{"expected proto2ros/Struct message for list_value member"};
        message << ", got " << ros_msg.list_value.type_name;
        throw std::runtime_error(message.str());
      }
      rclcpp::SerializedMessage serialized_message;
      const auto& value = ros_msg.list_value.value;
      serialized_message.reserve(value.size());
      auto& rcl_serialized_message = serialized_message.get_rcl_serialized_message();
      std::copy(value.begin(), value.end(), rcl_serialized_message.buffer);
      rcl_serialized_message.buffer_length = value.size();
      const auto serde = rclcpp::Serialization<proto2ros::msg::Struct>{};
      auto typed_ros_message = proto2ros::msg::List();
      serde.deserialize_message(&serialized_message, &typed_ros_message);
      Convert(typed_ros_message, proto_msg->mutable_list_value());
    } break;
    case proto2ros::msg::Value::NULL_VALUE_SET:
      proto_msg->set_null_value(google::protobuf::NullValue::NULL_VALUE);
      break;
    default:
      break;
  }
}

void Convert(const google::protobuf::Value& proto_msg, proto2ros::msg::Value* ros_msg) {
  switch (proto_msg.kind_case()) {
    case google::protobuf::Value::kNumberValue:
      ros_msg->number_value = proto_msg.number_value();
      ros_msg->kind = proto2ros::msg::Value::NUMBER_VALUE_SET;
      break;
    case google::protobuf::Value::kStringValue:
      ros_msg->string_value = proto_msg.string_value();
      ros_msg->kind = proto2ros::msg::Value::STRING_VALUE_SET;
      break;
    case google::protobuf::Value::kBoolValue:
      ros_msg->bool_value = proto_msg.bool_value();
      ros_msg->kind = proto2ros::msg::Value::BOOL_VALUE_SET;
      break;
    case google::protobuf::Value::kStructValue: {
      auto typed_ros_message = proto2ros::msg::Struct();
      Convert(proto_msg.struct_value(), &typed_ros_message);
      const auto serde = rclcpp::Serialization<proto2ros::msg::Struct>{};
      rclcpp::SerializedMessage serialized_message;
      serde.serialize_message(&typed_ros_message, &serialized_message);
      const auto& rcl_serialized_message = serialized_message.get_rcl_serialized_message();
      const auto* begin = rcl_serialized_message.buffer;
      const auto* end = begin + rcl_serialized_message.buffer_length;
      ros_msg->struct_value.value.assign(begin, end);
      ros_msg->struct_value.type_name = "proto2ros/Struct";
      ros_msg->kind = proto2ros::msg::Value::STRUCT_VALUE_SET;
    } break;
    case google::protobuf::Value::kListValue: {
      auto typed_ros_message = proto2ros::msg::List();
      Convert(proto_msg.list_value(), &typed_ros_message);
      const auto serde = rclcpp::Serialization<proto2ros::msg::List>{};
      rclcpp::SerializedMessage serialized_message;
      serde.serialize_message(&typed_ros_message, &serialized_message);
      const auto& rcl_serialized_message = serialized_message.get_rcl_serialized_message();
      const auto* begin = rcl_serialized_message.buffer;
      const auto* end = begin + rcl_serialized_message.buffer_length;
      ros_msg->list_value.value.assign(begin, end);
      ros_msg->list_value.type_name = "proto2ros/List";
      ros_msg->kind = proto2ros::msg::Value::LIST_VALUE_SET;
    } break;
    case google::protobuf::Value::kNullValue:
      ros_msg->kind = proto2ros::msg::Value::NULL_VALUE_SET;
      break;
    default:
      ros_msg->kind = proto2ros::msg::Value::NO_VALUE_SET;
      break;
  }
}

void Convert(const proto2ros::msg::List& ros_msg, google::protobuf::ListValue* proto_msg) {
  proto_msg->Clear();
  auto* values = proto_msg->mutable_values();
  values->Reserve(static_cast<int>(ros_msg.values.size()));
  for (const auto& input_item : ros_msg.values) {
    auto* output_item = values->Add();
    Convert(input_item, output_item);
  }
}

void Convert(const google::protobuf::ListValue& proto_msg, proto2ros::msg::List* ros_msg) {
  ros_msg->values.clear();
  ros_msg->values.reserve(proto_msg.values_size());
  for (const auto& input_item : proto_msg.values()) {
    auto& output_item = ros_msg->values.emplace_back();
    Convert(input_item, &output_item);
  }
}

void Convert(const proto2ros::msg::Struct& ros_msg, google::protobuf::Struct* proto_msg) {
  proto_msg->Clear();
  auto* output_fields = proto_msg->mutable_fields();
  for (const auto& field : ros_msg.fields) {
    Convert(field.value, &(*output_fields)[field.key]);
  }
}

void Convert(const google::protobuf::Struct& proto_msg, proto2ros::msg::Struct* ros_msg) {
  ros_msg->fields.clear();
  const auto& input_fields = proto_msg.fields();
  ros_msg->fields.reserve(input_fields.size());
  for (const auto& [key, value] : input_fields) {
    auto& field = ros_msg->fields.emplace_back();
    field.key = key;
    Convert(value, &field.value);
  }
}

}  // namespace proto2ros::conversions
