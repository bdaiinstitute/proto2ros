# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides basic conversion APIs, applicable to any proto2ros generated packages."""

from typing import Any

import builtin_interfaces.msg
import google.protobuf.any_pb2
import google.protobuf.duration_pb2
import google.protobuf.struct_pb2
import google.protobuf.timestamp_pb2
import google.protobuf.wrappers_pb2
import rclpy
import std_msgs.msg

import proto2ros.msg
from proto2ros.conversions import convert


@convert.register(proto2ros.msg.AnyProto, object)
def convert_proto2ros_any_proto_message_to_some_proto(ros_msg: proto2ros.msg.AnyProto, proto_msg: Any) -> None:
    """Unpacks a proto2ros/AnyProto ROS message into any Protobuf message.

    Raises:
        ValueError: if the given ROS message cannot be unpacked onto the given Protobuf message.
    """
    proto_msg.Clear()
    wrapper = google.protobuf.any_pb2.Any()
    wrapper.type_url = ros_msg.type_url
    wrapper.value = ros_msg.value.tobytes()
    if not wrapper.Unpack(proto_msg):
        raise ValueError(f"failed to convert {ros_msg} to {proto_msg}")


@convert.register(object, proto2ros.msg.AnyProto)
def convert_some_proto_to_proto2ros_any_proto_message(proto_msg: Any, ros_msg: proto2ros.msg.AnyProto) -> None:
    """Packs any Protobuf message into a proto2ros/AnyProto ROS message."""
    wrapper = google.protobuf.any_pb2.Any()
    wrapper.Pack(proto_msg)
    ros_msg.type_url = wrapper.type_url
    ros_msg.value = wrapper.value


@convert.register(proto2ros.msg.AnyProto, proto2ros.msg.AnyProto)
def _(proto_msg: proto2ros.msg.AnyProto, ros_msg: proto2ros.msg.AnyProto) -> None:
    # address multipledispatch ambiguous resolution concerns
    raise RuntimeError("invalid overload")


@convert.register(proto2ros.msg.AnyProto, google.protobuf.any_pb2.Any)
def convert_proto2ros_any_proto_message_to_google_protobuf_any_proto(
    ros_msg: proto2ros.msg.AnyProto,
    proto_msg: google.protobuf.any_pb2.Any,
) -> None:
    """Converts from proto2ros/AnyProto ROS message to google.protobuf.Any Protobuf messages."""
    proto_msg.Clear()
    proto_msg.type_url = ros_msg.type_url
    proto_msg.value = ros_msg.value.tobytes()


@convert.register(google.protobuf.any_pb2.Any, proto2ros.msg.AnyProto)
def convert_google_protobuf_any_proto_to_proto2ros_any_proto_message(
    proto_msg: google.protobuf.any_pb2.Any,
    ros_msg: proto2ros.msg.AnyProto,
) -> None:
    """Converts from google.protobuf.Any Protobuf messages to proto2ros/AnyProto ROS messages."""
    ros_msg.type_url = proto_msg.type_url
    ros_msg.value = proto_msg.value


@convert.register(builtin_interfaces.msg.Duration, google.protobuf.duration_pb2.Duration)
def convert_builtin_interfaces_duration_message_to_google_protobuf_duration_proto(
    ros_msg: builtin_interfaces.msg.Duration,
    proto_msg: google.protobuf.duration_pb2.Duration,
) -> None:
    """Converts from google.protobuf.Any Protobuf messages to proto2ros/AnyProto ROS messages."""
    proto_msg.seconds = ros_msg.sec
    proto_msg.nanos = ros_msg.nanosec


convert_builtin_interfaces_duration_to_proto = (
    convert_builtin_interfaces_duration_message_to_google_protobuf_duration_proto
)


@convert.register(google.protobuf.duration_pb2.Duration, builtin_interfaces.msg.Duration)
def convert_google_protobuf_duration_proto_to_builtin_interfaces_duration_message(
    proto_msg: google.protobuf.duration_pb2.Duration,
    ros_msg: builtin_interfaces.msg.Duration,
) -> None:
    """Converts from google.protobuf.Duration Protobuf messages to builtin_interfaces/Duration ROS messages."""
    ros_msg.sec = proto_msg.seconds
    ros_msg.nanosec = proto_msg.nanos


convert_proto_to_builtin_interfaces_duration = (
    convert_google_protobuf_duration_proto_to_builtin_interfaces_duration_message
)


