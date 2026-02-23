import pytest
from sagelsp.plugins.cython_utils import *


def test_cython_definition():
    """Test cython_utils.py's definition locating function"""
    path = "/home/sean/miniforge3/envs/sage/lib/python3.11/site-packages/sage/rings/integer_ring.pyx"
    print(definition(path, "ZZ"))


if __name__ == "__main__":
    pytest.main([__file__])