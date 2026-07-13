# monorepo-cmake-sample

A CMake-based monorepo build system with a web dashboard. Provides unified target creation, dependency management, cross-compilation, testing, packaging, and a browser UI for the full build workflow.


## Quick Start

```bash
# configure and build
cmake -S . -B build
cmake --build build

# run tests
ctest --test-dir build --output-on-failure
```

## Web Dashboard

```bash
python ui.py
# open http://localhost:8080
```

Features:
- **Dashboard** -- project overview, build directory status, test results
- **Build** -- configure / build / test / install with generator, build type, toolchain selection
- **Targets** -- dependency graph visualization (Mermaid), coupling metrics (Ca / Ce / Instability), cycle detection
- **New Project** -- scaffolding wizard with live preview, GTest option, preset save/load
- **Cross Compile** -- toolchain file management (create from template / edit / delete), one-click cross-build
- **Watch Mode** -- auto-rebuild on file changes
- **Reports** -- build report and test result viewer (JSON / JUnit XML)

## Adding a New Project

### Via CLI

```bash
python cmake/cli.py                    # interactive
python cmake/cli.py --preset preset.json  # from saved preset
```

### Via Web UI

Open the dashboard, go to **New Project**, fill in the form, click **Generate Project**.

### Manual

Create `projects/<name>/CMakeLists.txt`:

```cmake
project(<name> VERSION 0.1.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)
set(PROJECT_NAMESPACE "<ns>")
add_modules(<module1> <module2>)
```

Each module directory gets its own `CMakeLists.txt` using `AddTarget.cmake`:

```cmake
set(DIR_TARGET_NAME  <target>)
set(DIR_TARGET_TYPE  LIBRARY)          # EXECUTABLE | LIBRARY | INTERFACE
set(DIR_SOURCES      foo.cpp)
set(DIR_HEADERS      foo.h)
set(DIR_PUBLIC_DEPS  some::lib)
set(DIR_ALIAS_PREFIX <ns>)
include(${CMAKE_SOURCE_DIR}/cmake/AddTarget.cmake)
```

Then register the project in the root `CMakeLists.txt`:

```cmake
add_workspace_projects(
  ROOT "${CMAKE_SOURCE_DIR}/projects"
  ONLY netlib projectlib utils <name>
)
```

## AddTarget.cmake Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DIR_TARGET_NAME` | yes | -- | Target name |
| `DIR_TARGET_TYPE` | yes | -- | `EXECUTABLE`, `LIBRARY`, or `INTERFACE` |
| `DIR_SOURCES` | for non-INTERFACE | -- | Source file list (no glob) |
| `DIR_HEADERS` | no | `""` | Header file list |
| `DIR_LIBRARY_KIND` | no | auto | `STATIC`, `SHARED`, or omit for CMake default |
| `DIR_ALIAS_PREFIX` | no | `project` | Creates `<prefix>::<name>` alias |
| `DIR_PUBLIC_DEPS` | no | -- | PUBLIC link dependencies |
| `DIR_PRIVATE_DEPS` | no | -- | PRIVATE link dependencies |
| `DIR_INTERFACE_DEPS` | no | -- | INTERFACE link dependencies |
| `DIR_CXX_STD` | no | `cxx_std_20` | C++ standard feature |
| `DIR_INCLUDE_CURRENT` | no | `ON` | Add current dir to include path |
| `DIR_ENABLE_INSTALL` | no | `OFF` | Generate install rules |
| `DIR_EXPORT_NAME` | no | `<project>Targets` | Export set name |
| `DIR_REGISTER_TEST` | no | auto | Register as CTest (auto-on in `/tests/`) |
| `DIR_USE_GTEST` | no | `OFF` | Link GTest and use `gtest_discover_tests` |
| `DIR_ENABLE_FILE_SET` | no | `ON` | Use CMake 3.23+ file sets |
| `DIR_POSITION_INDEPENDENT` | no | `ON` for libs | Set `POSITION_INDEPENDENT_CODE` |

## Cross-Compilation

### Via Web UI

Go to **Cross Compile**, select a toolchain, set build directory, click **Configure** then **Build**.

### Via CLI

```bash
cmake -S . -B build-arm64 \
  -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/linux-aarch64-gcc.cmake \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build-arm64
```

Included toolchain files:

| File | Target |
|---|---|
| `linux-aarch64-gcc.cmake` | Linux ARM64 via GCC cross-compiler |
| `linux-armv7-gcc.cmake` | Linux ARMv7 (32-bit) via GCC |
| `mingw-w64.cmake` | Windows x86_64 via MinGW-w64 |
| `emscripten.cmake` | WebAssembly via Emscripten |
| `android-ndk.cmake` | Android via NDK |
| `macos-arm64-clang.cmake` | macOS Apple Silicon via Clang |

Custom toolchain files can be created in the web UI's toolchain editor or placed directly in `cmake/toolchains/`.

## Install & Export

Libraries with `DIR_ENABLE_INSTALL ON` can be installed and consumed via `find_package`:

```cmake
# in the library's CMakeLists.txt
include(${CMAKE_SOURCE_DIR}/cmake/SetupPackage.cmake)
setup_package(
  PACKAGE_NAME      "mylib"
  PACKAGE_NAMESPACE "myns"
  APPEND_GIT_HASH   ON        # optional: version suffix with git hash
)
```

```bash
cmake --install build --prefix /usr/local
```

Consumers:

```cmake
find_package(mylib REQUIRED)
target_link_libraries(app PRIVATE myns::mylib)
```

## Testing

CTest is enabled at the workspace root. Test targets in `tests/` directories are auto-registered.

For Google Test:

```cmake
set(DIR_USE_GTEST ON)    # links GTest::gtest_main, uses gtest_discover_tests
```

GTest is fetched automatically via `SetupGTest.cmake` (FetchContent with `find_package` fallback).

## Reports

```bash
cmake --build build --target report-build   # build-report.json
cmake --build build --target report-test    # tests.log + tests.junit.xml
cmake --build build --target report-all     # both
```

Reports are written to `<build-dir>/reports/` and viewable in the web dashboard.

## Watch Mode

Auto-rebuild on source file changes:

```bash
python cmake/watch_build.py --build build --build-type Release
```

Options: `--interval` (seconds), `--exts` (file extensions), `--generator`, `--config` (multi-config).

Also available in the web dashboard under **Watch Mode**.

## Multi-Platform Build Helper

```bash
python cmake/build.py --platform windows --generator "Visual Studio 17 2022" --config Release --build
python cmake/build.py --platform linux --generator Ninja --build-type Release --build
```

## Packaging

```bash
cmake -P cmake/DeployPackage.cmake
```

Options via cache variables: `DEPLOY_COPY_PROJECTS` (ON), `DEPLOY_COPY_DOCS` (ON).

## Requirements

- CMake >= 3.20
- Python >= 3.7 (for UI and CLI tools, no pip dependencies)
- C++20 capable compiler
