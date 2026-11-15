"""Paths — framework directory vs. workspace directory.

FRAMEWORK_DIR is this repository (cmake/ modules, cli.py, toolchains shipped with the framework).
The workspace is the repository being managed: its projects/, build dirs, preset.json and
working directory for jobs. By default they are the same; `python ui.py --root <dir>` points the
workspace at another repository that references the framework (e.g. as a git submodule).
"""

import os
from pathlib import Path

FRAMEWORK_DIR = Path(__file__).resolve().parent.parent
FRAMEWORK_TOOLCHAINS_DIR = FRAMEWORK_DIR / "cmake" / "toolchains"

_workspace = FRAMEWORK_DIR


def set_workspace(path) -> Path:
    global _workspace
    p = Path(path).resolve()
    if not p.is_dir():
        raise ValueError(f"workspace root is not a directory: {p}")
    _workspace = p
    return _workspace


def workspace() -> Path:
    return _workspace


def is_external_workspace() -> bool:
    return _workspace != FRAMEWORK_DIR


def workspace_toolchains_dir() -> Path:
    """Where toolchains are saved: the framework's own dir, or <workspace>/toolchains when external."""
    return _workspace / "toolchains" if is_external_workspace() else FRAMEWORK_TOOLCHAINS_DIR


def toolchain_dirs() -> list:
    """Toolchain search order: the workspace's own first, then the framework's."""
    dirs = [workspace_toolchains_dir()]
    if FRAMEWORK_TOOLCHAINS_DIR not in dirs:
        dirs.append(FRAMEWORK_TOOLCHAINS_DIR)
    return dirs


def rel_to_workspace(p: Path) -> str:
    """Path as used in commands run from the workspace (relative when possible)."""
    try:
        return os.path.relpath(Path(p).resolve(), _workspace).replace("\\", "/")
    except ValueError:  # different drive on Windows
        return str(Path(p).resolve()).replace("\\", "/")


def inside_workspace(p: Path) -> bool:
    root = _workspace.resolve()
    rp = Path(p).resolve()
    return rp == root or root in rp.parents
