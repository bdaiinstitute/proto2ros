// Copyright (c) 2024 Boston Dynamics AI Institute LLC. All rights reserved.
// NOLINTBEGIN(readability-magic-numbers,readability-function-cognitive-complexity,cppcoreguidelines-pro-type-reinterpret-cast)
#include <bosdyn/api/geometry.pb.h>
#include <gtest/gtest.h>
#include <test.pb.h>

#include <cmath>
#include <string_view>

#include <proto2ros/conversions.hpp>
#include <proto2ros_tests/conversions.hpp>
#include <proto2ros_tests/msg/any_command.hpp>
#include <proto2ros_tests/msg/diagnostic.hpp>
#include <proto2ros_tests/msg/fragment.hpp>
#include <proto2ros_tests/msg/goal.hpp>
#include <proto2ros_tests/msg/http_request.hpp>
#include <proto2ros_tests/msg/hvac_control_request.hpp>
#include <proto2ros_tests/msg/remote_execution_request.hpp>
#include <proto2ros_tests/msg/remote_execution_result.hpp>
#include <proto2ros_tests/msg/value.hpp>

using proto2ros::conversions::Convert;
using proto2ros_tests::conversions::Convert;

TEST(Proto2RosTesting, MessageMapping) {
  auto proto_request = proto2ros_tests::HVACControlRequest();
  proto_request.set_air_flow_rate(1000.0);
  auto* setpoint = proto_request.mutable_temperature_setpoint();
  setpoint->set_value(77.0);
  setpoint->set_scale(proto2ros_tests::Temperature::FAHRENHEIT);

  auto ros_request = proto2ros_tests::msg::HVACControlRequest();
  Convert(proto_request, &ros_request);

  auto other_proto_request = proto2ros_tests::HVACControlRequest();
  Convert(ros_request, &other_proto_request);

  EXPECT_DOUBLE_EQ(proto_request.air_flow_rate(), other_proto_request.air_flow_rate());
  // sensor_msgs/Temperature messages are in the Celsius temperature scale
  EXPECT_DOUBLE_EQ(other_proto_request.temperature_setpoint().value(), 25.0);
  EXPECT_EQ(other_proto_request.temperature_setpoint().scale(), proto2ros_tests::Temperature::CELSIUS);
}

TEST(Proto2RosTesting, RecursiveMessages) {
  auto proto_fragment = proto2ros_tests::Fragment();
  proto_fragment.set_payload("important data");
  auto* proto_subfragment = proto_fragment.add_nested();
  proto_subfragment->set_payload("important addendum");

  auto ros_fragment = proto2ros_tests::msg::Fragment();
  Convert(proto_fragment, &ros_fragment);

  const auto payload =
      std::string_view{reinterpret_cast<char*>(ros_fragment.payload.data()), ros_fragment.payload.size()};
  EXPECT_EQ(payload, proto_fragment.payload());
  EXPECT_EQ(ros_fragment.nested.size(), static_cast<size_t>(proto_fragment.nested_size()));

  auto other_proto_fragment = proto2ros_tests::Fragment();
  Convert(ros_fragment, &other_proto_fragment);
  EXPECT_EQ(other_proto_fragment.payload(), proto_fragment.payload());
  ASSERT_EQ(other_proto_fragment.nested_size(), proto_fragment.nested_size());
  const auto& other_proto_subfragment = other_proto_fragment.nested(0);
  EXPECT_EQ(other_proto_subfragment.payload(), proto_subfragment->payload());
}

