"""
Zero-Copy Content-Addressed Array Store for Heavy 2D/3D Simulation Fields.
Stores large multi-dimensional arrays (voxel FEM displacements, CA grain maps, CFD velocity grids)
out-of-band on disk/shared memory, returning lightweight URIs for UADIB envelopes.
"""

from __future__ import annotations
import os
import hashlib
import tempfile
from typing import Dict, Optional, Tuple, Any, Union
import numpy as np


class ArrayStore:
    """
    Manages persistence and memory-mapped retrieval of high-density numerical tensors.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = os.path.abspath(storage_dir)
        else:
            self.storage_dir = os.path.join(tempfile.gettempdir(), "alloy_array_store")
        os.makedirs(self.storage_dir, exist_ok=True)

    def put_array(
        self,
        array: np.ndarray,
        tag: str = "tensor",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Saves a NumPy array to disk using its SHA-256 content hash.
        Returns (uri, content_hash).
        """
        raw_bytes = array.tobytes()
        content_hash = hashlib.sha256(raw_bytes).hexdigest()
        filename = f"{tag}_{content_hash[:16]}.npz"
        file_path = os.path.join(self.storage_dir, filename)

        if not os.path.exists(file_path):
            meta_dict = metadata or {}
            np.savez_compressed(file_path, data=array, metadata=np.array([str(meta_dict)]))

        uri = f"file://{file_path}"
        return uri, content_hash

    def get_array(self, uri_or_path: str, mmap_mode: Optional[str] = "r") -> np.ndarray:
        """
        Loads array by URI or file path using memory mapping for zero-copy efficiency.
        """
        path = uri_or_path.replace("file://", "")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Array store file not found: {path}")

        loaded = np.load(path, mmap_mode=mmap_mode)
        if isinstance(loaded, np.lib.npyio.NpzFile):
            return loaded["data"]
        return loaded

    def exists(self, content_hash_or_filename: str) -> bool:
        """Check if an array already exists in the store."""
        for f in os.listdir(self.storage_dir):
            if content_hash_or_filename in f:
                return True
        return False
