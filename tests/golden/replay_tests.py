import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_replay_engine():
    replay = load_module('replay', 'harness/replay_engine.py')
    engine = replay.ReplayEngine(events=[1,2,3])
    assert engine.replay() == [1,2,3]