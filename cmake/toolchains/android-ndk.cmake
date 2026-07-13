# Cross-compilation toolchain: Android via NDK
#
# Prerequisites:
#   Install Android NDK: https://developer.android.com/ndk/downloads
#
# Usage:
#   cmake -S . -B build-android \
#     -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/android-ndk.cmake \
#     -DANDROID_NDK=/path/to/ndk \
#     -DANDROID_ABI=arm64-v8a \
#     -DANDROID_PLATFORM=android-24
#
# This file delegates to the NDK's built-in toolchain. Set ANDROID_NDK
# or the ANDROID_NDK_HOME environment variable.

if(DEFINED ANDROID_NDK)
  set(_ndk "${ANDROID_NDK}")
elseif(DEFINED ENV{ANDROID_NDK_HOME})
  set(_ndk "$ENV{ANDROID_NDK_HOME}")
elseif(DEFINED ENV{ANDROID_NDK})
  set(_ndk "$ENV{ANDROID_NDK}")
else()
  message(FATAL_ERROR "ANDROID_NDK not set. Pass -DANDROID_NDK=/path/to/ndk "
    "or set ANDROID_NDK_HOME environment variable.")
endif()

if(NOT DEFINED ANDROID_ABI)
  set(ANDROID_ABI "arm64-v8a")
endif()

if(NOT DEFINED ANDROID_PLATFORM)
  set(ANDROID_PLATFORM "android-24")
endif()

set(_ndk_toolchain "${_ndk}/build/cmake/android.toolchain.cmake")
if(EXISTS "${_ndk_toolchain}")
  include("${_ndk_toolchain}")
else()
  message(FATAL_ERROR "NDK toolchain not found at: ${_ndk_toolchain}")
endif()
