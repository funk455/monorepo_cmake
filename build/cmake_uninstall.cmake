if(NOT EXISTS "/home/monorepo-cmake-sample/build/install_manifest.txt")
  message(FATAL_ERROR "Cannot find install manifest: /home/monorepo-cmake-sample/build/install_manifest.txt
Hint: run 'cmake --install <build>' once before uninstall.")
endif()

file(READ "/home/monorepo-cmake-sample/build/install_manifest.txt" _manifest)

string(REPLACE "\r\n" "\n" _manifest "${_manifest}")
string(REPLACE "\r"   "\n" _manifest "${_manifest}")

string(REPLACE "\n" ";" _files "${_manifest}")

set(_fail FALSE)
foreach(_f IN LISTS _files)
  if(_f STREQUAL "")
    continue()
  endif()
  if(EXISTS "${_f}" OR IS_SYMLINK "${_f}")
    message(STATUS "Uninstalling: ${_f}")
    file(REMOVE "${_f}")
    if(EXISTS "${_f}")
      message(WARNING "Failed to remove: ${_f}")
      set(_fail TRUE)
    endif()
  else()
    message(STATUS "Skip (not found): ${_f}")
  endif()
endforeach()

if(_fail)
  message(WARNING "Uninstall completed with errors (some files could not be removed).")
else()
  message(STATUS "Uninstall finished.")
endif()
