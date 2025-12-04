import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_reproduce_supply():
    mod = load_module('reproduction', 'kernel/economic/reproduction.py')
    assert abs(mod.reproduce_supply(100.0, 0.01) - 101.0) < 1e-9