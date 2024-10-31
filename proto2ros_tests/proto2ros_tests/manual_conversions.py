import math

import bosdyn.api.geometry_pb2
import geometry_msgs.msg
import sensor_msgs.msg
import test_pb2

from proto2ros.conversions import convert


@convert.register(geometry_msgs.msg.Vector3, bosdyn.api.geometry_pb2.Vec3)
def convert_geometry_msgs_vector3_message_to_bosdyn_api_vec3_proto(
    ros_msg: geometry_msgs.msg.Vector3,
    proto_msg: bosdyn.api.geometry_pb2.Vec3,
) -> None:
    proto_msg.x = ros_msg.x
    proto_msg.y = ros_msg.y
    proto_msg.z = ros_msg.z


@convert.register(bosdyn.api.geometry_pb2.Vec3, geometry_msgs.msg.Vector3)
def convert_bosdyn_api_vec3_proto_to_geometry_msgs_vector3_message(
    proto_msg: bosdyn.api.geometry_pb2.Vec3,
    ros_msg: geometry_msgs.msg.Vector3,
) -> None:
    ros_msg.x = proto_msg.x
    ros_msg.y = proto_msg.y
    ros_msg.z = proto_msg.z


@convert.register(geometry_msgs.msg.Quaternion, bosdyn.api.geometry_pb2.Quaternion)
def convert_geometry_msgs_quaternion_message_to_bosdyn_api_quaternion_proto(
    ros_msg: geometry_msgs.msg.Quaternion,
    proto_msg: bosdyn.api.geometry_pb2.Quaternion,
) -> None:
    proto_msg.w = ros_msg.w
    proto_msg.x = ros_msg.x
    proto_msg.y = ros_msg.y
    proto_msg.z = ros_msg.z


@convert.register(bosdyn.api.geometry_pb2.Quaternion, geometry_msgs.msg.Quaternion)
def convert_bosdyn_api_quaternion_proto_to_geometry_msgs_quaternion_message(
    proto_msg: bosdyn.api.geometry_pb2.Quaternion,
    ros_msg: geometry_msgs.msg.Quaternion,
) -> None:
    ros_msg.w = proto_msg.w
    ros_msg.x = proto_msg.x
    ros_msg.y = proto_msg.y
    ros_msg.z = proto_msg.z


@convert.register(geometry_msgs.msg.Pose, bosdyn.api.geometry_pb2.SE3Pose)
def convert_geometry_msgs_pose_message_to_bosdyn_api_se3_pose_proto(
    ros_msg: geometry_msgs.msg.Pose,
    proto_msg: bosdyn.api.geometry_pb2.SE3Pose,
) -> None:
    convert_geometry_msgs_vector3_message_to_bosdyn_api_vec3_proto(ros_msg.position, proto_msg.position)
    convert_geometry_msgs_quaternion_message_to_bosdyn_api_quaternion_proto(ros_msg.orientation, proto_msg.rotation)


@convert.register(bosdyn.api.geometry_pb2.SE3Pose, geometry_msgs.msg.Pose)
def convert_bosdyn_api_se3_pose_proto_to_geometry_msgs_pose_message(
    proto_msg: bosdyn.api.geometry_pb2.SE3Pose,
    ros_msg: geometry_msgs.msg.Pose,
) -> None:
    convert_bosdyn_api_vec3_proto_to_geometry_msgs_vector3_message(proto_msg.position, ros_msg.position)
    convert_bosdyn_api_quaternion_proto_to_geometry_msgs_quaternion_message(proto_msg.rotation, ros_msg.orientation)


@convert.register(geometry_msgs.msg.Pose, bosdyn.api.geometry_pb2.SE2Pose)
def convert_geometry_msgs_pose_message_to_bosdyn_api_se2_pose_proto(
    ros_msg: geometry_msgs.msg.Pose,
    proto_msg: bosdyn.api.geometry_pb2.SE2Pose,
) -> None:
    proto_msg.position.x = ros_msg.position.x
    proto_msg.position.y = ros_msg.position.y
    proto_msg.angle = 2.0 * math.acos(ros_msg.orientation.w)


@convert.register(bosdyn.api.geometry_pb2.SE2Pose, geometry_msgs.msg.Pose)
def convert_bosdyn_api_se2_pose_proto_to_geometry_msgs_pose_message(
    proto_msg: bosdyn.api.geometry_pb2.SE2Pose,
    ros_msg: geometry_msgs.msg.Pose,
) -> None:
    ros_msg.position.x = proto_msg.position.x
    ros_msg.position.y = proto_msg.position.y
    ros_msg.orientation.w = math.cos(proto_msg.angle / 2.0)
    ros_msg.orientation.z = math.sin(proto_msg.angle / 2.0)


@convert.register(geometry_msgs.msg.Polygon, bosdyn.api.geometry_pb2.Polygon)
def convert_geometry_msgs_polygon_message_to_bosdyn_api_polygon_proto(
    ros_msg: geometry_msgs.msg.Polygon,
    proto_msg: bosdyn.api.geometry_pb2.Polygon,
) -> None:
    proto_msg.Clear()
    for point in ros_msg.points:
        vertex = proto_msg.vertexes.add()
        vertex.x = point.x
        vertex.y = point.y


