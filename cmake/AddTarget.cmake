# AddTarget.cmake
# 统一创建可执行文件或库目标，并提供一致的默认行为。
# 要求显式列出源码文件，避免 glob 触发重新配置与不必要的重编译。
#
# 必填：
#   - DIR_TARGET_NAME
#   - DIR_TARGET_TYPE (EXECUTABLE|LIBRARY|INTERFACE)
#
# 可选：
#   - DIR_LIBRARY_KIND, DIR_PUBLIC_DEPS, DIR_PRIVATE_DEPS, DIR_INTERFACE_DEPS
#   - DIR_ALIAS_PREFIX (默认 "project"), DIR_INCLUDE_CURRENT (默认 ON)
#   - DIR_SOURCES (显式列表，INTERFACE 类型时可省略), DIR_HEADERS (可选)
#   - DIR_ENABLE_FILE_SET (默认 ON，CMake >= 3.23)
#   - DIR_POSITION_INDEPENDENT (库默认 ON), DIR_CXX_STD (默认 cxx_std_20)
#   - DIR_REGISTER_TEST (默认 OFF), DIR_TEST_NAME
#   - DIR_USE_GTEST (默认 OFF) — 链接 GTest::gtest_main 并用 gtest_discover_tests 注册
#   - DIR_ENABLE_INSTALL (默认 OFF), DIR_EXPORT_NAME
include(GNUInstallDirs)

# 本模块要求调用方先设置 DIR_* 变量，然后 include 本文件，
# 以统一方式创建并配置目标。

if(NOT DEFINED DIR_TARGET_NAME)
  message(FATAL_ERROR "[AddTarget] DIR_TARGET_NAME is required")
endif()

if(NOT DEFINED DIR_TARGET_TYPE)
  message(FATAL_ERROR "[AddTarget] DIR_TARGET_TYPE is required (EXECUTABLE or LIBRARY)")
endif()

if(NOT DEFINED DIR_ALIAS_PREFIX)
  set(DIR_ALIAS_PREFIX "project")
endif()
if(NOT DEFINED DIR_INCLUDE_CURRENT)
  set(DIR_INCLUDE_CURRENT ON)
endif()
if(NOT DEFINED DIR_ENABLE_FILE_SET)
  set(DIR_ENABLE_FILE_SET ON)
endif()
if(NOT DEFINED DIR_CXX_STD)
  set(DIR_CXX_STD cxx_std_20)
endif()
if(NOT DEFINED DIR_ENABLE_INSTALL)
  set(DIR_ENABLE_INSTALL OFF)
endif()

if(NOT DEFINED DIR_REGISTER_TEST)
  if(CMAKE_CURRENT_SOURCE_DIR MATCHES "/tests(/|$)")
    set(DIR_REGISTER_TEST ON)
  else()
    set(DIR_REGISTER_TEST OFF)
  endif()
endif()

if(NOT DEFINED DIR_USE_GTEST)
  set(DIR_USE_GTEST OFF)
endif()

if(NOT DEFINED DIR_SOURCES)
  if(NOT DIR_TARGET_TYPE STREQUAL "INTERFACE")
    message(FATAL_ERROR "[AddTarget] DIR_SOURCES is required to avoid glob-based reconfigure")
  endif()
  set(DIR_SOURCES "")
endif()

if(NOT DEFINED DIR_HEADERS)
  set(DIR_HEADERS "")
endif()

if(DIR_TARGET_TYPE STREQUAL "EXECUTABLE")
  add_executable(${DIR_TARGET_NAME} ${DIR_SOURCES} ${DIR_HEADERS})
elseif(DIR_TARGET_TYPE STREQUAL "LIBRARY")
  if(DEFINED DIR_LIBRARY_KIND)
    add_library(${DIR_TARGET_NAME} ${DIR_LIBRARY_KIND} ${DIR_SOURCES} ${DIR_HEADERS})
  else()
    add_library(${DIR_TARGET_NAME} ${DIR_SOURCES} ${DIR_HEADERS})
  endif()
elseif(DIR_TARGET_TYPE STREQUAL "INTERFACE")
  add_library(${DIR_TARGET_NAME} INTERFACE)
else()
  message(FATAL_ERROR "[AddTarget] Unknown DIR_TARGET_TYPE='${DIR_TARGET_TYPE}' (expected EXECUTABLE, LIBRARY, or INTERFACE)")
endif()

if(DIR_TARGET_TYPE STREQUAL "LIBRARY" OR DIR_TARGET_TYPE STREQUAL "INTERFACE")
  add_library(${DIR_ALIAS_PREFIX}::${DIR_TARGET_NAME} ALIAS ${DIR_TARGET_NAME})
endif()

if(DIR_TARGET_TYPE STREQUAL "INTERFACE")
  target_compile_features(${DIR_TARGET_NAME} INTERFACE ${DIR_CXX_STD})
else()
  target_compile_features(${DIR_TARGET_NAME} PUBLIC ${DIR_CXX_STD})
endif()

# 头文件走 FILE_SET 时，CMake 会自动把 BASE_DIRS 加入构建树的 include 路径，
# 因此不再重复添加 BUILD_INTERFACE。
set(_use_file_set FALSE)
if(DIR_ENABLE_FILE_SET AND CMAKE_VERSION VERSION_GREATER_EQUAL "3.23" AND DIR_HEADERS)
  set(_use_file_set TRUE)
endif()

