# 说明：
# add_modules(<mod> [<mod>...])
#
# 为每个模块名添加子目录。对 "tests" 做特殊处理：
# - 如果 tests/ 里有 CMakeLists.txt，直接 add_subdirectory(tests)。
# - 如果 tests/ 只是容器目录，则扫描其一级子目录，发现含 CMakeLists.txt 的就加入。
function(add_modules)
  foreach(mod IN LISTS ARGN) 
    if(mod STREQUAL "tests")
      # 处理 tests/ 作为直接模块或容器目录的两种情况。
      set(tests_root "${CMAKE_CURRENT_SOURCE_DIR}/tests")
      if(EXISTS "${tests_root}/CMakeLists.txt")
        add_subdirectory(tests)
      elseif(EXISTS "${tests_root}")
        file(GLOB children LIST_DIRECTORIES TRUE "${tests_root}/*")
        foreach(child IN LISTS children)
          if(IS_DIRECTORY "${child}" AND EXISTS "${child}/CMakeLists.txt")
            file(RELATIVE_PATH rel "${CMAKE_CURRENT_SOURCE_DIR}" "${child}")
            add_subdirectory("${rel}")
          endif()
        endforeach()
      else()
        message(STATUS "[AddModules] no tests/ directory in ${CMAKE_CURRENT_SOURCE_DIR}")
      endif()
    else()
      # 普通模块：要求 <mod>/CMakeLists.txt 必须存在。
      set(dir "${CMAKE_CURRENT_SOURCE_DIR}/${mod}")
      if(EXISTS "${dir}/CMakeLists.txt")
        add_subdirectory("${mod}")
      else()
        message(FATAL_ERROR "[AddModules] '${mod}/CMakeLists.txt' not found in ${CMAKE_CURRENT_SOURCE_DIR}")
      endif()
    endif()
  endforeach()
endfunction()