TEST(Proto2RosTesting, CircularlyDependentMessages) {
  auto proto_value = proto2ros_tests::Value();
  auto* proto_items = proto_value.mutable_dict()->mutable_items();
  auto* proto_pair = (*proto_items)["interval"].mutable_pair();
  proto_pair->mutable_first()->set_number(-0.5F);
  proto_pair->mutable_second()->set_number(0.5F);
  auto* proto_list = (*proto_items)["range"].mutable_list();
  for (const float number : {-0.1F, 0.0F, 0.1F, -0.7F, 0.3F, 0.4F}) {
    proto_list->add_values()->set_number(number);
  }

  auto ros_value = proto2ros_tests::msg::Value();
  Convert(proto_value, &ros_value);

  auto other_proto_value = proto2ros_tests::Value();
  Convert(ros_value, &other_proto_value);

  const auto& other_proto_items = other_proto_value.dict().items();
  EXPECT_TRUE(other_proto_items.count("interval"));
  const auto& other_proto_pair = other_proto_items.at("interval").pair();
  EXPECT_EQ(other_proto_pair.first().number(), proto_pair->first().number());
  EXPECT_EQ(other_proto_pair.second().number(), proto_pair->second().number());
  EXPECT_TRUE(other_proto_items.count("range"));
  const auto& other_proto_list = other_proto_items.at("range").list();
  ASSERT_EQ(other_proto_list.values_size(), proto_list->values_size());
  for (int i = 0; i < proto_list->values_size(); ++i) {
    EXPECT_EQ(other_proto_list.values(i).number(), proto_list->values(i).number());
  }
}

TEST(Proto2RosTesting, MessagesWithEnums) {
  auto proto_motion_request = proto2ros_tests::MotionRequest();
  proto_motion_request.set_direction(proto2ros_tests::MotionRequest::Forward);
  proto_motion_request.set_speed(1.0);
  auto ros_motion_request = proto2ros_tests::msg::MotionRequest();
  Convert(proto_motion_request, &ros_motion_request);
  EXPECT_EQ(ros_motion_request.direction.value, proto_motion_request.direction());
  EXPECT_EQ(ros_motion_request.speed, proto_motion_request.speed());

  auto other_proto_motion_request = proto2ros_tests::MotionRequest();
  Convert(ros_motion_request, &other_proto_motion_request);
  EXPECT_EQ(other_proto_motion_request.direction(), proto_motion_request.direction());
  EXPECT_EQ(other_proto_motion_request.speed(), proto_motion_request.speed());
}

TEST(Proto2RosTesting, MessagesWithNestedEnums) {
  auto proto_http_request = proto2ros_tests::HTTP::Request();
  proto_http_request.set_method(proto2ros_tests::HTTP::PUT);
  proto_http_request.set_uri("https://proto2ros.xyz/post");

  auto ros_http_request = proto2ros_tests::msg::HTTPRequest();
  Convert(proto_http_request, &ros_http_request);
  EXPECT_EQ(ros_http_request.method.value, proto_http_request.method());
  EXPECT_EQ(ros_http_request.uri, proto_http_request.uri());

  auto other_proto_http_request = proto2ros_tests::HTTP::Request();
  Convert(ros_http_request, &other_proto_http_request);
  EXPECT_EQ(other_proto_http_request.method(), proto_http_request.method());
  EXPECT_EQ(other_proto_http_request.uri(), proto_http_request.uri());
}

TEST(Proto2RosTesting, OneOfMessages) {
  auto proto_any_command = proto2ros_tests::AnyCommand();
  proto_any_command.mutable_walk()->set_distance(1.0);
  proto_any_command.mutable_walk()->set_speed(1.0);

  auto ros_any_command = proto2ros_tests::msg::AnyCommand();
  Convert(proto_any_command, &ros_any_command);
  constexpr auto expected_choice = proto2ros_tests::msg::AnyCommandOneOfCommands::COMMANDS_WALK_SET;
  EXPECT_EQ(ros_any_command.commands.which, expected_choice);
  EXPECT_EQ(ros_any_command.commands.commands_choice, expected_choice);
  EXPECT_EQ(ros_any_command.commands.walk.distance, proto_any_command.walk().distance());
  EXPECT_EQ(ros_any_command.commands.walk.speed, proto_any_command.walk().speed());

  auto other_proto_any_command = proto2ros_tests::AnyCommand();
  Convert(ros_any_command, &other_proto_any_command);
  EXPECT_TRUE(other_proto_any_command.has_walk());
  EXPECT_EQ(other_proto_any_command.walk().distance(), proto_any_command.walk().distance());
  EXPECT_EQ(other_proto_any_command.walk().speed(), proto_any_command.walk().speed());
}

