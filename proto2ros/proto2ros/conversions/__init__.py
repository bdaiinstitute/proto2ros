# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.
import multipledispatch

# Overloads entrypoint (via multiple dispatch)
convert = multipledispatch.Dispatcher("convert")
