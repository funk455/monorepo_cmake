project(perf_p016 VERSION 1.0.0 LANGUAGES CXX)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(AddModules)
set(PROJECT_NAMESPACE "pp016")

add_modules(mod_a mod_b mod_c)