@convert.register(builtin_interfaces.msg.Time, google.protobuf.timestamp_pb2.Timestamp)
def convert_builtin_interfaces_time_message_to_google_protobuf_timestamp_proto(
    ros_msg: builtin_interfaces.msg.Time,
    proto_msg: google.protobuf.timestamp_pb2.Timestamp,
) -> None:
    """Converts from builtin_interfaces/Time ROS messages to google.protobuf.Timestamp Protobuf messages."""
    proto_msg.seconds = ros_msg.sec
    proto_msg.nanos = ros_msg.nanosec


convert_builtin_interfaces_time_to_proto = convert_builtin_interfaces_time_message_to_google_protobuf_timestamp_proto


@convert.register(google.protobuf.timestamp_pb2.Timestamp, builtin_interfaces.msg.Time)
def convert_google_protobuf_timestamp_proto_to_builtin_interfaces_time_message(
    proto_msg: google.protobuf.timestamp_pb2.Timestamp,
    ros_msg: builtin_interfaces.msg.Time,
) -> None:
    """Converts from google.protobuf.Timestamp Protobuf messages to builtin_interfaces/Time ROS messages."""
    ros_msg.sec = proto_msg.seconds
    ros_msg.nanosec = proto_msg.nanos


convert_proto_to_builtin_interfaces_time = convert_google_protobuf_timestamp_proto_to_builtin_interfaces_time_message


@convert.register(std_msgs.msg.Float64, google.protobuf.wrappers_pb2.DoubleValue)
def convert_std_msgs_float64_message_to_google_protobuf_double_value_proto(
    ros_msg: std_msgs.msg.Float64,
    proto_msg: google.protobuf.wrappers_pb2.DoubleValue,
) -> None:
    """Converts from std_msgs/Float64 ROS messages to google.protobuf.DoubleValue Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_float64_to_proto = convert_std_msgs_float64_message_to_google_protobuf_double_value_proto


@convert.register(google.protobuf.wrappers_pb2.DoubleValue, std_msgs.msg.Float64)
def convert_google_protobuf_double_value_proto_to_std_msgs_float64_message(
    proto_msg: google.protobuf.wrappers_pb2.DoubleValue,
    ros_msg: std_msgs.msg.Float64,
) -> None:
    """Converts from google.protobuf.DoubleValue Protobuf messages to std_msgs/Float64 ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_float64 = convert_google_protobuf_double_value_proto_to_std_msgs_float64_message


@convert.register(std_msgs.msg.Float32, google.protobuf.wrappers_pb2.FloatValue)
def convert_std_msgs_float32_message_to_google_protobuf_float_value_proto(
    ros_msg: std_msgs.msg.Float32,
    proto_msg: google.protobuf.wrappers_pb2.FloatValue,
) -> None:
    """Converts from std_msgs/Float32 ROS messages to google.protobuf.FloatValue Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_float32_to_proto = convert_std_msgs_float32_message_to_google_protobuf_float_value_proto


@convert.register(google.protobuf.wrappers_pb2.FloatValue, std_msgs.msg.Float32)
def convert_google_protobuf_float_value_proto_to_std_msgs_float32_message(
    proto_msg: google.protobuf.wrappers_pb2.FloatValue,
    ros_msg: std_msgs.msg.Float32,
) -> None:
    """Converts from google.protobuf.FloatValue Protobuf messages to std_msgs/Float32 ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_float32 = convert_google_protobuf_float_value_proto_to_std_msgs_float32_message


@convert.register(std_msgs.msg.Int64, google.protobuf.wrappers_pb2.Int64Value)
def convert_std_msgs_int64_message_to_google_protobuf_int64_value_proto(
    ros_msg: std_msgs.msg.Int64,
    proto_msg: google.protobuf.wrappers_pb2.Int64Value,
) -> None:
    """Converts from std_msgs/Int64 ROS messages to google.protobuf.Int64Value Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_int64_to_proto = convert_std_msgs_int64_message_to_google_protobuf_int64_value_proto


@convert.register(google.protobuf.wrappers_pb2.Int64Value, std_msgs.msg.Int64)
def convert_google_protobuf_int64_value_proto_to_std_msgs_int64_message(
    proto_msg: google.protobuf.wrappers_pb2.Int64Value,
    ros_msg: std_msgs.msg.Int64,
) -> None:
    """Converts from google.protobuf.Int64Value Protobuf messages to std_msgs/Int64 ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_int64 = convert_google_protobuf_int64_value_proto_to_std_msgs_int64_message


