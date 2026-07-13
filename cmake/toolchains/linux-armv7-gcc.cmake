# Cross-compilation toolchain: Linux ARMv7 (32-bit ARM) with GCC
#
# Prerequisites:
#   sudo apt install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
#
# Usage:
#   cmake -S . -B build-armv7 -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/linux-armv7-gcc.cmake

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR armv7l)

set(CMAKE_C_COMPILER   arm-linux-gnueabihf-gcc)
set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)

set(CMAKE_FIND_ROOT_PATH /usr/arm-linux-gnueabihf)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
