# cmake/DeployPackage.cmake
# 根据当前仓库结构打包构建产物与关键源码/文档。

# 获取 git 短哈希（失败时回退为 nogit）。
execute_process(
  COMMAND git rev-parse --short HEAD
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  OUTPUT_VARIABLE GIT_HASH
  OUTPUT_STRIP_TRAILING_WHITESPACE
  RESULT_VARIABLE _git_ok
)
if(NOT _git_ok EQUAL 0 OR GIT_HASH STREQUAL "")
  set(GIT_HASH "nogit")
endif()

# 打包暂存根目录。
set(DEFAULT_STAGE_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}")

# 默认目录布局（可通过缓存覆盖）。
set(DEFAULT_BIN_DIR "${DEFAULT_STAGE_DIR}/bin")
set(DEFAULT_LIB_DIR "${DEFAULT_STAGE_DIR}/lib")
set(DEFAULT_INCLUDE_DIR "${DEFAULT_STAGE_DIR}/include")
set(DEFAULT_PROJECTS_DIR "${DEFAULT_STAGE_DIR}/projects")
set(DEFAULT_CMAKE_DIR "${DEFAULT_STAGE_DIR}/cmake")
set(DEFAULT_DOCS_DIR "${DEFAULT_STAGE_DIR}/docs")

set(STAGE_DIR ${DEFAULT_STAGE_DIR} CACHE PATH "Package staging root directory")
set(BIN_DIR ${DEFAULT_BIN_DIR} CACHE PATH "Directory for binary files")
set(LIB_DIR ${DEFAULT_LIB_DIR} CACHE PATH "Directory for library files")
set(INCLUDE_DIR ${DEFAULT_INCLUDE_DIR} CACHE PATH "Directory for include files")
set(PROJECTS_DIR ${DEFAULT_PROJECTS_DIR} CACHE PATH "Directory for project sources")
set(CMAKE_DIR ${DEFAULT_CMAKE_DIR} CACHE PATH "Directory for cmake modules")
set(DOCS_DIR ${DEFAULT_DOCS_DIR} CACHE PATH "Directory for docs and metadata")

# 选择性复制开关。
option(DEPLOY_COPY_PROJECTS "Copy projects/ sources into package" ON)
option(DEPLOY_COPY_CMAKE "Copy cmake/ modules into package" ON)
option(DEPLOY_COPY_DOCS "Copy docs/metadata into package" ON)

# 确保暂存目录存在。
file(MAKE_DIRECTORY ${STAGE_DIR})
file(MAKE_DIRECTORY ${BIN_DIR})
file(MAKE_DIRECTORY ${LIB_DIR})
file(MAKE_DIRECTORY ${INCLUDE_DIR})
file(MAKE_DIRECTORY ${PROJECTS_DIR})
file(MAKE_DIRECTORY ${CMAKE_DIR})
file(MAKE_DIRECTORY ${DOCS_DIR})

# 复制构建产物（存在才复制）。
if(EXISTS "${CMAKE_BINARY_DIR}/bin")
  execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/bin ${BIN_DIR})
endif()
if(EXISTS "${CMAKE_BINARY_DIR}/lib")
  execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/lib ${LIB_DIR})
endif()
if(EXISTS "${CMAKE_BINARY_DIR}/include")
  execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/include ${INCLUDE_DIR})
endif()

# 复制源码与构建脚本（按需）。
if(DEPLOY_COPY_PROJECTS AND EXISTS "${CMAKE_SOURCE_DIR}/projects")
  execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/projects ${PROJECTS_DIR})
endif()
if(DEPLOY_COPY_CMAKE AND EXISTS "${CMAKE_SOURCE_DIR}/cmake")
  execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/cmake ${CMAKE_DIR})
endif()

# 复制根 CMakeLists.txt（若存在）。
if(EXISTS "${CMAKE_SOURCE_DIR}/CMakeLists.txt")
  execute_process(
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    ${CMAKE_SOURCE_DIR}/CMakeLists.txt
    ${STAGE_DIR}/CMakeLists.txt
  )
endif()

# 复制文档与元数据（按需）。
if(DEPLOY_COPY_DOCS)
  foreach(_doc IN ITEMS README.md LICENSE SUMMARY.md DIAGRAMS.md config.md preset.json)
    if(EXISTS "${CMAKE_SOURCE_DIR}/${_doc}")
      execute_process(
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${CMAKE_SOURCE_DIR}/${_doc}
        ${DOCS_DIR}/${_doc}
      )
    endif()
  endforeach()
endif()

# 包名（可覆盖）。
if(NOT DEFINED PACKAGE_NAME)
  if(DEFINED PROJECT_NAME AND NOT PROJECT_NAME STREQUAL "")
    set(PACKAGE_NAME "${PROJECT_NAME}_${GIT_HASH}")
  else()
    set(PACKAGE_NAME "project_${GIT_HASH}")
  endif()
endif()
set(PACKAGE_NAME ${PACKAGE_NAME} CACHE STRING "Package name")

# 根据平台创建归档包。
if(WIN32)
  execute_process(
    COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.zip" -C "${CMAKE_BINARY_DIR}" "deploy_package_${GIT_HASH}"
  )
  message(STATUS "Windows package created: ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.zip")
else()
  execute_process(
    COMMAND tar -czvf ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz -C ${CMAKE_BINARY_DIR} deploy_package_${GIT_HASH}
  )
  message(STATUS "Linux/Mac package created: ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz")
endif()
