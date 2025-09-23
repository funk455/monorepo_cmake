# cmake/BuildType.cmake
# Debug/Release/RelWithDebInfo/MinSizeRel
# - 单配置生成器：设置/校验 CMAKE_BUILD_TYPE
# - 多配置生成器：限定可用配置并给出一个默认配置提示（使用 --config 选择）

# 可调参数（在 include 本文件前/或命令行 -D 传入）：
#   PROJECT_BUILD_TYPE         想要的构建类型（优先级高于 CMAKE_BUILD_TYPE）
#   PROJECT_DEFAULT_BUILD_TYPE 没指定时的默认值（默认 Release）

set(_BT_ALLOWED "Debug;Release;RelWithDebInfo;MinSizeRel")

set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "${_BT_ALLOWED}")

if(NOT DEFINED PROJECT_DEFAULT_BUILD_TYPE)
  set(PROJECT_DEFAULT_BUILD_TYPE "Release")
endif()

if(CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_CONFIGURATION_TYPES "${_BT_ALLOWED}" CACHE STRING "Configs" FORCE)

  if(DEFINED PROJECT_BUILD_TYPE AND NOT PROJECT_BUILD_TYPE STREQUAL "")
    set(_BT_DEFAULT "${PROJECT_BUILD_TYPE}")
  elseif(DEFINED CMAKE_BUILD_TYPE AND NOT CMAKE_BUILD_TYPE STREQUAL "")
    set(_BT_DEFAULT "${CMAKE_BUILD_TYPE}")
  else()
    set(_BT_DEFAULT "${PROJECT_DEFAULT_BUILD_TYPE}")
  endif()

  list(FIND _BT_ALLOWED "${_BT_DEFAULT}" _idx)
  if(_idx EQUAL -1)
    message(FATAL_ERROR "[BuildType] Unsupported build type '${_BT_DEFAULT}'. Allowed: ${_BT_ALLOWED}")
  endif()

  set(CMAKE_DEFAULT_CONFIG "${_BT_DEFAULT}" CACHE STRING "Default config (use with --config)" FORCE)
  message(STATUS "[BuildType] Multi-config: {${CMAKE_CONFIGURATION_TYPES}}; default: ${CMAKE_DEFAULT_CONFIG} (use: cmake --build <b> --config ${CMAKE_DEFAULT_CONFIG})")

else()
  if(DEFINED PROJECT_BUILD_TYPE AND NOT PROJECT_BUILD_TYPE STREQUAL "")
    set(CMAKE_BUILD_TYPE "${PROJECT_BUILD_TYPE}" CACHE STRING "Build type" FORCE)
  elseif(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "${PROJECT_DEFAULT_BUILD_TYPE}" CACHE STRING "Build type" FORCE)
  else()
    set(CMAKE_BUILD_TYPE "${CMAKE_BUILD_TYPE}" CACHE STRING "Build type" FORCE)
  endif()

  list(FIND _BT_ALLOWED "${CMAKE_BUILD_TYPE}" _idx2)
  if(_idx2 EQUAL -1)
    message(FATAL_ERROR "[BuildType] Unsupported CMAKE_BUILD_TYPE='${CMAKE_BUILD_TYPE}'. Allowed: ${_BT_ALLOWED}")
  endif()

  message(STATUS "[BuildType] Single-config: CMAKE_BUILD_TYPE='${CMAKE_BUILD_TYPE}'")
endif()
