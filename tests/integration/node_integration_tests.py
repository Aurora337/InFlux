import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_node_mesh_simulation():
    mesh = load_module('mesh', 'harness/node_mesh_simulator.py')
    Node = mesh.Node
    NodeMeshSimulator = mesh.NodeMeshSimulator

    received = {}

    def handler(payload):
        received['p'] = payload

    n1 = Node('n1')
    n2 = Node('n2', handler=handler)
    sim = NodeMeshSimulator()
    sim.add_node(n1)
    sim.add_node(n2)
    sim.send('n1', 'n2', {'hello': 'world'})
    assert received.get('p') == {'hello': 'world'}