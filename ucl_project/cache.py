"""Simple file-based cache for API responses"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DURATION_HOURS = 1  # Cache for 1 hour


def _ensure_cache_dir() -> None:
    """Ensure cache directory exists"""
    CACHE_DIR.mkdir(exist_ok=True)


def _get_cache_path(key: str) -> Path:
    """Get cache file path for a key"""
    return CACHE_DIR / f"{key}.json"


def get_cached(key: str) -> dict[str, Any] | None:
    """
    Get cached data if exists and not expired.

    Args:
        key: Cache key (e.g., 'standings_61644')

    Returns:
        Cached data or None if expired/missing
    """
    try:
        _ensure_cache_dir()
        cache_path = _get_cache_path(key)

        if not cache_path.exists():
            return None

        # Check if cache is expired
        modified_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - modified_time > timedelta(hours=CACHE_DURATION_HOURS):
            logger.info(f"Cache expired for {key}")
            cache_path.unlink()  # Delete expired cache
            return None

        # Load cached data
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Cache hit for {key} (age: {datetime.now() - modified_time})")
        return data

    except Exception as e:
        logger.warning(f"Failed to read cache for {key}: {e}")
        return None


def set_cached(key: str, data: dict[str, Any]) -> None:
    """
    Save data to cache.

    Args:
        key: Cache key
        data: Data to cache
    """
    try:
        _ensure_cache_dir()
        cache_path = _get_cache_path(key)

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Cached data for {key}")

    except Exception as e:
        logger.warning(f"Failed to write cache for {key}: {e}")


def clear_cache() -> None:
    """Clear all cached data"""
    try:
        _ensure_cache_dir()
        for cache_file in CACHE_DIR.glob("*.json"):
            cache_file.unlink()
        logger.info("Cache cleared")
    except Exception as e:
        logger.warning(f"Failed to clear cache: {e}")
