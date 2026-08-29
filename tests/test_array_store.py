"""
Unit tests for Zero-Copy ArrayStore.
Verifies out-of-band NumPy compression, SHA-256 hashing, and memory-mapped retrieval.
"""

import os
import shutil
import tempfile
import numpy as np
import pytest
from alloy_core.cache.array_store import ArrayStore


@pytest.fixture
def temp_store():
    d = tempfile.mkdtemp()
    store = ArrayStore(storage_dir=d)
    yield store
    shutil.rmtree(d, ignore_errors=True)


def test_array_store_put_and_get(temp_store):
    # 3D FEM grid test tensor (100 x 100 x 50)
    tensor = np.random.randn(50, 50, 20).astype(np.float32)
    uri, h = temp_store.put_array(tensor, tag="voxel_stress")
    
    assert uri.startswith("file://")
    assert len(h) == 64
    assert temp_store.exists(h[:16])

    # Zero-copy memory mapped load
    loaded = temp_store.get_array(uri, mmap_mode="r")
    assert loaded.shape == (50, 50, 20)
    assert np.allclose(loaded, tensor)


def test_array_store_deduplication(temp_store):
    tensor = np.ones((20, 20), dtype=np.float64)
    uri1, h1 = temp_store.put_array(tensor, tag="ca_grains")
    uri2, h2 = temp_store.put_array(tensor, tag="ca_grains")

    assert uri1 == uri2
    assert h1 == h2
