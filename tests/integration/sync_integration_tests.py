import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_hash_and_state_sync():
    hash_sync = load_module('hash_sync', 'kernel/ledger/hash_sync.py')
    shcm = load_module('shcm', 'kernel/sync/shcm.py')

    root = hash_sync.compute_root_hash([b'a', b'b'])
    assert shcm.verify_state_hash(root, root)