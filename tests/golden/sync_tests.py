import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_sync_components():
    gde = load_module('gde', 'kernel/sync/gde.py')
    ros = load_module('ros', 'kernel/sync/ros.py')
    shcm = load_module('shcm', 'kernel/sync/shcm.py')
    ainf = load_module('ainf', 'kernel/sync/ainf.py')

    state = {'x': 1}
    assert gde.gde_exchange(state) == state
    assert ros.ros_step(0) == 1
    assert shcm.verify_state_hash('a', 'a') is True
    assert ainf.ainf_anchor({'k': 'v'}) == {'k': 'v'}