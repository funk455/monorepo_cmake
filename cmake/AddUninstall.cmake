# 添加一个自定义目标 "uninstall"，用于删除已安装文件。
# 会从 cmake_uninstall.cmake.in 生成辅助脚本。
set(MODULE_DIR "${CMAKE_CURRENT_LIST_DIR}")
function(add_uninstall_target)
  # 防止重复添加 uninstall 目标。
  get_property(_added GLOBAL PROPERTY _UNINSTALL_TARGET_ADDED)
  if(_added)
    return()
  endif()
  configure_file(
    "${MODULE_DIR}/cmake_uninstall.cmake.in"
    "${CMAKE_BINARY_DIR}/cmake_uninstall.cmake"
    @ONLY
  )

  # uninstall 目标调用生成的脚本。
  add_custom_target(uninstall
    COMMAND ${CMAKE_COMMAND} -P "${CMAKE_BINARY_DIR}/cmake_uninstall.cmake"
    COMMENT "Remove files listed in install_manifest.txt"
    VERBATIM
  )

  # 标记已添加，避免重复。
  set_property(GLOBAL PROPERTY _UNINSTALL_TARGET_ADDED TRUE)
endfunction()
