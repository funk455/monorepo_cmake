#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path


def prompt(text, default=None, required=False):
    suffix = f" [默认: {default}]" if default is not None else ""
    while True:
        value = input(f"{text}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        if not required:
            return ""
        print("该项必填，请输入有效值。")


def prompt_yes_no(text, default=True):
    default_str = "Y/n" if default else "y/N"
    while True:
        value = input(f"{text} [{default_str}]: ").strip().lower()
        if not value:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("请输入 y 或 n。")


def prompt_target_type(text, default):
    while True:
        value = prompt(text, default=default).upper()
        if value in ("EXECUTABLE", "LIBRARY"):
            return value
        print("请输入 EXECUTABLE 或 LIBRARY。")


def parse_list(value):
    if not value:
        return []
    parts = []
    for chunk in value.replace(";", ",").split(","):
        item = chunk.strip()
        if item:
            parts.append(item)
    return parts


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def write_text(path, content):
    path.write_text(content, encoding="utf-8")


def gen_library_files(lib_dir, target_name, sources, headers):
    if headers:
        header_name = headers[0]
    else:
        header_name = f"{target_name}.h"
        headers = [header_name]
    if sources:
        source_name = sources[0]
    else:
        source_name = f"{target_name}.cpp"
        sources = [source_name]

    header_path = lib_dir / header_name
    source_path = lib_dir / source_name

    if not header_path.exists():
        write_text(
            header_path,
            f"#pragma once\n\nint {target_name}_add(int a, int b);\n",
        )
    if not source_path.exists():
        write_text(
            source_path,
            f'#include "{header_name}"\n\nint {target_name}_add(int a, int b) {{\n  return a + b;\n}}\n',
        )
    return sources, headers


def gen_exe_files(dir_path, sources, use_lib, lib_target, lib_header):
    source_name = sources[0] if sources else "main.cpp"
    source_path = dir_path / source_name
    if source_path.exists():
        return sources or [source_name]

    if use_lib:
        content = (
            f'#include "{lib_header}"\n\n'
            "int main() {\n"
            f"  return {lib_target}_add(1, 2) == 3 ? 0 : 1;\n"
            "}\n"
        )
    else:
        content = "int main() {\n  return 0;\n}\n"

    write_text(source_path, content)
    return sources or [source_name]


def gen_test_files(dir_path, sources, lib_target, lib_header, use_lib=True):
    source_name = sources[0] if sources else "smoke.cpp"
    source_path = dir_path / source_name
    if source_path.exists():
        return sources or [source_name]

    if use_lib:
        content = (
            f'#include "{lib_header}"\n'
            "#include <cassert>\n\n"
            "int main() {\n"
            f"  assert({lib_target}_add(2, 2) == 4);\n"
            "  return 0;\n"
            "}\n"
        )
    else:
        content = "#include <cassert>\n\nint main() {\n  assert(2 + 2 == 4);\n  return 0;\n}\n"
    write_text(source_path, content)
    return sources or [source_name]


def write_project_cmakelists(path, project_name, version, namespace, modules, include_tests):
    lines = [
        f"project({project_name} VERSION {version} LANGUAGES CXX)",
        'list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")',
        "include(AddModules)",
        f'set(PROJECT_NAMESPACE "{namespace}")',
        "",
        f"add_modules({' '.join(modules)})",
        "",
    ]
    if include_tests:
        lines += [
            "include(CTest)",
            "if(BUILD_TESTING)",
            "  enable_testing()",
            "  add_modules(tests)",
            "endif()",
            "",
        ]
    write_text(path, "\n".join(lines) + "\n")


def write_target_cmakelists(path, target):
    lines = [
        f'set(PKG_TARGET_NAME "{target["name"]}")',
        "set(DIR_TARGET_NAME ${PKG_TARGET_NAME})",
        f'set(DIR_TARGET_TYPE {target["type"]})',
    ]
    if target.get("alias_prefix"):
        lines.append(f'set(DIR_ALIAS_PREFIX {target["alias_prefix"]})')
    if target.get("public_deps"):
        lines.append(f'set(DIR_PUBLIC_DEPS {";".join(target["public_deps"])})')
    if target.get("private_deps"):
        lines.append(f'set(DIR_PRIVATE_DEPS {";".join(target["private_deps"])})')
    if target.get("enable_install"):
        lines.append("set(DIR_ENABLE_INSTALL ON)")
    if target["type"] == "LIBRARY":
        lines.append('set(PROJECT_EXPORT_NAME "${PKG_TARGET_NAME}Targets")')
    if target.get("sources"):
        lines.append(f'set(DIR_SOURCES {";".join(target["sources"])})')
    if target.get("headers"):
        lines.append(f'set(DIR_HEADERS {";".join(target["headers"])})')
    lines.append("include(${CMAKE_SOURCE_DIR}/cmake/AddTarget.cmake)")
    if target["type"] == "LIBRARY":
        lines += [
            "include(${CMAKE_SOURCE_DIR}/cmake/SetupPackage.cmake)",
            "setup_package(",
            '  PACKAGE_NAME      "${PKG_TARGET_NAME}"',
            '  PACKAGE_NAMESPACE "${PROJECT_NAMESPACE}"',
            '  EXPORT_NAME       "${PROJECT_EXPORT_NAME}"',
            "  APPEND_GIT_HASH   ON",
            ")",
        ]
    lines.append("")
    write_text(path, "\n".join(lines))


def ensure_root_cmakelists(root, workspace_dir):
    root_cmakelists = root / "CMakeLists.txt"
    if root_cmakelists.exists():
        return

    # 根目录缺失时生成一个最小可用的 CMakeLists.txt
    content = [
        "cmake_minimum_required(VERSION 3.20)",
        "project(Workspace LANGUAGES CXX)",
        "",
        'list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")',
        "include(UnifiedOutputDirs)",
        "include(AddUninstall)",
        "include(BuildType)",
        "add_uninstall_target()",
        "# Enable tests at the root so CTest can discover tests in subprojects",
        "include(CTest)",
        "enable_testing()",
        "",
        "include(AddWorkspaces)",
        "add_workspace_projects(",
        '  ROOT "${CMAKE_SOURCE_DIR}/projects"',
        "  DIRS",
        f'    "{workspace_dir}"',
        ")",
        "",
    ]
    write_text(root_cmakelists, "\n".join(content))


def update_root_workspace_list(root_cmakelists, workspace_dir):
    content = root_cmakelists.read_text(encoding="utf-8").splitlines()
    new_entry = f'    "{workspace_dir}"'
    if any(line.strip() == f'"{workspace_dir}"' for line in content):
        return

    start_idx = None
    for i, line in enumerate(content):
        if "add_workspace_projects" in line:
            start_idx = i
            break
    if start_idx is None:
        raise RuntimeError("无法在根 CMakeLists.txt 中找到 add_workspace_projects 调用。")

    dirs_idx = None
    for i in range(start_idx, len(content)):
        if content[i].strip().startswith("DIRS"):
            dirs_idx = i
            break
    if dirs_idx is None:
        raise RuntimeError("无法在根 CMakeLists.txt 中找到 DIRS 块，请手动添加工作区目录。")

    for i in range(dirs_idx + 1, len(content)):
        if content[i].strip().startswith(")"):
            content.insert(i, new_entry)
            root_cmakelists.write_text("\n".join(content) + "\n", encoding="utf-8")
            return

    raise RuntimeError("DIRS 块未正确闭合，请检查根 CMakeLists.txt。")


def interactive_config(root):
    project_name = prompt("项目名", required=True)
    version = prompt("项目版本", default="0.1.0")
    namespace = prompt("命名空间", default=project_name)

    include_lib = prompt_yes_no("是否生成库目标", default=True)
    include_app = prompt_yes_no("是否生成应用程序目标", default=True)
    include_tests = prompt_yes_no("是否生成测试目标", default=True)

    targets = []
    modules = []

    lib_target = None
    lib_dir = None

    if include_lib:
        lib_dir = prompt("库目录名", default=project_name)
        lib_target = prompt("库目标名", default=project_name)
        lib_type = prompt_target_type("库目标类型", default="LIBRARY")
        lib_sources = parse_list(prompt("库源码列表(逗号分隔)", default=f"{lib_target}.cpp"))
        lib_headers = parse_list(prompt("库头文件列表(逗号分隔)", default=f"{lib_target}.h"))
        targets.append(
            {
                "dir": lib_dir,
                "name": lib_target,
                "type": lib_type,
                "kind": "lib",
                "alias_prefix": namespace,
                "enable_install": True,
                "sources": lib_sources,
                "headers": lib_headers,
            }
        )
        modules.append(lib_dir)

    if include_app:
        app_dir = prompt("应用目录名", default="app")
        app_target = prompt("应用目标名", default=f"{project_name}_app")
        app_type = prompt_target_type("应用目标类型", default="EXECUTABLE")
        app_sources = parse_list(prompt("应用源码列表(逗号分隔)", default="main.cpp"))
        app_deps = [f"{namespace}::{lib_target}"] if lib_target else []
        targets.append(
            {
                "dir": app_dir,
                "name": app_target,
                "type": app_type,
                "kind": "app",
                "private_deps": app_deps,
                "enable_install": True,
                "sources": app_sources,
            }
        )
        modules.append(app_dir)

    if include_tests:
        test_dir = prompt("测试目录名", default="tests/smoke")
        test_target = prompt("测试目标名", default=f"{project_name}_smoke")
        test_type = prompt_target_type("测试目标类型", default="EXECUTABLE")
        test_sources = parse_list(prompt("测试源码列表(逗号分隔)", default="smoke.cpp"))
        test_deps = [f"{namespace}::{lib_target}"] if lib_target else []
        targets.append(
            {
                "dir": test_dir,
                "name": test_target,
                "type": test_type,
                "kind": "test",
                "private_deps": test_deps,
                "sources": test_sources,
            }
        )

    return {
        "project_name": project_name,
        "project_version": version,
        "project_namespace": namespace,
        "workspace_dir": f"projects/{project_name}",
        "modules": modules,
        "include_tests": include_tests,
        "targets": targets,
    }


def generate_from_config(root, cfg, force=False):
    workspace_dir = root / cfg["workspace_dir"]
    if workspace_dir.exists() and not force:
        raise RuntimeError(f"目录已存在: {workspace_dir}")

    # 确保根目录的 CMakeLists.txt 存在。
    ensure_root_cmakelists(root, cfg["workspace_dir"])

    ensure_dir(workspace_dir)

    # 写入项目根 CMakeLists.txt
    write_project_cmakelists(
        workspace_dir / "CMakeLists.txt",
        cfg["project_name"],
        cfg["project_version"],
        cfg["project_namespace"],
        cfg["modules"],
        cfg["include_tests"],
    )

    # 生成子模块与目标
    lib_targets = [t for t in cfg["targets"] if t["type"] == "LIBRARY"]
    lib_target_name = lib_targets[0]["name"] if lib_targets else "lib"
    lib_header_name = None
    if lib_targets:
        headers = lib_targets[0].get("headers") or []
        lib_header_name = headers[0] if headers else f"{lib_target_name}.h"

    for target in cfg["targets"]:
        target_dir = workspace_dir / target["dir"]
        ensure_dir(target_dir)

        if "kind" not in target:
            target["kind"] = "lib" if target["type"] == "LIBRARY" else "app"

        if target["type"] == "LIBRARY":
            sources, headers = gen_library_files(
                target_dir,
                target["name"],
                target.get("sources", []),
                target.get("headers", []),
            )
            target["sources"] = sources
            target["headers"] = headers
        elif target.get("kind") == "test":
            sources = gen_test_files(
                target_dir,
                target.get("sources", []),
                lib_target_name,
                lib_header_name or f"{lib_target_name}.h",
                use_lib=len(lib_targets) > 0,
            )
            target["sources"] = sources
        else:
            sources = gen_exe_files(
                target_dir,
                target.get("sources", []),
                len(lib_targets) > 0,
                lib_target_name,
                lib_header_name or f"{lib_target_name}.h",
            )
            target["sources"] = sources

        write_target_cmakelists(target_dir / "CMakeLists.txt", target)

    # 更新根目录的工作区列表
    update_root_workspace_list(root / "CMakeLists.txt", cfg["workspace_dir"])


def main():
    parser = argparse.ArgumentParser(description="CMake 项目引导式模板生成器")
    parser.add_argument("--preset", help="使用预设文件直接生成项目")
    parser.add_argument("--save-preset", action="store_true", help="保存为 preset.json")
    parser.add_argument("--force", action="store_true", help="目标目录已存在时强制生成")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    preset_path = Path(args.preset) if args.preset else root / "preset.json"

    if args.preset:
        cfg = json.loads(preset_path.read_text(encoding="utf-8"))
        generate_from_config(root, cfg, force=args.force)
        return

    cfg = interactive_config(root)

    # 先保存预设，确保首次引导后一定有 preset.json 可复用。
    if args.save_preset or not preset_path.exists():
        preset_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    generate_from_config(root, cfg, force=args.force)


if __name__ == "__main__":
    main()
