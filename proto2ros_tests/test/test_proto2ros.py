# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

import filecmp
import math
import os
import pathlib

import bosdyn.api.geometry_pb2
import geometry_msgs.msg
import google.protobuf.type_pb2
import test_pb2

import proto2ros.msg
import proto2ros_tests.msg
from proto2ros_tests.conversions import convert


def test_message_generation() -> None:
    cmake_binary_dir = pathlib.Path(os.environ["CMAKE_BINARY_DIR"])
    gen_msg_dir = cmake_binary_dir / "proto2ros_generate" / "proto2ros_tests" / "msg"
    ref_msg_dir = pathlib.Path(__file__).resolve().parent / "generated"
    _, mismatch, errors = filecmp.cmpfiles(gen_msg_dir, ref_msg_dir, os.listdir(ref_msg_dir))
    assert not mismatch, mismatch
    assert not errors, errors


def test_message_mapping() -> None:
    assert not hasattr(proto2ros_tests.msg, "Temperature")
    assert not hasattr(proto2ros_tests.msg, "TemperatureScale")
    proto_request = test_pb2.HVACControlRequest()
    proto_request.air_flow_rate = 1000.0
    proto_request.temperature_setpoint.value = 77.0
    proto_request.temperature_setpoint.scale = test_pb2.Temperature.Scale.FAHRENHEIT
    ros_request = proto2ros_tests.msg.HVACControlRequest()
    convert(proto_request, ros_request)
    other_proto_request = test_pb2.HVACControlRequest()
    convert(ros_request, other_proto_request)
    assert proto_request.air_flow_rate == other_proto_request.air_flow_rate
    # sensor_msgs/Temperature messages are in the Celsius temperature scale
    assert other_proto_request.temperature_setpoint.value == 25.0
    assert other_proto_request.temperature_setpoint.scale == test_pb2.Temperature.Scale.CELSIUS


def test_recursive_messages() -> None:
    proto_fragment = test_pb2.Fragment()
    proto_fragment.payload = b"important data"
    proto_subfragment = test_pb2.Fragment()
    proto_subfragment.payload = b"important addendum"
    proto_fragment.nested.append(proto_subfragment)
    ros_fragment = proto2ros_tests.msg.Fragment()
    convert(proto_fragment, ros_fragment)
    assert ros_fragment.payload.tobytes() == proto_fragment.payload
    assert len(ros_fragment.nested) == len(proto_fragment.nested)
    other_proto_fragment = test_pb2.Fragment()
    convert(ros_fragment, other_proto_fragment)
    assert other_proto_fragment.payload == proto_fragment.payload
    assert len(other_proto_fragment.nested) == len(proto_fragment.nested)
    other_proto_subfragment = other_proto_fragment.nested[0]
    assert other_proto_subfragment.payload == proto_subfragment.payload


def test_circularly_dependent_messages() -> None:
    proto_value = test_pb2.Value()
    proto_pair_value = proto_value.dict.items["interval"]
    proto_pair_value.pair.first.number = -0.5
    proto_pair_value.pair.second.number = 0.5
    proto_list_value = proto_value.dict.items["range"]
    for number in (-0.1, 0.0, 0.1, -0.7, 0.3, 0.4):
        value = proto_list_value.list.values.add()
        value.number = number
    ros_value = proto2ros_tests.msg.Value()
    convert(proto_value, ros_value)
    other_proto_value = test_pb2.Value()
    convert(ros_value, other_proto_value)
    assert "interval" in other_proto_value.dict.items
    other_proto_pair_value = proto_value.dict.items["interval"]
    assert other_proto_pair_value.pair.first.number == proto_pair_value.pair.first.number
    assert other_proto_pair_value.pair.second.number == proto_pair_value.pair.second.number
    other_proto_list_value = proto_value.dict.items["range"]
    assert [v.number for v in other_proto_list_value.list.values] == [v.number for v in proto_list_value.list.values]


