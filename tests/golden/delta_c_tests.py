import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_compute_delta():
    mod = load_module('delta_c', 'kernel/economic/delta_c.py')
    assert mod.compute_delta(10.0, 12.5) == 2.5