TEST(Proto2RosTesting, OneOfEmptyMessages) {
  auto proto_any_command = proto2ros_tests::AnyCommand();
  (void)proto_any_command.mutable_sit();

  auto ros_any_command = proto2ros_tests::msg::AnyCommand();
  Convert(proto_any_command, &ros_any_command);

  constexpr auto expected_choice = proto2ros_tests::msg::AnyCommandOneOfCommands::COMMANDS_SIT_SET;
  EXPECT_EQ(ros_any_command.commands.which, expected_choice);
  EXPECT_EQ(ros_any_command.commands.commands_choice, expected_choice);

  auto other_proto_any_command = proto2ros_tests::AnyCommand();
  Convert(ros_any_command, &other_proto_any_command);
  EXPECT_TRUE(other_proto_any_command.has_sit());
}

TEST(Proto2RosTesting, MessagesWithMapField) {
  auto proto_diagnostic = proto2ros_tests::Diagnostic();
  proto_diagnostic.set_severity(proto2ros_tests::Diagnostic::FATAL);
  proto_diagnostic.set_reason("Localization estimate diverged, cannot recover");
  auto& proto_attributes = *proto_diagnostic.mutable_attributes();
  proto_attributes["origin"] = "localization subsystem";

  auto ros_diagnostic = proto2ros_tests::msg::Diagnostic();
  Convert(proto_diagnostic, &ros_diagnostic);
  EXPECT_EQ(ros_diagnostic.severity.value, proto_diagnostic.severity());
  EXPECT_EQ(ros_diagnostic.reason, proto_diagnostic.reason());
  EXPECT_EQ(ros_diagnostic.reason, proto_diagnostic.reason());
  EXPECT_EQ(ros_diagnostic.attributes.size(), static_cast<size_t>(proto_attributes.size()));
  EXPECT_EQ(ros_diagnostic.attributes[0].key, "origin");
  EXPECT_EQ(ros_diagnostic.attributes[0].value, "localization subsystem");

  auto other_proto_diagnostic = proto2ros_tests::Diagnostic();
  Convert(ros_diagnostic, &other_proto_diagnostic);
  EXPECT_EQ(other_proto_diagnostic.severity(), proto_diagnostic.severity());
  EXPECT_EQ(other_proto_diagnostic.reason(), proto_diagnostic.reason());
  EXPECT_TRUE(other_proto_diagnostic.attributes().contains("origin"));
  EXPECT_EQ(other_proto_diagnostic.attributes().at("origin"), "localization subsystem");
}

TEST(Proto2RosTesting, MessagesWithDeprecatedFields) {
  auto proto_remote_execution_request = proto2ros_tests::RemoteExecutionRequest();
  proto_remote_execution_request.set_prompt("grab bike seat");
  proto_remote_execution_request.set_timeout(10000000000);
  proto_remote_execution_request.set_timeout_sec(10.0);

  auto ros_remote_execution_request = proto2ros_tests::msg::RemoteExecutionRequest();
  Convert(proto_remote_execution_request, &ros_remote_execution_request);
  EXPECT_EQ(ros_remote_execution_request.prompt, proto_remote_execution_request.prompt());
  EXPECT_EQ(ros_remote_execution_request.timeout, proto_remote_execution_request.timeout());
  EXPECT_EQ(ros_remote_execution_request.timeout_sec, proto_remote_execution_request.timeout_sec());

  auto other_proto_remote_execution_request = proto2ros_tests::RemoteExecutionRequest();
  Convert(ros_remote_execution_request, &other_proto_remote_execution_request);
  EXPECT_EQ(other_proto_remote_execution_request.prompt(), proto_remote_execution_request.prompt());
  EXPECT_EQ(other_proto_remote_execution_request.timeout(), proto_remote_execution_request.timeout());
  EXPECT_EQ(other_proto_remote_execution_request.timeout_sec(), proto_remote_execution_request.timeout_sec());
}

