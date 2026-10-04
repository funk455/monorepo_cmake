#!/usr/bin/env python3
"""Generate a large monorepo structure for performance testing.

Usage:
    python scripts/gen_large_repo.py --projects 50 --modules-per-project 3
    python scripts/gen_large_repo.py --projects 100 --modules-per-project 5 --dep-density 0.15
    python scripts/gen_large_repo.py --clean   # remove all generated projects

Generated projects are named perf_p001..perf_pNNN, each containing
modules named mod_a, mod_b, etc. Dependencies form a realistic DAG:
modules only depend on modules from lower-numbered projects (no cycles).
"""

import argparse
import random
import shutil
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "projects"
PREFIX = "perf_p"


def clean():
    removed = 0
    for d in sorted(PROJECTS_DIR.iterdir()):
        if d.is_dir() and d.name.startswith(PREFIX):
            shutil.rmtree(d)
            removed += 1
    print(f"Removed {removed} generated projects.")


def gen_header(target_name: str, deps: list[tuple[str, str, str]]) -> str:
    pub_deps = [(ns, name) for ns, name, kind in deps if kind == "PUBLIC"]
    includes = ""
    calls = ""
    for _, dep_name in pub_deps:
        includes += f'#include "{dep_name}.h"\n'
        calls += f"    (void){dep_name}_value();\n"
    return textwrap.dedent(f"""\
        #pragma once
        #include <string>
        {includes}
        inline int {target_name}_value() {{
        {calls}    return 42;
        }}

        std::string {target_name}_info();
    """)


def gen_source(target_name: str, deps: list[tuple[str, str, str]]) -> str:
    priv_includes = ""
    priv_calls = ""
    for _, dep_name, kind in deps:
        if kind == "PRIVATE":
            priv_includes += f'#include "{dep_name}.h"\n'
            priv_calls += f"    (void){dep_name}_value();\n"
    return textwrap.dedent(f"""\
        #include "{target_name}.h"
        #include <string>
        {priv_includes}
        std::string {target_name}_info() {{
        {priv_calls}    return "{target_name} v1.0";
        }}
    """)


def gen_test_source(target_name: str) -> str:
    return textwrap.dedent(f"""\
        #include "{target_name}.h"
        #include <cassert>
        #include <iostream>

        int main() {{
            assert({target_name}_value() == 42);
            std::cout << {target_name}_info() << " OK\\n";
            return 0;
        }}
    """)


def gen_target_cmake(target_name: str, alias_prefix: str,
                     target_type: str, sources: list[str],
                     headers: list[str], deps: list[tuple[str, str, str]]) -> str:
    lines = []
    lines.append(f'set(DIR_TARGET_NAME {target_name})')
    lines.append(f'set(DIR_TARGET_TYPE {target_type})')
    lines.append(f'set(DIR_ALIAS_PREFIX {alias_prefix})')
    lines.append(f'set(DIR_SOURCES {" ".join(sources)})')
    if headers:
        lines.append(f'set(DIR_HEADERS {" ".join(headers)})')

    pub_deps = [f"{ns}::{name}" for ns, name, kind in deps if kind == "PUBLIC"]
    priv_deps = [f"{ns}::{name}" for ns, name, kind in deps if kind == "PRIVATE"]
    if pub_deps:
        lines.append(f'set(DIR_PUBLIC_DEPS {" ".join(pub_deps)})')
    if priv_deps:
        lines.append(f'set(DIR_PRIVATE_DEPS {" ".join(priv_deps)})')

    lines.append(f'include(${{CMAKE_SOURCE_DIR}}/cmake/AddTarget.cmake)')
    return "\n".join(lines) + "\n"


def gen_project_cmake(project_name: str, namespace: str,
                      modules: list[str], has_tests: bool) -> str:
    lines = [
        f'project({project_name} VERSION 1.0.0 LANGUAGES CXX)',
        f'list(APPEND CMAKE_MODULE_PATH "${{CMAKE_SOURCE_DIR}}/cmake")',
        f'include(AddModules)',
        f'set(PROJECT_NAMESPACE "{namespace}")',
        f'',
        f'add_modules({" ".join(modules)})',
    ]
    if has_tests:
        lines += [
            '',
            'include(CTest)',
            'if(BUILD_TESTING)',
            '  enable_testing()',
            '  add_modules(tests)',
            'endif()',
        ]
    return "\n".join(lines) + "\n"


