project(projectlib VERSION 1.0.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)

# Build the library and a demo executable
add_modules(projectlib app)

# Enable tests just for this subproject (optional)
include(CTest)
if(BUILD_TESTING)
  enable_testing()
  add_modules(tests)
endif()

include(SetupPackage)
set(PROJECT_NAMESPACE "proj")
setup_package(
  PACKAGE_NAME      "${PROJECT_NAME}"
  PACKAGE_NAMESPACE "${PROJECT_NAMESPACE}"
  APPEND_GIT_HASH   ON
)