@convert.register(std_msgs.msg.Int32, google.protobuf.wrappers_pb2.Int32Value)
def convert_std_msgs_int32_message_to_google_protobuf_int32_value_proto(
    ros_msg: std_msgs.msg.Int32,
    proto_msg: google.protobuf.wrappers_pb2.Int32Value,
) -> None:
    """Converts from std_msgs/Int32 ROS messages to google.protobuf.Int32Value Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_int32_to_proto = convert_std_msgs_int32_message_to_google_protobuf_int32_value_proto


@convert.register(google.protobuf.wrappers_pb2.Int32Value, std_msgs.msg.Int32)
def convert_google_protobuf_int32_value_proto_to_std_msgs_int32_message(
    proto_msg: google.protobuf.wrappers_pb2.Int32Value,
    ros_msg: std_msgs.msg.Int32,
) -> None:
    """Converts from google.protobuf.Int32Value Protobuf messages to std_msgs/Int32 ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_int32 = convert_google_protobuf_int32_value_proto_to_std_msgs_int32_message


@convert.register(std_msgs.msg.UInt64, google.protobuf.wrappers_pb2.UInt64Value)
def convert_std_msgs_uint64_message_to_google_protobuf_uint64_value_proto(
    ros_msg: std_msgs.msg.UInt64,
    proto_msg: google.protobuf.wrappers_pb2.UInt64Value,
) -> None:
    """Converts from std_msgs/UInt64 ROS messages to google.protobuf.UInt64Value Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_uint64_to_proto = convert_std_msgs_uint64_message_to_google_protobuf_uint64_value_proto


@convert.register(google.protobuf.wrappers_pb2.UInt64Value, std_msgs.msg.UInt64)
def convert_google_protobuf_uint64_value_proto_to_std_msgs_uint64_message(
    proto_msg: google.protobuf.wrappers_pb2.UInt64Value,
    ros_msg: std_msgs.msg.UInt64,
) -> None:
    """Converts from google.protobuf.UInt64Value Protobuf messages to std_msgs/UInt64 ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_uint64 = convert_google_protobuf_uint64_value_proto_to_std_msgs_uint64_message


@convert.register(std_msgs.msg.UInt32, google.protobuf.wrappers_pb2.UInt32Value)
def convert_std_msgs_uint32_message_to_google_protobuf_uint32_value_proto(
    ros_msg: std_msgs.msg.UInt32,
    proto_msg: google.protobuf.wrappers_pb2.UInt32Value,
) -> None:
    """Converts from std_msgs/UInt32 ROS messages to google.protobuf.UInt32Value Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_uint32_to_proto = convert_std_msgs_uint32_message_to_google_protobuf_uint32_value_proto


@convert.register(google.protobuf.wrappers_pb2.UInt32Value, std_msgs.msg.UInt32)
def convert_google_protobuf_uint32_value_proto_to_std_msgs_uint32_message(
    proto_msg: google.protobuf.wrappers_pb2.UInt32Value,
    ros_msg: std_msgs.msg.UInt32,
) -> None:
    """Converts from google.protobuf.UInt32Value Protobuf messages to std_msgs/UInt32 ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_uint32 = convert_google_protobuf_uint32_value_proto_to_std_msgs_uint32_message


@convert.register(std_msgs.msg.Bool, google.protobuf.wrappers_pb2.BoolValue)
def convert_std_msgs_bool_message_to_google_protobuf_bool_value_proto(
    ros_msg: std_msgs.msg.Bool,
    proto_msg: google.protobuf.wrappers_pb2.BoolValue,
) -> None:
    """Converts from std_msgs/Bool ROS messages to google.protobuf.BoolValue Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_bool_to_proto = convert_std_msgs_bool_message_to_google_protobuf_bool_value_proto


@convert.register(google.protobuf.wrappers_pb2.BoolValue, std_msgs.msg.Bool)
def convert_google_protobuf_bool_value_proto_to_std_msgs_bool_message(
    proto_msg: google.protobuf.wrappers_pb2.BoolValue,
    ros_msg: std_msgs.msg.Bool,
) -> None:
    """Converts from google.protobuf.BoolValue Protobuf messages to std_msgs/Bool ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_bool = convert_google_protobuf_bool_value_proto_to_std_msgs_bool_message


@convert.register(std_msgs.msg.String, google.protobuf.wrappers_pb2.StringValue)
def convert_std_msgs_string_message_to_google_protobuf_string_value_proto(
    ros_msg: std_msgs.msg.String,
    proto_msg: google.protobuf.wrappers_pb2.StringValue,
) -> None:
    """Converts from std_msgs/String ROS messages to google.protobuf.StringValue Protobuf messages."""
    proto_msg.value = ros_msg.data


convert_std_msgs_string_to_proto = convert_std_msgs_string_message_to_google_protobuf_string_value_proto