@convert.register(bosdyn.api.geometry_pb2.Polygon, geometry_msgs.msg.Polygon)
def convert_bosdyn_api_polygon_proto_to_geometry_msgs_polygon_message(
    proto_msg: bosdyn.api.geometry_pb2.Polygon,
    ros_msg: geometry_msgs.msg.Polygon,
) -> None:
    ros_msg.points = [geometry_msgs.msg.Point32(x=vertex.x, y=vertex.y, z=0.0) for vertex in proto_msg.vertexes]


@convert.register(geometry_msgs.msg.Vector3, bosdyn.api.geometry_pb2.Circle)
def convert_geometry_msgs_vector3_message_to_bosdyn_api_circle_proto(
    ros_msg: geometry_msgs.msg.Vector3,
    proto_msg: bosdyn.api.geometry_pb2.Circle,
) -> None:
    proto_msg.center_pt.x = ros_msg.x
    proto_msg.center_pt.y = ros_msg.y
    proto_msg.radius = ros_msg.z


@convert.register(bosdyn.api.geometry_pb2.Circle, geometry_msgs.msg.Vector3)
def convert_bosdyn_api_circle_proto_to_geometry_msgs_vector3_message(
    proto_msg: bosdyn.api.geometry_pb2.Circle,
    ros_msg: geometry_msgs.msg.Vector3,
) -> None:
    ros_msg.x = proto_msg.center_pt.x
    ros_msg.y = proto_msg.center_pt.y
    ros_msg.z = proto_msg.radius


@convert.register(geometry_msgs.msg.Twist, bosdyn.api.geometry_pb2.SE3Velocity)
def convert_geometry_msgs_twist_message_to_bosdyn_api_se3_velocity_proto(
    ros_msg: geometry_msgs.msg.Twist,
    proto_msg: bosdyn.api.geometry_pb2.SE3Velocity,
) -> None:
    convert_geometry_msgs_vector3_message_to_bosdyn_api_vec3_proto(ros_msg.linear, proto_msg.linear)
    convert_geometry_msgs_vector3_message_to_bosdyn_api_vec3_proto(ros_msg.angular, proto_msg.angular)


@convert.register(bosdyn.api.geometry_pb2.SE3Velocity, geometry_msgs.msg.Twist)
def convert_bosdyn_api_se3_velocity_proto_to_geometry_msgs_twist_message(
    proto_msg: bosdyn.api.geometry_pb2.SE3Velocity,
    ros_msg: geometry_msgs.msg.Twist,
) -> None:
    convert_bosdyn_api_vec3_proto_to_geometry_msgs_vector3_message(proto_msg.linear, ros_msg.linear)
    convert_bosdyn_api_vec3_proto_to_geometry_msgs_vector3_message(proto_msg.angular, ros_msg.angular)


@convert.register(geometry_msgs.msg.Wrench, bosdyn.api.geometry_pb2.Wrench)
def convert_geometry_msgs_wrench_message_to_bosdyn_api_wrench_proto(
    ros_msg: geometry_msgs.msg.Wrench,
    proto_msg: bosdyn.api.geometry_pb2.Wrench,
) -> None:
    convert_geometry_msgs_vector3_message_to_bosdyn_api_vec3_proto(ros_msg.force, proto_msg.force)
    convert_geometry_msgs_vector3_message_to_bosdyn_api_vec3_proto(ros_msg.torque, proto_msg.torque)


@convert.register(bosdyn.api.geometry_pb2.Wrench, geometry_msgs.msg.Wrench)
def convert_bosdyn_api_wrench_proto_to_geometry_msgs_wrench_message(
    proto_msg: bosdyn.api.geometry_pb2.Wrench,
    ros_msg: geometry_msgs.msg.Wrench,
) -> None:
    convert_bosdyn_api_vec3_proto_to_geometry_msgs_vector3_message(proto_msg.force, ros_msg.force)
    convert_bosdyn_api_vec3_proto_to_geometry_msgs_vector3_message(proto_msg.torque, ros_msg.torque)


@convert.register(sensor_msgs.msg.Temperature, test_pb2.Temperature)
def convert_sensor_msgs_temperature_message_to_proto2ros_tests_temperature_proto(
    ros_msg: sensor_msgs.msg.Temperature,
    proto_msg: test_pb2.Temperature,
) -> None:
    proto_msg.scale = test_pb2.Temperature.Scale.CELSIUS
    proto_msg.value = ros_msg.temperature


@convert.register(test_pb2.Temperature, sensor_msgs.msg.Temperature)
def convert_proto2ros_tests_temperature_proto_to_sensor_msgs_temperature_message(
    proto_msg: test_pb2.Temperature,
    ros_msg: sensor_msgs.msg.Temperature,
) -> None:
    if proto_msg.scale == test_pb2.Temperature.Scale.KELVIN:
        ros_msg.temperature = proto_msg.value + 273
    elif proto_msg.scale == test_pb2.Temperature.Scale.FAHRENHEIT:
        ros_msg.temperature = (proto_msg.value - 32) * 5 / 9
    else:  # proto_msg.scale == test_pb2.Temperature.Scale.CELSIUS
        ros_msg.temperature = proto_msg.value