def test_messages_with_enums() -> None:
    proto_motion_request = test_pb2.MotionRequest()
    proto_motion_request.direction = test_pb2.MotionRequest.Direction.Forward
    proto_motion_request.speed = 1.0
    ros_motion_request = proto2ros_tests.msg.MotionRequest()
    convert(proto_motion_request, ros_motion_request)
    assert ros_motion_request.direction.value == proto_motion_request.direction
    assert ros_motion_request.speed == proto_motion_request.speed
    other_proto_motion_request = test_pb2.MotionRequest()
    convert(ros_motion_request, other_proto_motion_request)
    assert other_proto_motion_request.direction == proto_motion_request.direction
    assert other_proto_motion_request.speed == proto_motion_request.speed


def test_messages_with_nested_enums() -> None:
    proto_http_request = test_pb2.HTTP.Request()
    proto_http_request.method = test_pb2.HTTP.Method.PUT
    proto_http_request.uri = "https://proto2ros.xyz/post"
    ros_http_request = proto2ros_tests.msg.HTTPRequest()
    convert(proto_http_request, ros_http_request)
    assert ros_http_request.method.value == test_pb2.HTTP.Method.PUT
    assert ros_http_request.uri == proto_http_request.uri
    other_proto_http_request = test_pb2.HTTP.Request()
    convert(ros_http_request, other_proto_http_request)
    assert other_proto_http_request.method == proto_http_request.method
    assert other_proto_http_request.uri == proto_http_request.uri


def test_one_of_messages() -> None:
    proto_any_command = test_pb2.AnyCommand()
    proto_any_command.walk.distance = 1.0
    proto_any_command.walk.speed = 1.0

    ros_any_command = proto2ros_tests.msg.AnyCommand()
    convert(proto_any_command, ros_any_command)
    walk_set = proto2ros_tests.msg.AnyCommandOneOfCommands.COMMANDS_WALK_SET
    assert ros_any_command.commands.which == walk_set
    assert ros_any_command.commands.commands_choice == walk_set
    assert ros_any_command.commands.walk.distance == proto_any_command.walk.distance
    assert ros_any_command.commands.walk.speed == proto_any_command.walk.speed

    other_proto_any_command = test_pb2.AnyCommand()
    convert(ros_any_command, other_proto_any_command)
    assert other_proto_any_command.WhichOneof("commands") == "walk"
    assert other_proto_any_command.walk.distance == proto_any_command.walk.distance
    assert other_proto_any_command.walk.speed == proto_any_command.walk.speed


def test_one_of_empty_messages() -> None:
    proto_any_command = test_pb2.AnyCommand()
    proto_any_command.sit.SetInParent()

    ros_any_command = proto2ros_tests.msg.AnyCommand()
    convert(proto_any_command, ros_any_command)
    sit_set = proto2ros_tests.msg.AnyCommandOneOfCommands.COMMANDS_SIT_SET
    assert ros_any_command.commands.which == sit_set
    assert ros_any_command.commands.commands_choice == sit_set

    other_proto_any_command = test_pb2.AnyCommand()
    convert(ros_any_command, other_proto_any_command)
    assert other_proto_any_command.WhichOneof("commands") == "sit"


def test_messages_with_map_field() -> None:
    proto_diagnostic = test_pb2.Diagnostic()
    proto_diagnostic.severity = test_pb2.Diagnostic.Severity.FATAL
    proto_diagnostic.reason = "Localization estimate diverged, cannot recover"
    proto_diagnostic.attributes["origin"] = "localization subsystem"

    ros_diagnostic = proto2ros_tests.msg.Diagnostic()
    convert(proto_diagnostic, ros_diagnostic)
    assert ros_diagnostic.severity.value == proto_diagnostic.severity
    assert ros_diagnostic.reason == proto_diagnostic.reason
    assert len(ros_diagnostic.attributes) == 1
    assert ros_diagnostic.attributes[0].key == "origin"
    assert ros_diagnostic.attributes[0].value == "localization subsystem"

    other_proto_diagnostic = test_pb2.Diagnostic()
    convert(ros_diagnostic, other_proto_diagnostic)
    assert other_proto_diagnostic.severity == proto_diagnostic.severity
    assert other_proto_diagnostic.reason == proto_diagnostic.reason
    assert other_proto_diagnostic.attributes == proto_diagnostic.attributes


