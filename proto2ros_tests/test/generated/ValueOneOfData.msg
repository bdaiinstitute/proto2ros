
int8 DATA_NOT_SET=0
int8 DATA_NUMBER_SET=1
int8 DATA_TEXT_SET=2
int8 DATA_PAIR_SET=3
int8 DATA_LIST_SET=4
int8 DATA_DICT_SET=5

# Numeric value.
float32 number
# Text value.
string text
# Pair value.
proto2ros_tests/Pair pair
# List value.
proto2ros_tests/List list
# Dict value.
proto2ros_tests/Dict dict
int8 data_choice  # deprecated
int8 which