def generate(num_projects: int, modules_per_project: int,
             dep_density: float, test_ratio: float, seed: int):
    rng = random.Random(seed)
    mod_names = [chr(ord('a') + i) for i in range(min(modules_per_project, 26))]

    all_libs: list[tuple[str, str, str]] = []
    generated_projects = []

    for pi in range(1, num_projects + 1):
        proj_name = f"{PREFIX}{pi:03d}"
        namespace = f"pp{pi:03d}"
        proj_dir = PROJECTS_DIR / proj_name
        proj_dir.mkdir(parents=True, exist_ok=True)

        has_tests = rng.random() < test_ratio
        module_dirs = []
        project_libs = []

        for mi, mod_letter in enumerate(mod_names):
            mod_name = f"p{pi:03d}_{mod_letter}"
            mod_dir = proj_dir / f"mod_{mod_letter}"
            mod_dir.mkdir(exist_ok=True)
            module_dirs.append(f"mod_{mod_letter}")

            num_deps = 0
            if all_libs:
                max_deps = max(1, int(len(all_libs) * dep_density))
                num_deps = rng.randint(0, min(max_deps, 4))
            deps = rng.sample(all_libs, min(num_deps, len(all_libs)))
            dep_tuples = [(ns, name, rng.choice(["PUBLIC", "PRIVATE"]))
                          for ns, name, _ in deps]

            (mod_dir / f"{mod_name}.h").write_text(
                gen_header(mod_name, dep_tuples), encoding="utf-8")
            (mod_dir / f"{mod_name}.cpp").write_text(
                gen_source(mod_name, dep_tuples), encoding="utf-8")
            (mod_dir / "CMakeLists.txt").write_text(
                gen_target_cmake(mod_name, namespace, "LIBRARY",
                                 [f"{mod_name}.cpp"], [f"{mod_name}.h"],
                                 dep_tuples),
                encoding="utf-8")

            project_libs.append((namespace, mod_name, ""))
            all_libs.append((namespace, mod_name, ""))

        if has_tests:
            tests_dir = proj_dir / "tests" / "smoke"
            tests_dir.mkdir(parents=True, exist_ok=True)
            test_target = project_libs[-1]
            test_name = f"test_{proj_name}"
            test_dep_ns, test_dep_name, _ = test_target
            (tests_dir / f"{test_name}.cpp").write_text(
                gen_test_source(test_dep_name), encoding="utf-8")
            (tests_dir / "CMakeLists.txt").write_text(
                gen_target_cmake(test_name, namespace, "EXECUTABLE",
                                 [f"{test_name}.cpp"], [],
                                 [(test_dep_ns, test_dep_name, "PRIVATE")]),
                encoding="utf-8")

        (proj_dir / "CMakeLists.txt").write_text(
            gen_project_cmake(proj_name, namespace, module_dirs, has_tests),
            encoding="utf-8")

        generated_projects.append(proj_name)

    total_libs = len(all_libs)
    total_deps = sum(1 for _ in all_libs)
    print(f"Generated {num_projects} projects, {total_libs} library targets")
    print(f"Projects: {generated_projects[0]} .. {generated_projects[-1]}")
    return generated_projects


def update_root_cmake(project_names: list[str]):
    cmake_path = ROOT / "CMakeLists.txt"
    text = cmake_path.read_text(encoding="utf-8")

    import re
    m = re.search(
        r'(add_workspace_projects\s*\(\s*ROOT\s+"[^"]*"\s*ONLY)\s+([\s\S]*?)\)',
        text
    )
    if not m:
        print("WARNING: Could not find add_workspace_projects ONLY block in root CMakeLists.txt")
        print("Add these projects manually to the ONLY list:")
        for name in project_names:
            print(f"    {name}")
        return

    existing = m.group(2).strip().split()
    all_names = existing + [n for n in project_names if n not in existing]
    indent = "\n    "
    new_list = indent + indent.join(all_names) + "\n"
    new_block = f"{m.group(1)}{new_list})"
    new_text = text[:m.start()] + new_block + text[m.end():]
    cmake_path.write_text(new_text, encoding="utf-8")
    print(f"Updated root CMakeLists.txt: {len(all_names)} projects in ONLY list")


def main():
    parser = argparse.ArgumentParser(description="Generate large monorepo for perf testing")
    parser.add_argument("--projects", type=int, default=50,
                        help="Number of projects to generate (default: 50)")
    parser.add_argument("--modules-per-project", type=int, default=3,
                        help="Modules per project (default: 3, max: 26)")
    parser.add_argument("--dep-density", type=float, default=0.1,
                        help="Dependency density 0.0-1.0 (default: 0.1)")
    parser.add_argument("--test-ratio", type=float, default=0.3,
                        help="Fraction of projects with tests (default: 0.3)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    parser.add_argument("--clean", action="store_true",
                        help="Remove all generated projects and exit")
    parser.add_argument("--no-update-root", action="store_true",
                        help="Don't update root CMakeLists.txt")
    args = parser.parse_args()

    if args.clean:
        clean()
        return

    names = generate(
        num_projects=args.projects,
        modules_per_project=args.modules_per_project,
        dep_density=args.dep_density,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    if not args.no_update_root:
        update_root_cmake(names)

    print(f"\nTo configure and build:")
    print(f"  cmake -S . -B build-perf -G Ninja -DCMAKE_BUILD_TYPE=Release")
    print(f"  cmake --build build-perf")
    print(f"\nTo test dashboard performance:")
    print(f"  python ui.py")
    print(f"\nTo clean up:")
    print(f"  python scripts/gen_large_repo.py --clean")


if __name__ == "__main__":
    main()
