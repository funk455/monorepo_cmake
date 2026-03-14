#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "net::network" for configuration "Release"
set_property(TARGET net::network APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(net::network PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libnetwork.a"
  )

list(APPEND _cmake_import_check_targets net::network )
list(APPEND _cmake_import_check_files_for_net::network "${_IMPORT_PREFIX}/lib/libnetwork.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