def test_messages_with_deprecated_fields() -> None:
    proto_remote_execution_request = test_pb2.RemoteExecutionRequest()
    proto_remote_execution_request.prompt = "grab bike seat"
    proto_remote_execution_request.timeout = 2
    proto_remote_execution_request.timeout_sec = 10.0

    ros_remote_execution_request = proto2ros_tests.msg.RemoteExecutionRequest()
    convert(proto_remote_execution_request, ros_remote_execution_request)
    assert ros_remote_execution_request.prompt == proto_remote_execution_request.prompt
    assert ros_remote_execution_request.timeout == proto_remote_execution_request.timeout
    assert ros_remote_execution_request.timeout_sec == proto_remote_execution_request.timeout_sec

    other_proto_remote_execution_request = test_pb2.RemoteExecutionRequest()
    convert(ros_remote_execution_request, other_proto_remote_execution_request)
    assert other_proto_remote_execution_request.prompt == proto_remote_execution_request.prompt
    assert other_proto_remote_execution_request.timeout == proto_remote_execution_request.timeout
    assert other_proto_remote_execution_request.timeout_sec == proto_remote_execution_request.timeout_sec


def test_redefined_messages() -> None:
    proto_remote_execution_result = test_pb2.RemoteExecutionResult()
    proto_remote_execution_result.ok = False
    proto_remote_execution_result.error.code = 255
    proto_remote_execution_result.error.reason = "interrupted"
    proto_remote_execution_result.error.traceback.append("<root>")

    ros_remote_execution_result = proto2ros_tests.msg.RemoteExecutionResult()
    convert(proto_remote_execution_result, ros_remote_execution_result)
    assert ros_remote_execution_result.ok == proto_remote_execution_result.ok
    assert ros_remote_execution_result.error.code == proto_remote_execution_result.error.code
    assert ros_remote_execution_result.error.reason == proto_remote_execution_result.error.reason
    assert len(ros_remote_execution_result.error.traceback) > 0
    assert ros_remote_execution_result.error.traceback[0] == proto_remote_execution_result.error.traceback[0]

    other_proto_remote_execution_result = test_pb2.RemoteExecutionResult()
    convert(ros_remote_execution_result, other_proto_remote_execution_result)
    assert other_proto_remote_execution_result.ok == proto_remote_execution_result.ok
    assert other_proto_remote_execution_result.error.code == proto_remote_execution_result.error.code
    assert other_proto_remote_execution_result.error.reason == proto_remote_execution_result.error.reason
    assert other_proto_remote_execution_result.error.traceback == proto_remote_execution_result.error.traceback


def test_messages_with_reserved_fields() -> None:
    proto_displacement = test_pb2.Displacement()
    proto_displacement.translation.x = 1.0
    proto_displacement.translation.y = 2.0
    proto_displacement.translation.z = 3.0

    ros_displacement = proto2ros_tests.msg.Displacement()
    convert(proto_displacement, ros_displacement)
    assert ros_displacement.translation.x == proto_displacement.translation.x
    assert ros_displacement.translation.y == proto_displacement.translation.y
    assert ros_displacement.translation.z == proto_displacement.translation.z
    assert not hasattr(ros_displacement, "rotation")

    other_proto_displacement = test_pb2.Displacement()
    convert(ros_displacement, other_proto_displacement)
    assert other_proto_displacement.translation.x == proto_displacement.translation.x
    assert other_proto_displacement.translation.y == proto_displacement.translation.y
    assert other_proto_displacement.translation.z == proto_displacement.translation.z


