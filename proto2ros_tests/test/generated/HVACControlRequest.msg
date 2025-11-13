# A control request for an HVAC system.

uint8 TEMPERATURE_SETPOINT_FIELD_SET=2
uint8 HUMIDITY_SETPOINT_FIELD_SET=4

float64 air_flow_rate
sensor_msgs/Temperature temperature_setpoint
float64 humidity_setpoint
uint8 has_field 255
