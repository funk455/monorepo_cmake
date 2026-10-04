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

# 统一输出目录。多配置生成器（VS/Xcode/Ninja Multi-Config）会自动追加 <Config>/ 子目录，
# 即 bin/Debug、bin/Release，不同配置的产物互不覆盖，因此不设置按配置的覆盖变量。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${_BIN}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${_LIB}")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${_LIB}")

if(UNIX)
  # 构建树内：可执行文件直接从 build/lib 找项目动态库。
  set(CMAKE_BUILD_RPATH "${_LIB}")
  # 安装后：按可执行文件自身位置找 ../lib，安装目录整体移动后仍可运行。
  # （USE_LINK_PATH 只会加入项目外部的库目录，不覆盖项目自己的库。）
  if(NOT DEFINED CMAKE_INSTALL_RPATH)
    include(GNUInstallDirs)
    if(APPLE)
      set(CMAKE_INSTALL_RPATH "@loader_path/../${CMAKE_INSTALL_LIBDIR}")
    else()
      set(CMAKE_INSTALL_RPATH "$ORIGIN/../${CMAKE_INSTALL_LIBDIR}")
    endif()
  endif()
  set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
endif()

# 清理内部变量。
unset(_BIN)
unset(_LIB)