def test_message_forwarding() -> None:
    proto_camera_info = test_pb2.CameraInfo()
    proto_camera_info.height = 720
    proto_camera_info.width = 1280
    proto_camera_info.K.rows = 3
    proto_camera_info.K.cols = 3
    proto_camera_info.K.data[:] = [2000, 0, 800, 0, 2000, 800, 0, 0, 1]
    proto_camera_info.R.rows = 3
    proto_camera_info.R.cols = 3
    proto_camera_info.R.data[:] = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    proto_camera_info.P.rows = 3
    proto_camera_info.P.cols = 4
    proto_camera_info.P.data[:] = [2000, 0, 800, 0, 0, 2000, 800, 0, 0, 0, 0, 1]
    proto_camera_info.distortion_model.type = test_pb2.CameraInfo.DistortionModel.Type.PLUMB_BOB
    proto_camera_info.distortion_model.coefficients[:] = [-0.2, -0.4, -0.0001, -0.0001, 0]

    ros_camera_info = proto2ros_tests.msg.CameraInfo()
    convert(proto_camera_info, ros_camera_info)
    assert ros_camera_info.height == proto_camera_info.height
    assert ros_camera_info.width == proto_camera_info.width
    assert ros_camera_info.k.rows == proto_camera_info.K.rows
    assert ros_camera_info.k.cols == proto_camera_info.K.cols
    assert list(ros_camera_info.k.data) == proto_camera_info.K.data
    assert ros_camera_info.r.rows == proto_camera_info.R.rows
    assert ros_camera_info.r.cols == proto_camera_info.R.cols
    assert list(ros_camera_info.r.data) == proto_camera_info.R.data
    assert ros_camera_info.p.rows == proto_camera_info.P.rows
    assert ros_camera_info.p.cols == proto_camera_info.P.cols
    assert list(ros_camera_info.p.data) == proto_camera_info.P.data
    assert ros_camera_info.distortion_model.type.value == proto_camera_info.distortion_model.type
    assert list(ros_camera_info.distortion_model.coefficients) == proto_camera_info.distortion_model.coefficients

    other_proto_camera_info = test_pb2.CameraInfo()
    convert(ros_camera_info, other_proto_camera_info)
    assert other_proto_camera_info.height == proto_camera_info.height
    assert other_proto_camera_info.width == proto_camera_info.width
    assert other_proto_camera_info.K.rows == proto_camera_info.K.rows
    assert other_proto_camera_info.K.cols == proto_camera_info.K.cols
    assert other_proto_camera_info.K.data == proto_camera_info.K.data
    assert other_proto_camera_info.R.rows == proto_camera_info.R.rows
    assert other_proto_camera_info.R.cols == proto_camera_info.R.cols
    assert other_proto_camera_info.R.data == proto_camera_info.R.data
    assert other_proto_camera_info.P.rows == proto_camera_info.P.rows
    assert other_proto_camera_info.P.cols == proto_camera_info.P.cols
    assert other_proto_camera_info.P.data == proto_camera_info.P.data
    assert other_proto_camera_info.distortion_model.type == proto_camera_info.distortion_model.type
    assert other_proto_camera_info.distortion_model.coefficients == proto_camera_info.distortion_model.coefficients


def test_messages_with_submessage_map_field() -> None:
    proto_map = test_pb2.Map()
    proto_fragment = proto_map.submaps[13]
    proto_fragment.height = 20
    proto_fragment.width = 20
    proto_fragment.grid = b"\x00" * 20 * 20

    ros_map = proto2ros_tests.msg.Map()
    convert(proto_map, ros_map)
    assert len(ros_map.submaps) == 1
    assert ros_map.submaps[0].key == 13
    ros_fragment = ros_map.submaps[0].value
    assert ros_fragment.height == proto_fragment.height
    assert ros_fragment.width == proto_fragment.width
    assert ros_fragment.grid.tobytes() == proto_fragment.grid

    other_proto_map = test_pb2.Map()
    convert(ros_map, other_proto_map)
    assert len(other_proto_map.submaps)
    other_proto_fragment = other_proto_map.submaps[13]
    assert other_proto_fragment.height == proto_fragment.height
    assert other_proto_fragment.width == proto_fragment.width
    assert other_proto_fragment.grid == proto_fragment.grid


