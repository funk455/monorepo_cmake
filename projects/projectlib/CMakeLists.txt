project(projectlib VERSION 1.0.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)
set(PROJECT_NAMESPACE "test")

# Build the library and a demo executable
add_modules(projectlib app)

# Enable tests just for this subproject (optional)
include(CTest)
if(BUILD_TESTING)
  enable_testing()
  add_modules(tests)
endif()