TEST(Proto2RosTesting, RedefinedMessages) {
  auto proto_remote_execution_result = proto2ros_tests::RemoteExecutionResult();
  proto_remote_execution_result.set_ok(false);
  auto* proto_remote_execution_error = proto_remote_execution_result.mutable_error();
  proto_remote_execution_error->set_code(255);
  proto_remote_execution_error->set_reason("interrupted");
  proto_remote_execution_error->add_traceback("<root>");

  auto ros_remote_execution_result = proto2ros_tests::msg::RemoteExecutionResult();
  Convert(proto_remote_execution_result, &ros_remote_execution_result);
  EXPECT_EQ(ros_remote_execution_result.ok, proto_remote_execution_result.ok());
  EXPECT_EQ(ros_remote_execution_result.error.code, proto_remote_execution_result.error().code());
  EXPECT_EQ(ros_remote_execution_result.error.reason, proto_remote_execution_result.error().reason());
  EXPECT_EQ(ros_remote_execution_result.error.traceback.size(),
            static_cast<size_t>(proto_remote_execution_error->traceback_size()));
  EXPECT_EQ(ros_remote_execution_result.error.traceback[0], proto_remote_execution_result.error().traceback(0));

  auto other_proto_remote_execution_result = proto2ros_tests::RemoteExecutionResult();
  Convert(ros_remote_execution_result, &other_proto_remote_execution_result);
  EXPECT_EQ(other_proto_remote_execution_result.ok(), proto_remote_execution_result.ok());
  EXPECT_EQ(other_proto_remote_execution_result.error().code(), proto_remote_execution_result.error().code());
  EXPECT_EQ(other_proto_remote_execution_result.error().reason(), proto_remote_execution_result.error().reason());
  EXPECT_EQ(other_proto_remote_execution_result.error().traceback_size(),
            proto_remote_execution_error->traceback_size());
  EXPECT_EQ(other_proto_remote_execution_result.error().traceback(0),
            proto_remote_execution_result.error().traceback(0));
}

namespace {
// NOLINTBEGIN(readability-identifier-naming)
template <class, class = void>
struct has_rotation_member : std::false_type {};

// specialization recognizes types that do have a nested ::type member:
template <class T>
struct has_rotation_member<T, std::void_t<decltype(std::declval<T>().rotation)>> : std::true_type {};

template <class T>
constexpr bool has_rotation_member_v = has_rotation_member<T>::value;
// NOLINTEND(readability-identifier-naming)
}  // namespace

TEST(Proto2RosTesting, MessagesWithReservedFields) {
  auto proto_displacement = proto2ros_tests::Displacement();
  proto_displacement.mutable_translation()->set_x(1.0);
  proto_displacement.mutable_translation()->set_y(2.0);
  proto_displacement.mutable_translation()->set_z(3.0);

  auto ros_displacement = proto2ros_tests::msg::Displacement();
  Convert(proto_displacement, &ros_displacement);
  EXPECT_EQ(ros_displacement.translation.x, proto_displacement.translation().x());
  EXPECT_EQ(ros_displacement.translation.y, proto_displacement.translation().y());
  EXPECT_EQ(ros_displacement.translation.z, proto_displacement.translation().z());
  static_assert(!has_rotation_member_v<decltype(ros_displacement)>);

  auto other_proto_displacement = proto2ros_tests::Displacement();
  Convert(ros_displacement, &other_proto_displacement);
  EXPECT_EQ(other_proto_displacement.translation().x(), proto_displacement.translation().x());
  EXPECT_EQ(other_proto_displacement.translation().y(), proto_displacement.translation().y());
  EXPECT_EQ(other_proto_displacement.translation().z(), proto_displacement.translation().z());
}

