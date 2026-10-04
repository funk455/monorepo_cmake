project(projectlib VERSION 1.0.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)
set(PROJECT_NAMESPACE "test")

# Build the library and a demo executable
add_modules(projectlib app)

# BUILD_TESTING 由根 CMakeLists 的 include(CTest) 定义；子项目不要再 include(CTest)，
# 否则每个子项目都会重新执行一遍 CTest 的工具探测（大量 find_program），拖慢 configure。
if(BUILD_TESTING)
  add_modules(tests)
endif()
