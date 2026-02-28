import timeit
from hermeneus.src.macros import load_standard_macros, get_all_macros, get_macro_registry, get_macro_expansion

def test_load_standard():
    load_standard_macros()

def test_get_all():
    get_all_macros()

if __name__ == "__main__":
    t_std = timeit.timeit("test_load_standard()", setup="from __main__ import test_load_standard", number=100)
    print(f"load_standard_macros (100 runs): {t_std:.4f} seconds")

    t_all = timeit.timeit("test_get_all()", setup="from __main__ import test_get_all", number=100)
    print(f"get_all_macros (100 runs): {t_all:.4f} seconds")