def test_messages_with_any_fields() -> None:
    proto_matrix = test_pb2.Matrix()
    proto_matrix.rows = 1
    proto_matrix.cols = 1
    proto_matrix.data.append(0)

    proto_request = test_pb2.RTTIQueryRequest()
    proto_request.msg.Pack(proto_matrix)

    ros_request = proto2ros_tests.msg.RTTIQueryRequest()
    convert(proto_request, ros_request)
    assert isinstance(ros_request.msg, proto2ros.msg.AnyProto)

    unpacked_proto_matrix = test_pb2.Matrix()
    convert(ros_request.msg, unpacked_proto_matrix)
    assert unpacked_proto_matrix.rows == proto_matrix.rows
    assert unpacked_proto_matrix.cols == proto_matrix.cols
    assert unpacked_proto_matrix.data == proto_matrix.data

    other_proto_request = test_pb2.RTTIQueryRequest()
    convert(ros_request, other_proto_request)

    other_unpacked_proto_matrix = test_pb2.Matrix()
    other_proto_request.msg.Unpack(other_unpacked_proto_matrix)
    assert other_unpacked_proto_matrix.rows == proto_matrix.rows
    assert other_unpacked_proto_matrix.cols == proto_matrix.cols
    assert other_unpacked_proto_matrix.data == proto_matrix.data


def test_messages_with_unknown_type_fields() -> None:
    proto_result = test_pb2.RTTIQueryResult()
    proto_result.type.name = "SomeMessage"

    ros_result = proto2ros_tests.msg.RTTIQueryResult()
    convert(proto_result, ros_result)
    assert isinstance(ros_result.type, proto2ros.msg.AnyProto)

    unpacked_proto_type = google.protobuf.type_pb2.Type()
    convert(ros_result.type, unpacked_proto_type)
    assert unpacked_proto_type.name == proto_result.type.name

    other_proto_result = test_pb2.RTTIQueryResult()
    convert(ros_result, other_proto_result)
    assert other_proto_result.type.name == proto_result.type.name


def test_messages_with_expanded_any_fields() -> None:
    proto_target = bosdyn.api.geometry_pb2.SE2Pose()
    proto_target.position.x = 1.0
    proto_target.position.y = -1.0
    proto_target.angle = math.pi

    proto_roi = bosdyn.api.geometry_pb2.Polygon()
    for dx in (-0.5, 0.5):
        for dy in (-0.5, 0.5):
            vertex = proto_roi.vertexes.add()
            vertex.x = proto_target.position.x + dx
            vertex.y = proto_target.position.y + dy

    proto_goal = test_pb2.Goal()
    proto_goal.target.Pack(proto_target)
    proto_goal.roi.Pack(proto_roi)

    ros_goal = proto2ros_tests.msg.Goal()
    convert(proto_goal, ros_goal)
    assert isinstance(ros_goal.target, geometry_msgs.msg.Pose)
    assert isinstance(ros_goal.roi, proto2ros.msg.Any)
    assert ros_goal.target.position.x == proto_target.position.x
    assert ros_goal.target.position.y == proto_target.position.y
    assert ros_goal.roi.type_name == "geometry_msgs/Polygon"

    other_proto_goal = test_pb2.Goal()
    convert(ros_goal, other_proto_goal)
    other_proto_target = bosdyn.api.geometry_pb2.SE2Pose()
    other_proto_goal.target.Unpack(other_proto_target)
    assert proto_target.position.x == other_proto_target.position.x
    assert proto_target.position.y == other_proto_target.position.y
    assert proto_target.angle == other_proto_target.angle

    other_proto_roi = bosdyn.api.geometry_pb2.Polygon()
    other_proto_goal.roi.Unpack(other_proto_roi)
    assert len(other_proto_roi.vertexes) == 4
    for a, b in zip(proto_roi.vertexes, other_proto_roi.vertexes, strict=True):
        assert a.x == b.x and a.y == b.y
