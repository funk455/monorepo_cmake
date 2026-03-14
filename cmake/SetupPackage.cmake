include(CMakePackageConfigHelpers)
include(GNUInstallDirs)

# setup_package 用于配置 CMake 包的安装与导出。
# setup_package(
#   PACKAGE_NAME "Name"
#   PACKAGE_NAMESPACE "ns"
#   EXPORT_NAME "NameTargets"
#   APPEND_GIT_HASH ON
#   GIT_LENGTH 6
# )
function(setup_package)
  set(options APPEND_GIT_HASH)
  set(oneValueArgs PACKAGE_NAME PACKAGE_NAMESPACE EXPORT_NAME GIT_LENGTH)
  set(multiValueArgs)
  cmake_parse_arguments(SP "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  if(NOT SP_PACKAGE_NAME)
    message(FATAL_ERROR "[setup_package] PACKAGE_NAME is required")
  endif()

  if(NOT SP_PACKAGE_NAMESPACE)
    # 优先使用 PROJECT_NAMESPACE 作为默认命名空间。
    if(DEFINED PROJECT_NAMESPACE)
      set(SP_PACKAGE_NAMESPACE "${PROJECT_NAMESPACE}")
    else()
      set(SP_PACKAGE_NAMESPACE "project")
    endif()
  endif()

  if(NOT SP_EXPORT_NAME)
    # 默认导出集合名称使用 PROJECT_EXPORT_NAME 或 <project>Targets。
    if(DEFINED PROJECT_EXPORT_NAME)
      set(SP_EXPORT_NAME "${PROJECT_EXPORT_NAME}")
    else()
      set(SP_EXPORT_NAME "${PROJECT_NAME}Targets")
    endif()
  endif()

  set(_pkg_name "${SP_PACKAGE_NAME}")
  if(SP_APPEND_GIT_HASH)
    # 可选的 git 哈希后缀，用于区分包版本。
    if(NOT SP_GIT_LENGTH)
      set(SP_GIT_LENGTH 6)
    endif()
    find_program(GIT_EXECUTABLE git)
    if(GIT_EXECUTABLE AND EXISTS "${CMAKE_SOURCE_DIR}/.git")
      execute_process(
        COMMAND "${GIT_EXECUTABLE}" -C "${CMAKE_SOURCE_DIR}" rev-parse --short=${SP_GIT_LENGTH} HEAD
        OUTPUT_VARIABLE _git_sha
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
      )
      if(_git_sha MATCHES "^[0-9A-Fa-f]+$")
        set(_pkg_name "${SP_PACKAGE_NAME}-${_git_sha}")
        message(STATUS "[setup_package] Using git suffix: ${_git_sha} → package '${_pkg_name}'")
      endif()
    endif()
  endif()

  # 生成兼容 find_package() 的版本文件。
  write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/${_pkg_name}-config-version.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
  )

  # 生成最小化的 <pkg>-config.cmake，并包含导出文件。
  set(_bt_cfg "${CMAKE_CURRENT_BINARY_DIR}/${_pkg_name}-config.cmake")
  file(WRITE "${_bt_cfg}" "include(\"\${CMAKE_CURRENT_LIST_DIR}/${SP_EXPORT_NAME}.cmake\")\n")

  # 安装导出目标与配置文件。
  install(EXPORT ${SP_EXPORT_NAME}
    NAMESPACE ${SP_PACKAGE_NAMESPACE}::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${_pkg_name}
  )
  install(FILES
    "${_bt_cfg}"
    "${CMAKE_CURRENT_BINARY_DIR}/${_pkg_name}-config-version.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${_pkg_name}
  )

  # 导出目标，供构建树内使用。
  export(EXPORT ${SP_EXPORT_NAME}
         NAMESPACE ${SP_PACKAGE_NAMESPACE}::
         FILE "${CMAKE_CURRENT_BINARY_DIR}/${SP_EXPORT_NAME}.cmake")
endfunction()
