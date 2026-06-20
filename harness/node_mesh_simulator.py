"""node_mesh_simulator.py

Simple node mesh simulator placeholder for emulating networked nodes and message passing.
"""

from typing import Dict, List, Callable

class Node:
    def __init__(self, id: str, handler: Callable[[dict], None] = None):
        self.id = id
        self.handler = handler

class NodeMeshSimulator:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.messages: List[dict] = []

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def send(self, src: str, dst: str, payload: dict) -> None:
        self.messages.append({"src": src, "dst": dst, "payload": payload})
        dst_node = self.nodes.get(dst)
        if dst_node and dst_node.handler:
            dst_node.handler(payload)

__all__ = ["Node", "NodeMeshSimulator"]