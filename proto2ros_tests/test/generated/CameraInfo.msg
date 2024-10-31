# Camera sensor information.

uint8 K_FIELD_SET=4
uint8 R_FIELD_SET=8
uint8 P_FIELD_SET=16
uint8 DISTORTION_MODEL_FIELD_SET=32

uint32 height
uint32 width
# Intrinsic matrix.
proto2ros_tests/Matrix k
# Rectification matrix.
proto2ros_tests/Matrix r
# Projection matrix.
proto2ros_tests/Matrix p
proto2ros_tests/CameraInfoDistortionModel distortion_model
uint8 has_field 255
