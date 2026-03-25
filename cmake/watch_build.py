#!/usr/bin/env python3
import argparse
import os
import subprocess
import time
import sys
from pathlib import Path
from shutil import which


def run(cmd, cwd=None):
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def resolve_cmake(value):
    # 如果用户提供的是完整路径，直接使用。
    if os.path.basename(value) != value:
        return value

    # 先尝试在 PATH 中查找。
    found = which(value)
    if found:
        return found

    # Windows 常见安装路径探测。
    if os.name == "nt":
        candidates = [
            r"C:\Program Files\CMake\bin\cmake.exe",
            r"C:\Program Files (x86)\CMake\bin\cmake.exe",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path

    # macOS 常见安装路径探测。
    if sys.platform == "darwin":
        candidates = [
            "/Applications/CMake.app/Contents/bin/cmake",
            "/usr/local/bin/cmake",
            "/opt/homebrew/bin/cmake",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path

    # Linux 常见路径探测（仅在 PATH 未命中时兜底）。
    candidates = ["/usr/bin/cmake", "/usr/local/bin/cmake", "/snap/bin/cmake"]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def should_skip_dir(path, build_dir):
    if path == build_dir or path.startswith(str(build_dir) + os.sep):
        return True
    name = os.path.basename(path)
    return name in {".git", ".cache", "__pycache__", "build", "dist", "out"}


def snapshot_files(root, build_dir, exts):
    result = {}
    for dirpath, dirnames, filenames in os.walk(root):
        if should_skip_dir(dirpath, build_dir):
            dirnames[:] = []
            continue
        # prune child dirs
        dirnames[:] = [d for d in dirnames if not should_skip_dir(os.path.join(dirpath, d), build_dir)]

        for name in filenames:
            if name == "CMakeLists.txt" or name.endswith(".cmake") or name.endswith(".cmake.in"):
                path = os.path.join(dirpath, name)
            else:
                if not any(name.endswith(ext) for ext in exts):
                    continue
                path = os.path.join(dirpath, name)
            try:
                result[path] = os.path.getmtime(path)
            except OSError:
                continue
    return result


def detect_changes(prev, curr):
    changed = []
    prev_keys = set(prev.keys())
    curr_keys = set(curr.keys())

    for path in curr_keys - prev_keys:
        changed.append(("added", path))
    for path in prev_keys - curr_keys:
        changed.append(("removed", path))
    for path in prev_keys & curr_keys:
        if prev[path] != curr[path]:
            changed.append(("modified", path))
    return changed


def any_config_change(changes):
    for kind, path in changes:
        base = os.path.basename(path)
        if base == "CMakeLists.txt" or path.endswith(".cmake") or path.endswith(".cmake.in"):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="文件变更自动构建（监视模式）")
    parser.add_argument("--cmake", default="cmake", help="CMake 可执行文件路径或名称")
    parser.add_argument("--source", default=".", help="源码目录")
    parser.add_argument("--build", default="build", help="构建目录")
    parser.add_argument("--generator", help="CMake 生成器")
    parser.add_argument("--build-type", default="Release", help="单配置生成器构建类型")
    parser.add_argument("--config", help="多配置生成器配置名（Debug/Release）")
    parser.add_argument("--interval", type=float, default=1.0, help="扫描间隔（秒）")
    parser.add_argument(
        "--exts",
        default=".c,.cc,.cpp,.cxx,.h,.hpp",
        help="监听的源码/头文件后缀（逗号分隔）",
    )
    args = parser.parse_args()

    root = Path(args.source).resolve()
    build_dir = (root / args.build).resolve()
    exts = [e.strip() for e in args.exts.split(",") if e.strip()]

    cmake_exe = resolve_cmake(args.cmake)
    if not cmake_exe:
        raise SystemExit("未找到 cmake，可用 --cmake 指定完整路径，或将 cmake 加入 PATH。")

    build_dir.mkdir(parents=True, exist_ok=True)

    # 初次配置
    config_cmd = [cmake_exe, "-S", str(root), "-B", str(build_dir)]
    if args.generator:
        config_cmd += ["-G", args.generator]
    if args.build_type:
        config_cmd += [f"-DCMAKE_BUILD_TYPE={args.build_type}"]
    run(config_cmd)

    # 初次构建
    build_cmd = [cmake_exe, "--build", str(build_dir)]
    if args.config:
        build_cmd += ["--config", args.config]
    run(build_cmd)

    prev = snapshot_files(str(root), str(build_dir), exts)
    print("Watching for changes... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(args.interval)
            curr = snapshot_files(str(root), str(build_dir), exts)
            changes = detect_changes(prev, curr)
            if not changes:
                continue

            print("Detected changes:")
            for kind, path in changes[:10]:
                print(f"  {kind}: {path}")
            if len(changes) > 10:
                print(f"  ... and {len(changes) - 10} more")

            if any_config_change(changes):
                run(config_cmd)
                run(build_cmd)

            run(build_cmd)

            prev = curr
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
