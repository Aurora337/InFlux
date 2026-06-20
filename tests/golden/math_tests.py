import os
import importlib.util

def load_module(module_name: str, rel_path: str):
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_fpe_and_dro_and_sgf():
    fpe = load_module('fpe', 'kernel/math/fpe.py')
    dro = load_module('dro', 'kernel/math/dro.py')
    sgf = load_module('sgf', 'kernel/math/sgf.py')

    assert fpe.emulated_add(1.0, 2.0) == 3.0
    assert fpe.emulated_mul(3.0, 2.0) == 6.0
    assert dro.clamp(5.0, 0.0, 4.0) == 4.0
    assert sgf.apply_sgf([1.0, 2.0, 3.0], kernel_size=3) == [1.5, 2.0, 2.5]