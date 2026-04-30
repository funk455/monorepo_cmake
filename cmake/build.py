#!/usr/bin/env python3
import argparse
import platform
import subprocess
from pathlib import Path


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


MULTI_CONFIG_GENERATORS = {
    "ninja multi-config",
    "visual studio 17 2022",
    "visual studio 16 2019",
    "visual studio 15 2017",
    "xcode",
}


def is_multi_config(generator: str) -> bool:
    return generator.lower() in MULTI_CONFIG_GENERATORS if generator else False


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
    parser.add_argument("--build-type", default="Release", help="单配置生成器的构建类型")
    parser.add_argument("--config", help="多配置生成器的配置名（如 Debug/Release）")
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

    multi = is_multi_config(args.generator)

    cmake_cmd = ["cmake", "-S", str(root), "-B", str(build_dir)]
    if args.generator:
        cmake_cmd += ["-G", args.generator]
    if not multi and args.build_type:
        cmake_cmd += [f"-DCMAKE_BUILD_TYPE={args.build_type}"]

    run(cmake_cmd)

    if args.build:
        build_cmd = ["cmake", "--build", str(build_dir)]
        cfg = args.config if multi else None
        if cfg:
            build_cmd += ["--config", cfg]
        run(build_cmd)

    print(f"Build directory: {build_dir}")


if __name__ == "__main__":
    main()
