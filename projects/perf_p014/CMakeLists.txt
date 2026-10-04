project(perf_p014 VERSION 1.0.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)
set(PROJECT_NAMESPACE "pp014")

add_modules(mod_a mod_b mod_c)

include(CTest)
if(BUILD_TESTING)
  enable_testing()
  add_modules(tests)
endif()