TEST(Proto2RosTesting, MessageForwarding) {
  auto proto_camera_info = proto2ros_tests::CameraInfo();
  proto_camera_info.set_height(720);
  proto_camera_info.set_width(1280);
  proto_camera_info.mutable_k()->set_rows(3);
  proto_camera_info.mutable_k()->set_cols(3);
  for (const double number : {2000.0, 0.0, 800.0, 0.0, 2000.0, 800.0, 0.0, 0.0, 1.0}) {
    proto_camera_info.mutable_k()->add_data(number);
  }
  proto_camera_info.mutable_r()->set_rows(3);
  proto_camera_info.mutable_r()->set_cols(3);
  for (const double number : {1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0}) {
    proto_camera_info.mutable_r()->add_data(number);
  }
  proto_camera_info.mutable_p()->set_rows(3);
  proto_camera_info.mutable_p()->set_cols(4);
  for (const double number : {2000.0, 0.0, 800.0, 0.0, 0.0, 2000.0, 800.0, 0.0, 0.0, 0.0, 0.0, 1.0}) {
    proto_camera_info.mutable_p()->add_data(number);
  }
  proto_camera_info.mutable_distortion_model()->set_type(proto2ros_tests::CameraInfo::DistortionModel::PLUMB_BOB);
  for (const double coeff : {-0.2, -0.4, -0.0001, -0.0001, 0.0}) {
    proto_camera_info.mutable_distortion_model()->add_coefficients(coeff);
  }

  auto ros_camera_info = proto2ros_tests::msg::CameraInfo();
  Convert(proto_camera_info, &ros_camera_info);
  EXPECT_EQ(ros_camera_info.height, proto_camera_info.height());
  EXPECT_EQ(ros_camera_info.width, proto_camera_info.width());
  EXPECT_EQ(ros_camera_info.k.rows, proto_camera_info.k().rows());
  EXPECT_EQ(ros_camera_info.k.cols, proto_camera_info.k().cols());
  EXPECT_EQ(ros_camera_info.k.data.size(), static_cast<size_t>(proto_camera_info.k().data_size()));
  for (size_t i = 0; i < ros_camera_info.k.data.size(); ++i) {
    EXPECT_EQ(ros_camera_info.k.data[i], proto_camera_info.k().data(i));
  }
  EXPECT_EQ(ros_camera_info.r.rows, proto_camera_info.r().rows());
  EXPECT_EQ(ros_camera_info.r.cols, proto_camera_info.r().cols());
  EXPECT_EQ(ros_camera_info.r.data.size(), static_cast<size_t>(proto_camera_info.r().data_size()));
  for (size_t i = 0; i < ros_camera_info.r.data.size(); ++i) {
    EXPECT_EQ(ros_camera_info.r.data[i], proto_camera_info.r().data(i));
  }
  EXPECT_EQ(ros_camera_info.p.rows, proto_camera_info.p().rows());
  EXPECT_EQ(ros_camera_info.p.cols, proto_camera_info.p().cols());
  EXPECT_EQ(ros_camera_info.p.data.size(), static_cast<size_t>(proto_camera_info.p().data_size()));
  for (size_t i = 0; i < ros_camera_info.p.data.size(); ++i) {
    EXPECT_EQ(ros_camera_info.p.data[i], proto_camera_info.p().data(i));
  }
  EXPECT_EQ(ros_camera_info.distortion_model.type.value, proto_camera_info.distortion_model().type());
  EXPECT_EQ(ros_camera_info.distortion_model.coefficients.size(),
            static_cast<size_t>(proto_camera_info.distortion_model().coefficients_size()));
  for (size_t i = 0; i < ros_camera_info.distortion_model.coefficients.size(); ++i) {
    EXPECT_EQ(ros_camera_info.distortion_model.coefficients[i], proto_camera_info.distortion_model().coefficients(i));
  }

  auto other_proto_camera_info = proto2ros_tests::CameraInfo();
  Convert(ros_camera_info, &other_proto_camera_info);
  EXPECT_EQ(other_proto_camera_info.height(), proto_camera_info.height());
  EXPECT_EQ(other_proto_camera_info.width(), proto_camera_info.width());
  EXPECT_EQ(other_proto_camera_info.k().rows(), proto_camera_info.k().rows());
  EXPECT_EQ(other_proto_camera_info.k().cols(), proto_camera_info.k().cols());
  EXPECT_EQ(other_proto_camera_info.k().data_size(), proto_camera_info.k().data_size());
  for (int i = 0; i < other_proto_camera_info.k().data_size(); ++i) {
    EXPECT_EQ(other_proto_camera_info.k().data(i), proto_camera_info.k().data(i));
  }
  EXPECT_EQ(other_proto_camera_info.r().rows(), proto_camera_info.r().rows());
  EXPECT_EQ(other_proto_camera_info.r().cols(), proto_camera_info.r().cols());
  EXPECT_EQ(other_proto_camera_info.r().data_size(), proto_camera_info.r().data_size());
  for (int i = 0; i < other_proto_camera_info.r().data_size(); ++i) {
    EXPECT_EQ(other_proto_camera_info.r().data(i), proto_camera_info.r().data(i));
  }
  EXPECT_EQ(other_proto_camera_info.p().rows(), proto_camera_info.p().rows());
  EXPECT_EQ(other_proto_camera_info.p().cols(), proto_camera_info.p().cols());
  EXPECT_EQ(other_proto_camera_info.p().data_size(), proto_camera_info.p().data_size());
  for (int i = 0; i < other_proto_camera_info.p().data_size(); ++i) {
    EXPECT_EQ(other_proto_camera_info.p().data(i), proto_camera_info.p().data(i));
  }
  EXPECT_EQ(other_proto_camera_info.distortion_model().type(), proto_camera_info.distortion_model().type());
  EXPECT_EQ(other_proto_camera_info.distortion_model().coefficients_size(),
            proto_camera_info.distortion_model().coefficients_size());
  for (int i = 0; i < other_proto_camera_info.distortion_model().coefficients_size(); ++i) {
    EXPECT_EQ(other_proto_camera_info.distortion_model().coefficients(i),
              proto_camera_info.distortion_model().coefficients(i));
  }
}

