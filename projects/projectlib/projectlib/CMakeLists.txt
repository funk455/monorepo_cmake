set(PKG_TARGET_NAME "projectlib")
set(DIR_TARGET_NAME ${PKG_TARGET_NAME})
set(DIR_TARGET_TYPE LIBRARY)
set(DIR_ALIAS_PREFIX proj)
set(DIR_PUBLIC_DEPS net::network;utils::utils)
set(DIR_ENABLE_INSTALL ON)
set(PROJECT_EXPORT_NAME "${PKG_TARGET_NAME}Targets")
set(DIR_SOURCES projectlib.cpp)
set(DIR_HEADERS projectlib.h)
include(${CMAKE_SOURCE_DIR}/cmake/AddTarget.cmake)

include(${CMAKE_SOURCE_DIR}/cmake/SetupPackage.cmake)
setup_package(
  PACKAGE_NAME      "${PKG_TARGET_NAME}"
  PACKAGE_NAMESPACE "${PROJECT_NAMESPACE}"
  EXPORT_NAME       "${PROJECT_EXPORT_NAME}"
  APPEND_GIT_HASH   ON
)