@convert.register(google.protobuf.wrappers_pb2.StringValue, std_msgs.msg.String)
def convert_google_protobuf_string_value_proto_to_std_msgs_string_message(
    proto_msg: google.protobuf.wrappers_pb2.StringValue,
    ros_msg: std_msgs.msg.String,
) -> None:
    """Converts from google.protobuf.StringValue Protobuf messages to std_msgs/String ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_std_msgs_string = convert_google_protobuf_string_value_proto_to_std_msgs_string_message


@convert.register(proto2ros.msg.Bytes, google.protobuf.wrappers_pb2.BytesValue)
def convert_proto2ros_bytes_message_to_google_protobuf_bytes_value_proto(
    ros_msg: proto2ros.msg.Bytes,
    proto_msg: google.protobuf.wrappers_pb2.BytesValue,
) -> None:
    """Converts from proto2ros/Bytes ROS messages to google.protobuf.BytesValue Protobuf messages."""
    proto_msg.value = ros_msg.data.tobytes()


convert_proto2ros_bytes_to_proto = convert_proto2ros_bytes_message_to_google_protobuf_bytes_value_proto


@convert.register(google.protobuf.wrappers_pb2.BytesValue, proto2ros.msg.Bytes)
def convert_google_protobuf_bytes_value_proto_to_proto2ros_bytes_message(
    proto_msg: google.protobuf.wrappers_pb2.BytesValue,
    ros_msg: proto2ros.msg.Bytes,
) -> None:
    """Converts from google.protobuf.BytesValue Protobuf messages to proto2ros/Bytes ROS messages."""
    ros_msg.data = proto_msg.value


convert_proto_to_proto2ros_bytes = convert_google_protobuf_bytes_value_proto_to_proto2ros_bytes_message


@convert.register(proto2ros.msg.Value, google.protobuf.struct_pb2.Value)
def convert_proto2ros_value_message_to_google_protobuf_value_proto(
    ros_msg: proto2ros.msg.Value,
    proto_msg: google.protobuf.struct_pb2.Value,
) -> None:
    """Converts from proto2ros/Value ROS messages to google.protobuf.Value Protobuf messages."""
    if ros_msg.kind == proto2ros.msg.Value.NUMBER_VALUE_SET:
        proto_msg.number_value = ros_msg.number_value
    elif ros_msg.kind == proto2ros.msg.Value.STRING_VALUE_SET:
        proto_msg.string_value = ros_msg.string_value
    elif ros_msg.kind == proto2ros.msg.Value.BOOL_VALUE_SET:
        proto_msg.bool_value = ros_msg.bool_value
    elif ros_msg.kind == proto2ros.msg.Value.STRUCT_VALUE_SET:
        if proto_msg.struct_value.type_name != "proto2ros/Struct":
            raise ValueError(
                f"expected proto2ros/Struct message for struct_value member, got {proto_msg.struct_value.type}",
            )
        typed_field_message = rclpy.serialization.deserialize_message(
            proto_msg.struct_value.value.tobytes(),
            proto2ros.msg.Struct,
        )
        convert_proto2ros_struct_message_to_google_protobuf_struct_proto(
            typed_field_message,
            proto_msg.struct_value,
        )
    elif ros_msg.kind == proto2ros.msg.Value.LIST_VALUE_SET:
        if proto_msg.list_value.type_name != "proto2ros/List":
            raise ValueError(
                f"expected proto2ros/Struct message for list_value member, got {proto_msg.list_value.type}",
            )
        typed_field_message = rclpy.serialization.deserialize_message(
            proto_msg.list_value.value.tobytes(),
            proto2ros.msg.List,
        )
        convert_proto2ros_list_message_to_google_protobuf_list_value_proto(
            typed_field_message,
            proto_msg.list_value,
        )
    elif ros_msg.kind == proto2ros.msg.Value.NO_VALUE_SET:
        proto_msg.null_value = google.protobuf.struct_pb2.NullValue.NULL_VALUE
    else:
        raise ValueError(f"unexpected value in kind member: {ros_msg.kind}")


convert_proto2ros_value_to_proto = convert_proto2ros_value_message_to_google_protobuf_value_proto


@convert.register(google.protobuf.struct_pb2.Value, proto2ros.msg.Value)
def convert_google_protobuf_value_proto_to_proto2ros_value_message(
    proto_msg: google.protobuf.struct_pb2.Value,
    ros_msg: proto2ros.msg.Value,
) -> None:
    """Converts from google.protobuf.Value Protobuf messages to proto2ros/Value ROS messages."""
    which = proto_msg.WhichOneOf("kind")
    if which == "null_value":
        ros_msg.kind = proto2ros.msg.Value.NO_VALUE_SET
    elif which == "number_value":
        ros_msg.number_value = proto_msg.number_value
        ros_msg.kind = proto2ros.msg.Value.NUMBER_VALUE_SET
    elif which == "string_value":
        ros_msg.string_value = proto_msg.string_value
        ros_msg.kind = proto2ros.msg.Value.STRING_VALUE_SET
    elif which == "bool_value":
        ros_msg.bool_value = proto_msg.bool_value
        ros_msg.kind = proto2ros.msg.Value.BOOL_VALUE_SET
    elif which == "struct_value":
        typed_struct_message = proto2ros.msg.Struct()
        convert_google_protobuf_struct_proto_to_proto2ros_struct_message(
            proto_msg.struct_value,
            typed_struct_message,
        )
        ros_msg.struct_value.value = rclpy.serialization.serialize_message(typed_struct_message)
        ros_msg.struct_value.type_name = "proto2ros/Struct"
        ros_msg.kind = proto2ros.msg.Value.STRUCT_VALUE_SET
    elif which == "list_value":
        typed_list_message = proto2ros.msg.List()
        convert_google_protobuf_list_value_proto_to_proto2ros_list_message(proto_msg.list_value, typed_list_message)
        ros_msg.list_value.value = rclpy.serialization.serialize_message(typed_list_message)
        ros_msg.list_value.type_name = "proto2ros/List"
        ros_msg.kind = proto2ros.msg.Value.LIST_VALUE_SET
    else:
        raise ValueError("unexpected one-of field: " + proto_msg.WhichOneOf("kind"))


convert_proto_to_proto2ros_value = convert_google_protobuf_value_proto_to_proto2ros_value_message


@convert.register(proto2ros.msg.List, google.protobuf.struct_pb2.ListValue)
def convert_proto2ros_list_message_to_google_protobuf_list_value_proto(
    ros_msg: proto2ros.msg.List,
    proto_msg: google.protobuf.struct_pb2.ListValue,
) -> None:
    """Converts from proto2ros/List ROS messages to google.protobuf.ListValue Protobuf messages."""
    proto_msg.Clear()
    for input_item in ros_msg.values:
        output_item = proto_msg.values.add()
        convert_proto2ros_value_message_to_google_protobuf_value_proto(input_item, output_item)


convert_proto2ros_list_to_proto = convert_proto2ros_list_message_to_google_protobuf_list_value_proto


@convert.register(google.protobuf.struct_pb2.ListValue, proto2ros.msg.List)
def convert_google_protobuf_list_value_proto_to_proto2ros_list_message(
    proto_msg: google.protobuf.struct_pb2.ListValue,
    ros_msg: proto2ros.msg.List,
) -> None:
    """Converts from google.protobuf.ListValue Protobuf messages to proto2ros/List ROS messages."""
    for input_item in proto_msg.values:
        output_item = proto2ros.msg.Value()
        convert_google_protobuf_value_proto_to_proto2ros_value_message(input_item, output_item)
        ros_msg.values.append(output_item)


convert_proto_to_proto2ros_list = convert_google_protobuf_list_value_proto_to_proto2ros_list_message


@convert.register(proto2ros.msg.Struct, google.protobuf.struct_pb2.Struct)
def convert_proto2ros_struct_message_to_google_protobuf_struct_proto(
    ros_msg: proto2ros.msg.Struct,
    proto_msg: google.protobuf.struct_pb2.Struct,
) -> None:
    """Converts from proto2ros/Struct ROS messages to google.protobuf.Struct Protobuf messages."""
    proto_msg.Clear()
    for field in ros_msg.fields:
        proto_msg.fields[field.key].CopyFrom(field.value)


convert_proto2ros_struct_to_proto = convert_proto2ros_struct_message_to_google_protobuf_struct_proto


@convert.register(google.protobuf.struct_pb2.Struct, proto2ros.msg.Struct)
def convert_google_protobuf_struct_proto_to_proto2ros_struct_message(
    proto_msg: google.protobuf.struct_pb2.Struct,
    ros_msg: proto2ros.msg.Struct,
) -> None:
    """Converts from google.protobuf.Struct Protobuf messages to proto2ros/Struct ROS messages."""
    for key, value in proto_msg.fields.items():
        field = proto2ros.msg.StructEntry(key=key)
        convert_google_protobuf_value_proto_to_proto2ros_value_message(value, field.value)
        ros_msg.fields.append(field)


convert_proto_to_proto2ros_struct = convert_google_protobuf_struct_proto_to_proto2ros_struct_message
