# Copyright (c) 2023 Robotics and AI Institute LLC dba RAI Institute. All rights reserved.
import multipledispatch

# Overloads entrypoint (via multiple dispatch)
convert = multipledispatch.Dispatcher("convert")
