include(CMakePackageConfigHelpers)
include(GNUInstallDirs)

# setup_package 用于配置 CMake 包的安装与导出。
# setup_package(
#   PACKAGE_NAME "Name"
#   PACKAGE_NAMESPACE "ns"
#   EXPORT_NAME "NameTargets"
#   APPEND_GIT_HASH ON   # 在 config 中记录 <Name>_GIT_HASH，包名不变
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

  # 包名保持稳定，find_package(<name>) 才能找到；git 哈希只记录在 config 文件里。
  set(_pkg_name "${SP_PACKAGE_NAME}")
  set(_git_line "")
  if(SP_APPEND_GIT_HASH)
    if(NOT SP_GIT_LENGTH)
      set(SP_GIT_LENGTH 6)
    endif()
    # 同一次配置内只调用一次 git，结果缓存在全局属性中。
    get_property(_git_sha GLOBAL PROPERTY _SP_GIT_SHA_${SP_GIT_LENGTH})
    if(NOT _git_sha)
      find_program(GIT_EXECUTABLE git)
      if(GIT_EXECUTABLE AND EXISTS "${CMAKE_SOURCE_DIR}/.git")
        execute_process(
          COMMAND "${GIT_EXECUTABLE}" -C "${CMAKE_SOURCE_DIR}" rev-parse --short=${SP_GIT_LENGTH} HEAD
          OUTPUT_VARIABLE _git_sha
          OUTPUT_STRIP_TRAILING_WHITESPACE
          ERROR_QUIET
        )
      endif()
      set_property(GLOBAL PROPERTY _SP_GIT_SHA_${SP_GIT_LENGTH} "${_git_sha}")
    endif()
    if(_git_sha MATCHES "^[0-9A-Fa-f]+$")
      set(_git_line "set(${_pkg_name}_GIT_HASH \"${_git_sha}\")\n")
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
  file(WRITE "${_bt_cfg}" "include(\"\${CMAKE_CURRENT_LIST_DIR}/${SP_EXPORT_NAME}.cmake\")\n${_git_line}")

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
