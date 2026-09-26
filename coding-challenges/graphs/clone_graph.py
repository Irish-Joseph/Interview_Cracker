"""Challenge: Clone Graph | Pattern: graph traversal | Difficulty: Medium

Deep-copy a connected undirected graph. Return None for an empty graph.
Hint: map each original node to its clone before visiting neighbors.
Complexity: O(V+E) time and O(V) auxiliary space.
"""
from dataclasses import dataclass, field

@dataclass(eq=False)
class Node:
    value: int
    neighbors: list["Node"] = field(default_factory=list)

def clone_graph(node: Node | None) -> Node | None:
    if node is None: return None
    clones: dict[Node, Node] = {}
    def clone(current: Node) -> Node:
        if current in clones: return clones[current]
        copy = Node(current.value)
        clones[current] = copy
        copy.neighbors = [clone(neighbor) for neighbor in current.neighbors]
        return copy
    return clone(node)

def _signature(start: Node) -> dict[int, list[int]]:
    result, queue = {}, [start]
    while queue:
        node = queue.pop()
        if node.value in result: continue
        result[node.value] = sorted(n.value for n in node.neighbors)
        queue.extend(node.neighbors)
    return result

def _tests() -> None:
    assert clone_graph(None) is None
    single = Node(1); single_copy = clone_graph(single)
    assert single_copy is not single and single_copy.value == 1
    nodes = [Node(i) for i in range(1, 5)]
    nodes[0].neighbors = [nodes[1], nodes[3]]; nodes[1].neighbors = [nodes[0], nodes[2]]
    nodes[2].neighbors = [nodes[1], nodes[3]]; nodes[3].neighbors = [nodes[0], nodes[2]]
    copied = clone_graph(nodes[0])
    assert copied is not None and _signature(copied) == _signature(nodes[0])
    copied.value = 99; assert nodes[0].value == 1
    print("Clone Graph: all tests passed")

if __name__ == "__main__": _tests()
