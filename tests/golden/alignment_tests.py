import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_alignment_components():
    router = load_module('router', 'kernel/alignment/router.py')
    classifier = load_module('classifier', 'kernel/alignment/classifier.py')
    tags = load_module('tags', 'kernel/alignment/tags.py')

    assert router.route_path('a', 'b') == ['a', 'b']
    assert classifier.classify({'type': 'tx'}) == 'tx'
    assert tags.normalize_tag('  Foo ') == 'foo'