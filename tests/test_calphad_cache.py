import pytest
import tempfile
import os
from alloy_core.cache.calphad_cache import CalphadContentCache


def test_calphad_cache_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "calphad_test.db")
        cache = CalphadContentCache(db_path=db_path)

        comp = {"Ti": 0.90, "Al": 0.06, "V": 0.04}
        key = cache.generate_cache_key(
            tdb_id_or_hash="TDB-COST507",
            composition_fractions=comp,
            temperature_k=1273.15
        )

        assert cache.get(key) is None
        assert cache.stats.misses == 1

        payload = {
            "phases": {"BCC_A2": 0.85, "HCP_A3": 0.15},
            "driving_force_j_mol": 1250.0
        }
        cache.put(key, payload)

        # Retrieve from in-memory cache
        retrieved = cache.get(key)
        assert retrieved is not None
        assert retrieved["phases"]["BCC_A2"] == 0.85
        assert cache.stats.hits == 1

        # Test persistence: new cache instance on same SQLite file
        cache2 = CalphadContentCache(db_path=db_path)
        retrieved2 = cache2.get(key)
        assert retrieved2 is not None
        assert retrieved2["phases"]["HCP_A3"] == 0.15
        assert cache2.stats.hits == 1
