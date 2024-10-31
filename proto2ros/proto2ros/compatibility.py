# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

# ruff: noqa
# fmt: off

# NOTE(mhidalgo): handle https://bugs.launchpad.net/ubuntu/+source/networkx/+bug/2002660
import numpy
numpy.int = numpy.int_

import networkx
