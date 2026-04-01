# UnifiedOutputDirs.cmake
# 统一二进制与库的构建输出目录。

if(NOT DEFINED UNIFIED_BIN_SUBDIR)  
  set(UNIFIED_BIN_SUBDIR "bin") 
endif()
if(NOT DEFINED UNIFIED_LIB_SUBDIR)  
  set(UNIFIED_LIB_SUBDIR "lib") 
endif()
if(IS_ABSOLUTE "${UNIFIED_BIN_SUBDIR}")
  # 直接使用绝对的 bin 路径。
  set(_BIN "${UNIFIED_BIN_SUBDIR}")
else()
  # 将 bin 路径解析为相对构建目录的路径。
  set(_BIN "${CMAKE_BINARY_DIR}/${UNIFIED_BIN_SUBDIR}")
endif()

if(IS_ABSOLUTE "${UNIFIED_LIB_SUBDIR}")
  # 直接使用绝对的 lib 路径。
  set(_LIB "${UNIFIED_LIB_SUBDIR}")
else()
  # 将 lib 路径解析为相对构建目录的路径。
  set(_LIB "${CMAKE_BINARY_DIR}/${UNIFIED_LIB_SUBDIR}")
endif()

# 为单配置生成器设置统一输出目录。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${_BIN}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${_LIB}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${_LIB}")

if(CMAKE_CONFIGURATION_TYPES)
  # 为多配置生成器设置按配置的输出目录。
  foreach(cfg IN LISTS CMAKE_CONFIGURATION_TYPES)
    string(TOUPPER "${cfg}" cfgU)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${cfgU} "${_BIN}")
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${cfgU} "${_LIB}")
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${cfgU} "${_LIB}")
  endforeach()
endif()

if(UNIX OR APPLE)
  # 改善类 UNIX 系统上的运行时链接行为。
  set(CMAKE_BUILD_RPATH "${_LIB}")
  set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
endif()

# 清理内部变量。
unset(_BIN)
unset(_LIB)
