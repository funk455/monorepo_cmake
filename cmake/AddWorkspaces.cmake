# 用法：
#   include(AddWorkspaces)
#   add_workspace_projects(
#     ROOT "${CMAKE_SOURCE_DIR}/projects"   # 可选，默认 ${CMAKE_SOURCE_DIR}/projects
#     DIRS  pathA pathB                     # 可选：显式目录（相对 CMAKE_SOURCE_DIR 或绝对路径）
#     ONLY   netlib utils                   # 可选：只加入 ROOT 下这些名字的项目
#     EXCLUDE legacy                        # 可选：排除这些名字的项目
#   )
#
# 项目查找规则（按优先级）：
#   1. DIRS：直接使用给出的目录。
#   2. ONLY：直接检查 ROOT/<name>/CMakeLists.txt，不扫描目录树。
#   3. 都没给：取 ROOT 下一级、含 CMakeLists.txt 的子目录。
# 每个目录只会被 add_subdirectory 一次（记录在全局属性 AWP_ADDED_DIRS 中）。

function(add_workspace_projects)
  cmake_parse_arguments(AWP "" "ROOT" "DIRS;ONLY;EXCLUDE" ${ARGN})

  if(NOT AWP_ROOT)
    set(AWP_ROOT "${CMAKE_SOURCE_DIR}/projects")
  endif()
  if(NOT EXISTS "${AWP_ROOT}")
    message(FATAL_ERROR "[add_workspace_projects] ROOT not found: ${AWP_ROOT}")
  endif()

  set(_dirs)
  if(AWP_DIRS)
    foreach(d IN LISTS AWP_DIRS)
      if(NOT IS_ABSOLUTE "${d}")
        set(d "${CMAKE_SOURCE_DIR}/${d}")
      endif()
      list(APPEND _dirs "${d}")
    endforeach()
  elseif(AWP_ONLY)
    foreach(name IN LISTS AWP_ONLY)
      list(APPEND _dirs "${AWP_ROOT}/${name}")
    endforeach()
  else()
    file(GLOB _children LIST_DIRECTORIES TRUE "${AWP_ROOT}/*")
    foreach(d IN LISTS _children)
      if(IS_DIRECTORY "${d}" AND EXISTS "${d}/CMakeLists.txt")
        list(APPEND _dirs "${d}")
      endif()
    endforeach()
  endif()

  get_property(_added GLOBAL PROPERTY AWP_ADDED_DIRS)
  foreach(d IN LISTS _dirs)
    get_filename_component(name "${d}" NAME)
    if(name IN_LIST AWP_EXCLUDE)
      continue()
    endif()
    if(NOT EXISTS "${d}/CMakeLists.txt")
      message(WARNING "[add_workspace_projects] CMakeLists.txt not found in: ${d}")
      continue()
    endif()
    file(RELATIVE_PATH rel "${CMAKE_SOURCE_DIR}" "${d}")
    if(rel IN_LIST _added)
      continue()
    endif()
    message(STATUS "[AddWorkspaces] add_subdirectory(${rel})")
    add_subdirectory("${rel}")
    list(APPEND _added "${rel}")
  endforeach()
  set_property(GLOBAL PROPERTY AWP_ADDED_DIRS "${_added}")
endfunction()
