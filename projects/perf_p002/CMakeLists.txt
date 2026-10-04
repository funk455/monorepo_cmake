project(perf_p002 VERSION 1.0.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)
set(PROJECT_NAMESPACE "pp002")

add_modules(mod_a mod_b mod_c)

if(BUILD_TESTING)
  add_modules(tests)
endif()
