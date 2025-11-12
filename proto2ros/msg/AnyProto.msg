# Copyright (c) 2023 Robotics and AI Institute LLC dba RAI Institute. All rights reserved.

# A dynamically typed Protobuf message. Equivalent to the google.protobuf.Any message.
# See https://protobuf.dev/reference/protobuf/google.protobuf/#any for further reference.

string  type_url    # Protobuf message type URL.
uint8[] value       # Packed Protobuf message instance.
