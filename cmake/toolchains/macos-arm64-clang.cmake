# Cross-compilation toolchain: macOS ARM64 (Apple Silicon)
#
# Use this to cross-compile for Apple Silicon from an x86_64 Mac,
# or to explicitly target arm64 on a universal build system.
#
# Usage:
#   cmake -S . -B build-macos-arm64 -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/macos-arm64-clang.cmake

set(CMAKE_SYSTEM_NAME Darwin)
set(CMAKE_SYSTEM_PROCESSOR arm64)

set(CMAKE_OSX_ARCHITECTURES arm64)

set(CMAKE_C_COMPILER   clang)
set(CMAKE_CXX_COMPILER clang++)
