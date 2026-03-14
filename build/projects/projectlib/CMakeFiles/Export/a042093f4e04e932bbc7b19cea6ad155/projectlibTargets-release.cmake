#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "proj::projectlib" for configuration "Release"
set_property(TARGET proj::projectlib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(proj::projectlib PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libprojectlib.a"
  )

list(APPEND _cmake_import_check_targets proj::projectlib )
list(APPEND _cmake_import_check_files_for_proj::projectlib "${_IMPORT_PREFIX}/lib/libprojectlib.a" )

# Import target "proj::proj_demo" for configuration "Release"
set_property(TARGET proj::proj_demo APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(proj::proj_demo PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/proj_demo"
  )

list(APPEND _cmake_import_check_targets proj::proj_demo )
list(APPEND _cmake_import_check_files_for_proj::proj_demo "${_IMPORT_PREFIX}/bin/proj_demo" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
