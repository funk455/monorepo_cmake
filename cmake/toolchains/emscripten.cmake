# Cross-compilation toolchain: WebAssembly via Emscripten
#
# Prerequisites:
#   Install emsdk: https://emscripten.org/docs/getting_started/downloads.html
#   source /path/to/emsdk/emsdk_env.sh
#
# Usage:
#   cmake -S . -B build-wasm -DCMAKE_TOOLCHAIN_FILE=cmake/toolchains/emscripten.cmake
#
# Note: If EMSDK is set in your environment, this file will locate the
# upstream Emscripten toolchain automatically. Otherwise set EMSDK_ROOT.

if(DEFINED ENV{EMSDK})
  set(_emsdk "$ENV{EMSDK}")
elseif(DEFINED EMSDK_ROOT)
  set(_emsdk "${EMSDK_ROOT}")
else()
  message(FATAL_ERROR "EMSDK environment variable or EMSDK_ROOT not set. "
    "Run 'source emsdk_env.sh' or pass -DEMSDK_ROOT=/path/to/emsdk")
endif()

set(_em_toolchain "${_emsdk}/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake")
if(EXISTS "${_em_toolchain}")
  include("${_em_toolchain}")
else()
  set(CMAKE_SYSTEM_NAME Emscripten)
  set(CMAKE_SYSTEM_PROCESSOR wasm32)
  set(CMAKE_C_COMPILER   "${_emsdk}/upstream/emscripten/emcc")
  set(CMAKE_CXX_COMPILER "${_emsdk}/upstream/emscripten/em++")
  set(CMAKE_AR           "${_emsdk}/upstream/emscripten/emar")
  set(CMAKE_RANLIB       "${_emsdk}/upstream/emscripten/emranlib")
endif()
