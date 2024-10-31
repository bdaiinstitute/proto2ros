# Copyright (c) 2023 Boston Dynamics AI Institute LLC. All rights reserved.

"""This module provides APIs to manipulate dependencies between Protobuf <-> ROS message equivalences."""

import collections
import itertools
import warnings
from typing import List

from rosidl_adapter.parser import MessageSpecification

from proto2ros.compatibility import networkx as nx
from proto2ros.utilities import to_ros_base_type


def message_dependency_graph(message_specs: List[MessageSpecification]) -> nx.DiGraph:
    """Returns the dependency graph for the given ROS message specifications.

    This dependency graph is a directed multi-graph where message types make up nodes
    and composition relationships (has-a) make up edges. Nodes are annotated with the
    corresponding message specification, while edges are annotated with the corresponding
    field specification.
    """
    dependency_graph = nx.MultiDiGraph()
    for message in message_specs:
        dependency_graph.add_node(str(message.base_type), message=message)
        for field in message.fields:
            if field.type.is_primitive_type():
                continue
            dependency_graph.add_edge(str(message.base_type), to_ros_base_type(field.type), field=field)
    return dependency_graph


def fix_dependency_cycles(message_specs: List[MessageSpecification], quiet: bool = True) -> None:
    """Fixes dependency cycles among ROS message specifications.

    ROS messages do not support recursive definitions, so this function works around this
    limitation by type erasing the least amount of offending fields.
    """
    dependency_graph = message_dependency_graph(message_specs)

    cycles = []
    for cycle in nx.simple_cycles(dependency_graph):
        if not quiet:
            message_types = [dependency_graph.nodes[node]["message"].base_type for node in cycle]
            dependency_cycle_depiction = " -> ".join(str(type_) for type_ in message_types)
            dependency_cycle_depiction += " -> " + str(message_types[0])  # close the loop
            warnings.warn("Dependency cycle found: " + dependency_cycle_depiction, stacklevel=1)
        cycles.append(cycle)

    counter = collections.Counter(
        sorted(
            sorted(itertools.chain(*cycles)),  # ensures an stable order (maintained by sorted)
            key=dependency_graph.in_degree,  # implicitly breaks ties by prioritizing the least common messages
        ),
    )
    while counter.total() > 0:
        for node, _ in counter.most_common():  # greedily break cycles
            message = dependency_graph.nodes[node]["message"]
            if message.annotations["proto-class"] != "message":
                continue
            break
        else:
            raise RuntimeError("no candidate for type erasure found")
        for cycle in list(cycles):
            if node not in cycle:
                continue
            parent = cycle[cycle.index(node) - 1]
            for data in dependency_graph[parent][node].values():
                field = data["field"]
                if not quiet:
                    message_type = dependency_graph.nodes[parent]["message"].base_type
                    warnings.warn(
                        f"Type erasing {field.type} {field.name} member in {message_type} to break recursion",
                        stacklevel=1,
                    )
                field.annotations["type-erased"] = True
            counter.subtract(cycle)
            cycles.remove(cycle)