TEST(Proto2RosTesting, MessagesWithSubMessageMapField) {
  auto proto_map = proto2ros_tests::Map();
  auto& proto_submaps = *proto_map.mutable_submaps();
  auto& proto_fragment = proto_submaps[13];
  proto_fragment.set_height(20);
  proto_fragment.set_width(20);
  auto* proto_grid = proto_fragment.mutable_grid();
  proto_grid->resize(20UL * 20UL, '\0');

  auto ros_map = proto2ros_tests::msg::Map();
  Convert(proto_map, &ros_map);
  EXPECT_EQ(ros_map.submaps.size(), static_cast<size_t>(proto_submaps.size()));
  EXPECT_EQ(ros_map.submaps[0].key, 13);
  auto& ros_fragment = ros_map.submaps[0].value;
  EXPECT_EQ(ros_fragment.height, proto_fragment.height());
  EXPECT_EQ(ros_fragment.width, proto_fragment.width());
  EXPECT_EQ(ros_fragment.grid.size(), static_cast<size_t>(proto_grid->size()));
  const auto grid = std::string_view{reinterpret_cast<char*>(ros_fragment.grid.data()), ros_fragment.grid.size()};
  EXPECT_EQ(grid, proto_fragment.grid());

  auto other_proto_map = proto2ros_tests::Map();
  Convert(ros_map, &other_proto_map);
  EXPECT_TRUE(other_proto_map.submaps().contains(13));
  const auto& other_proto_fragment = other_proto_map.submaps().at(13);
  EXPECT_EQ(other_proto_fragment.height(), proto_fragment.height());
  EXPECT_EQ(other_proto_fragment.width(), proto_fragment.width());
  EXPECT_EQ(other_proto_fragment.grid(), proto_fragment.grid());
}

