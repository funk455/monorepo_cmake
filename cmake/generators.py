"""Helpers shared by build.py and watch_build.py for CMake generator handling."""
import re
from pathlib import Path

# Every Visual Studio version, Xcode and Ninja Multi-Config are multi-config generators.
# Matching by prefix means new Visual Studio releases need no code change.
_MULTI_CONFIG_RE = re.compile(r"^(Visual Studio|Xcode|Ninja Multi-Config)", re.IGNORECASE)


def is_multi_config(generator=None, build_dir=None):
    """Return True if the build uses a multi-config generator.

    A configured build dir is authoritative: CMake only caches
    CMAKE_CONFIGURATION_TYPES for multi-config generators. This also covers
    the case where no generator was passed and CMake picked its platform
    default (Visual Studio on Windows). Otherwise fall back to the name.
    """
    if build_dir is not None:
        cache = Path(build_dir) / "CMakeCache.txt"
        if cache.is_file():
            text = cache.read_text(encoding="utf-8", errors="replace")
            return any(line.startswith("CMAKE_CONFIGURATION_TYPES:")
                       for line in text.splitlines())
    return bool(generator) and _MULTI_CONFIG_RE.match(generator) is not None
