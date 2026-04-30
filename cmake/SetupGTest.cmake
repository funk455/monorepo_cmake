# SetupGTest.cmake
# Finds GTest via find_package; falls back to FetchContent if not installed.
# Call setup_gtest() before linking against GTest targets.

macro(setup_gtest)
  if(NOT TARGET GTest::gtest)
    find_package(GTest QUIET)
  endif()
  if(NOT TARGET GTest::gtest)
    message(STATUS "[SetupGTest] GTest not found locally — fetching via FetchContent (v1.14.0)")
    include(FetchContent)
    FetchContent_Declare(
      googletest
      GIT_REPOSITORY https://github.com/google/googletest.git
      GIT_TAG        v1.14.0
      GIT_SHALLOW    TRUE
    )
    # Prevent GTest from overriding our compiler/linker settings on Windows
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    set(BUILD_GMOCK             OFF CACHE BOOL "" FORCE)
    set(INSTALL_GTEST           OFF CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
  endif()
endmacro()
