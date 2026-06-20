import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_ledger_pipeline_and_serialization_and_sort_and_hash():
    pipeline = load_module('pipeline', 'kernel/ledger/pipeline.py')
    serial = load_module('serialization', 'kernel/ledger/serialization.py')
    sorter = load_module('ctor_sort', 'kernel/ledger/ctor_sort.py')
    hash_sync = load_module('hash_sync', 'kernel/ledger/hash_sync.py')

    events = [{'a': 1}, {'b': 2}]
    processed = pipeline.process_pipeline(events)
    assert processed == events

    s = serial.serialize_event({'x': 1})
    assert isinstance(s, str)
    assert serial.deserialize_event(s)['x'] == 1

    sorted_events = sorter.ctor_sort(['b', 'a'])
    assert sorted_events == ['a', 'b']

    root = hash_sync.compute_root_hash([b'a', b'b'])
    assert isinstance(root, str) and len(root) == 64