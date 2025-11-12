# Protobuf / ROS 2 interoperability

![Python Support](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)
![ROS Support](https://img.shields.io/badge/ROS-humble%20%7C%20jazzy-blue)

## Overview

`proto2ros` helps maintain an interoperability layer between Protobuf dependent and ROS 2 aware code by generating equivalent ROS 2 message definitions given source Protobuf message definitions, as well bi-directional conversion APIs in relevant languages such as C++ and Python. To date, Protobuf syntax versions 2 and 3 are supported but only syntax version 3 has been extensively tested.

## Packages

This repository contains the following packages:

| Package                               | Description                                                                        |
|---------------------------------------| -----------------------------------------------------------------------------------|
| [`proto2ros`](proto2ros)              | Machinery for ROS 2 equivalent message generation and conversion code generation.  |
| [`proto2ros_tests`](proto2ros_tests)  | End-to-end tests for `proto2ros` generated messages and message conversion APIs.   |

## Next steps

See [contribution guidelines](CONTRIBUTING.md)!
