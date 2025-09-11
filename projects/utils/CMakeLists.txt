project(utils VERSION 1.0.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)

add_modules(utils)

include(SetupPackage)
set(PROJECT_NAMESPACE "utils")
setup_package(
  PACKAGE_NAME      "${PROJECT_NAME}"
  PACKAGE_NAMESPACE "${PROJECT_NAMESPACE}"
  APPEND_GIT_HASH   ON
)
