# add a target "uninstall"
set(MODULE_DIR "${CMAKE_CURRENT_LIST_DIR}")
function(add_uninstall_target)
  get_property(_added GLOBAL PROPERTY _UNINSTALL_TARGET_ADDED)
  if(_added)
    return()
  endif()
  configure_file(
    "${MODULE_DIR}/cmake_uninstall.cmake.in"
    "${CMAKE_BINARY_DIR}/cmake_uninstall.cmake"
    @ONLY
  )

  add_custom_target(uninstall
    COMMAND ${CMAKE_COMMAND} -P "${CMAKE_BINARY_DIR}/cmake_uninstall.cmake"
    COMMENT "Remove files listed in install_manifest.txt"
    VERBATIM
  )

  set_property(GLOBAL PROPERTY _UNINSTALL_TARGET_ADDED TRUE)
endfunction()