TEST(Proto2RosTesting, MessagesWithAnyFields) {
  auto proto_matrix = proto2ros_tests::Matrix();
  proto_matrix.set_rows(1);
  proto_matrix.set_cols(1);
  proto_matrix.add_data(0.0);

  auto proto_request = proto2ros_tests::RTTIQueryRequest();
  proto_request.mutable_msg()->PackFrom(proto_matrix);

  auto ros_request = proto2ros_tests::msg::RTTIQueryRequest();
  Convert(proto_request, &ros_request);

  auto other_proto_request = proto2ros_tests::RTTIQueryRequest();
  Convert(ros_request, &other_proto_request);

  auto other_unpacked_proto_matrix = proto2ros_tests::Matrix();
  EXPECT_TRUE(other_proto_request.msg().UnpackTo(&other_unpacked_proto_matrix));

  EXPECT_EQ(other_unpacked_proto_matrix.rows(), proto_matrix.rows());
  EXPECT_EQ(other_unpacked_proto_matrix.cols(), proto_matrix.cols());
  EXPECT_EQ(other_unpacked_proto_matrix.data_size(), proto_matrix.data_size());
  EXPECT_EQ(other_unpacked_proto_matrix.data(0), proto_matrix.data(0));
}

TEST(Proto2RosTesting, MessagesWithUnknownTypeFields) {
  auto proto_result = proto2ros_tests::RTTIQueryResult();
  proto_result.mutable_type()->set_name("SomeMessage");

  auto ros_result = proto2ros_tests::msg::RTTIQueryResult();
  Convert(proto_result, &ros_result);

  auto unpacked_proto_type = google::protobuf::Type();
  Convert(ros_result.type, &unpacked_proto_type);
  EXPECT_EQ(unpacked_proto_type.name(), proto_result.type().name());

  auto other_proto_result = proto2ros_tests::RTTIQueryResult();
  Convert(ros_result, &other_proto_result);
  EXPECT_EQ(other_proto_result.type().name(), proto_result.type().name());
}

TEST(Proto2RosTesting, MessagesWithExpandedAnyFields) {
  auto proto_target = bosdyn::api::SE2Pose();
  proto_target.mutable_position()->set_x(1.0);
  proto_target.mutable_position()->set_y(-1.0);
  proto_target.set_angle(M_PI);

  auto proto_roi = bosdyn::api::Polygon();
  for (const double dx : {-0.5, 0.5}) {
    for (const double dy : {-0.5, 0.5}) {
      auto* vertex = proto_roi.add_vertexes();
      vertex->set_x(proto_target.position().x() + dx);
      vertex->set_y(proto_target.position().y() + dy);
    }
  }

  auto proto_goal = proto2ros_tests::Goal();
  proto_goal.mutable_target()->PackFrom(proto_target);
  proto_goal.mutable_roi()->PackFrom(proto_roi);

  auto ros_goal = proto2ros_tests::msg::Goal();
  Convert(proto_goal, &ros_goal);

  EXPECT_EQ(ros_goal.target.position.x, proto_target.position().x());
  EXPECT_EQ(ros_goal.target.position.y, proto_target.position().y());
  EXPECT_EQ(ros_goal.roi.type_name, "geometry_msgs/Polygon");

  auto other_proto_goal = proto2ros_tests::Goal();
  Convert(ros_goal, &other_proto_goal);

  auto other_proto_target = bosdyn::api::SE2Pose();
  EXPECT_TRUE(other_proto_goal.target().UnpackTo(&other_proto_target));

  EXPECT_EQ(proto_target.position().x(), other_proto_target.position().x());
  EXPECT_EQ(proto_target.position().y(), other_proto_target.position().y());
  EXPECT_EQ(proto_target.angle(), other_proto_target.angle());

  auto other_proto_roi = bosdyn::api::Polygon();
  EXPECT_TRUE(other_proto_goal.roi().UnpackTo(&other_proto_roi));
  EXPECT_EQ(other_proto_roi.vertexes_size(), proto_roi.vertexes_size());
  for (int i = 0; i < proto_roi.vertexes_size(); ++i) {
    EXPECT_EQ(other_proto_roi.vertexes(i).x(), proto_roi.vertexes(i).x());
    EXPECT_EQ(other_proto_roi.vertexes(i).y(), proto_roi.vertexes(i).y());
  }
}
// NOLINTEND(readability-magic-numbers,readability-function-cognitive-complexity,cppcoreguidelines-pro-type-reinterpret-cast)
