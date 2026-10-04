# Packaging.cmake
# 基于 CPack 打包，替代原先手写的 DeployPackage.cmake。
#   二进制包：打包所有 install() 规则安装的内容（库、头文件、可执行文件、find_package 配置）
#     cmake --build <build> --target package
#   源码包：打包源码树（排除 .git、build*/ 等）
#     cmake --build <build> --target package_source
#
# 可在 include 前覆盖 CPACK_GENERATOR，例如 -DCPACK_GENERATOR="ZIP;TGZ"。

if(NOT CPACK_GENERATOR)
  if(WIN32)
    set(CPACK_GENERATOR ZIP)
  else()
    set(CPACK_GENERATOR TGZ)
  endif()
endif()
set(CPACK_SOURCE_GENERATOR "${CPACK_GENERATOR}")

set(_pkg_rev "nogit")
find_program(GIT_EXECUTABLE git)
if(GIT_EXECUTABLE AND EXISTS "${CMAKE_SOURCE_DIR}/.git")
  execute_process(
    COMMAND "${GIT_EXECUTABLE}" -C "${CMAKE_SOURCE_DIR}" rev-parse --short HEAD
    OUTPUT_VARIABLE _pkg_rev
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
  )
endif()

set(CPACK_PACKAGE_NAME "${PROJECT_NAME}")
set(CPACK_PACKAGE_FILE_NAME "${PROJECT_NAME}-${_pkg_rev}-${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR}")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${PROJECT_NAME}-${_pkg_rev}-src")
set(CPACK_SOURCE_IGNORE_FILES
  "/\\\\.git/"
  "/\\\\.claude/"
  "/build[^/]*/"
  "__pycache__"
)

include(CPack)
unset(_pkg_rev)