if(DIR_INCLUDE_CURRENT)
  if(DIR_TARGET_TYPE STREQUAL "LIBRARY" OR DIR_TARGET_TYPE STREQUAL "INTERFACE")
    if(DIR_TARGET_TYPE STREQUAL "LIBRARY")
      set(_inc_scope PUBLIC)
    else()
      set(_inc_scope INTERFACE)
    endif()
    # INSTALL_INTERFACE 始终保留：导出文件里 FILE_SET 提供的 include 路径被包在
    # if(CMAKE_VERSION >= 3.23) 中，用 3.20~3.22 的使用方只能靠这一条找到头文件。
    set(_inc_dirs $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/${DIR_TARGET_NAME}>)
    if(NOT _use_file_set)
      list(APPEND _inc_dirs $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)
    endif()
    target_include_directories(${DIR_TARGET_NAME} ${_inc_scope} ${_inc_dirs})
  elseif(NOT _use_file_set)
    target_include_directories(${DIR_TARGET_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
  endif()
endif()

if(DIR_TARGET_TYPE STREQUAL "LIBRARY")
  if(NOT DEFINED DIR_POSITION_INDEPENDENT)
    set(DIR_POSITION_INDEPENDENT ON)
  endif()
  set_target_properties(${DIR_TARGET_NAME} PROPERTIES POSITION_INDEPENDENT_CODE ${DIR_POSITION_INDEPENDENT})
endif()

if(_use_file_set)
  if(DIR_TARGET_TYPE STREQUAL "INTERFACE")
    set(_fs_scope INTERFACE)
  else()
    set(_fs_scope PUBLIC)
  endif()
  target_sources(${DIR_TARGET_NAME}
    ${_fs_scope}
      FILE_SET HEADERS
      BASE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}
      FILES ${DIR_HEADERS}
  )
endif()

if(DEFINED DIR_PUBLIC_DEPS OR DEFINED DIR_PRIVATE_DEPS OR DEFINED DIR_INTERFACE_DEPS)
  if(DIR_TARGET_TYPE STREQUAL "INTERFACE")
    target_link_libraries(${DIR_TARGET_NAME}
      INTERFACE ${DIR_PUBLIC_DEPS} ${DIR_INTERFACE_DEPS}
    )
  else()
    target_link_libraries(${DIR_TARGET_NAME}
      PUBLIC    ${DIR_PUBLIC_DEPS}
      PRIVATE   ${DIR_PRIVATE_DEPS}
      INTERFACE ${DIR_INTERFACE_DEPS}
    )
  endif()
endif()

if(DIR_USE_GTEST AND DIR_TARGET_TYPE STREQUAL "EXECUTABLE")
  include("${CMAKE_CURRENT_LIST_DIR}/SetupGTest.cmake")
  setup_gtest()
  target_link_libraries(${DIR_TARGET_NAME} PRIVATE GTest::gtest_main)
  if(DIR_REGISTER_TEST)
    include(GoogleTest)
    gtest_discover_tests(${DIR_TARGET_NAME}
      WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
  endif()
elseif(DIR_REGISTER_TEST AND DIR_TARGET_TYPE STREQUAL "EXECUTABLE")
  if(NOT DEFINED DIR_TEST_NAME)
    set(DIR_TEST_NAME ${DIR_TARGET_NAME})
  endif()
  add_test(NAME ${DIR_TEST_NAME} COMMAND ${DIR_TARGET_NAME})
endif()

if(DIR_ENABLE_INSTALL)
  if(NOT DEFINED DIR_EXPORT_NAME)
    if(DEFINED PROJECT_EXPORT_NAME)
      set(DIR_EXPORT_NAME "${PROJECT_EXPORT_NAME}")
    else()
      set(DIR_EXPORT_NAME "${PROJECT_NAME}Targets")
    endif()
  endif()

  set(_install_args EXPORT ${DIR_EXPORT_NAME})
  if(DIR_TARGET_TYPE STREQUAL "EXECUTABLE")
    list(APPEND _install_args RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
  elseif(DIR_TARGET_TYPE STREQUAL "LIBRARY")
    list(APPEND _install_args
      ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
      LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
      RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
  endif()
  set(_header_dest ${CMAKE_INSTALL_INCLUDEDIR}/${DIR_TARGET_NAME})
  if(_use_file_set)
    list(APPEND _install_args FILE_SET HEADERS DESTINATION ${_header_dest})
  endif()
  install(TARGETS ${DIR_TARGET_NAME} ${_install_args})

  # 不走 FILE_SET 时（CMake < 3.23 或关闭），头文件单独安装；
  # include 路径由前面 target_include_directories 的 INSTALL_INTERFACE 提供。
  if(DIR_HEADERS AND NOT _use_file_set AND NOT DIR_TARGET_TYPE STREQUAL "EXECUTABLE")
    install(FILES ${DIR_HEADERS} DESTINATION ${_header_dest})
  endif()
endif()

# 清理临时变量，避免状态泄漏到调用方。
unset(DIR_TARGET_NAME)
unset(DIR_TARGET_TYPE)
unset(DIR_LIBRARY_KIND)
unset(DIR_PUBLIC_DEPS)
unset(DIR_PRIVATE_DEPS)
unset(DIR_INTERFACE_DEPS)
unset(DIR_ALIAS_PREFIX)
unset(DIR_INCLUDE_CURRENT)
unset(DIR_SOURCES)
unset(DIR_HEADERS)
unset(DIR_ENABLE_FILE_SET)
unset(DIR_POSITION_INDEPENDENT)
unset(DIR_CXX_STD)
unset(DIR_REGISTER_TEST)
unset(DIR_TEST_NAME)
unset(DIR_USE_GTEST)
unset(DIR_ENABLE_INSTALL)
unset(DIR_EXPORT_NAME)
unset(_use_file_set)
unset(_inc_scope)
unset(_inc_dirs)
unset(_fs_scope)
unset(_install_args)
unset(_header_dest)
