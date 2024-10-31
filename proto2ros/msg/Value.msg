# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

# A dynamically typed (scalar or composite) value. Equivalent to the google.protobuf.Value message.
# See https://protobuf.dev/reference/protobuf/google.protobuf/#value for further reference.

int8 NO_VALUE_SET=0
int8 NULL_VALUE_SET=1
int8 NUMBER_VALUE_SET=2
int8 STRING_VALUE_SET=3
int8 BOOL_VALUE_SET=4
int8 STRUCT_VALUE_SET=5
int8 LIST_VALUE_SET=6

int8 kind 0

float64 number_value
string string_value
bool bool_value
proto2ros/Any struct_value  # is proto2ros/Struct
proto2ros/Any list_value  # is proto2ros/List
