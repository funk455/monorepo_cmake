#!/usr/bin/env python3
import argparse
import platform
import subprocess
from pathlib import Path

from generators import is_multi_config


def run(cmd):
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def detect_platform():
    name = platform.system().lower()
    if "windows" in name:
        return "windows"
    if "darwin" in name or "mac" in name:
        return "macos"
    return "linux"


def make_build_dir(root, build_root, plat, generator, build_type, config):
    parts = [plat]
    if generator:
        parts.append(generator.replace(" ", "_"))
    # Multi-config generators: config distinguishes builds, not build_type
    if is_multi_config(generator):
        if config:
            parts.append(config)
    else:
        if build_type:
            parts.append(build_type)
    suffix = "-".join(parts)
    return root / build_root / suffix


def main():
    parser = argparse.ArgumentParser(description="多平台构建目录助手")
    parser.add_argument("--platform", help="平台（windows|linux|macos），默认自动识别")
    parser.add_argument("--generator", help="CMake 生成器，如 Ninja、Unix Makefiles、Visual Studio 17 2022")
    parser.add_argument("--build-type", default="Release", help="构建类型；多配置生成器未给 --config 时也用它")
    parser.add_argument("--config", help="多配置生成器的配置名（如 Debug/Release），默认同 --build-type")
    parser.add_argument("--build", action="store_true", help="配置完成后直接构建")
    parser.add_argument("--source", default=".", help="源码目录")
    parser.add_argument("--build-root", default="build", help="构建根目录")
    args = parser.parse_args()

    root = Path(args.source).resolve()
    plat = args.platform or detect_platform()

    build_dir = make_build_dir(
        root, args.build_root, plat, args.generator, args.build_type, args.config
    )
    build_dir.mkdir(parents=True, exist_ok=True)

    cmake_cmd = ["cmake", "-S", str(root), "-B", str(build_dir)]
    if args.generator:
        cmake_cmd += ["-G", args.generator]
    if not is_multi_config(args.generator) and args.build_type:
        cmake_cmd += [f"-DCMAKE_BUILD_TYPE={args.build_type}"]

    run(cmake_cmd)

    if args.build:
        build_cmd = ["cmake", "--build", str(build_dir)]
        # 以配置后的 CMakeCache 为准：未指定 --generator 时 Windows 默认是 Visual Studio，
        # 不传 --config 会编译 Debug，与 --build-type 不符。
        if is_multi_config(args.generator, build_dir):
            build_cmd += ["--config", args.config or args.build_type]
        run(build_cmd)

    print(f"Build directory: {build_dir}")


if __name__ == "__main__":
    main()
