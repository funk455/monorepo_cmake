# CMake Variables and Types (cmake/)

This document lists the user-facing/configurable variables used by the CMake helpers under `cmake/`.
Internal locals (often prefixed with `_`) and loop variables are intentionally omitted.

## AddTarget.cmake
- `DIR_TARGET_NAME`: STRING (required). Target name.
- `DIR_TARGET_TYPE`: STRING (required). `EXECUTABLE` or `LIBRARY`.
- `DIR_LIBRARY_KIND`: STRING (optional). Library type, e.g. `STATIC`, `SHARED`, `MODULE`, `OBJECT`.
- `DIR_PUBLIC_DEPS`: LIST (optional). Public link dependencies.
- `DIR_PRIVATE_DEPS`: LIST (optional). Private link dependencies.
- `DIR_INTERFACE_DEPS`: LIST (optional). Interface link dependencies.
- `DIR_ALIAS_PREFIX`: STRING (optional, default `project`). Alias namespace prefix.
- `DIR_INCLUDE_CURRENT`: BOOL (optional, default `ON`). Whether to include current source dir.
- `DIR_SOURCES`: LIST (required). Source files; must be explicit to avoid glob-based reconfigure.
- `DIR_HEADERS`: LIST (optional). Header files; use an explicit list or leave empty.
- `DIR_ENABLE_FILE_SET`: BOOL (optional, default `ON`). Enable CMake FILE_SET for headers (CMake >= 3.23).
- `DIR_POSITION_INDEPENDENT`: BOOL (optional, default `ON` for libraries). PIC setting.
- `DIR_CXX_STD`: STRING (optional, default `cxx_std_20`). Compile features.
- `DIR_REGISTER_TEST`: BOOL (optional, default `OFF`, auto-ON in `/tests`). Register with CTest.
- `DIR_TEST_NAME`: STRING (optional, default target name). CTest name.
- `DIR_ENABLE_INSTALL`: BOOL (optional, default `OFF`). Install target.
- `DIR_EXPORT_NAME`: STRING (optional, default `${PROJECT_EXPORT_NAME}` or `${PROJECT_NAME}Targets`). Export set name.
- `PROJECT_EXPORT_NAME`: STRING (optional). Used as default for `DIR_EXPORT_NAME` when defined elsewhere.

## AddWorkspaces.cmake
- `ROOT`: PATH (optional, default `${CMAKE_SOURCE_DIR}/projects`). Directory that holds the projects.
- `DIRS`: LIST (optional). Explicit directories to add (relative to `CMAKE_SOURCE_DIR` or absolute). Takes precedence over `ONLY`.
- `ONLY`: LIST (optional). Project names under `ROOT`; each is checked directly as `ROOT/<name>/CMakeLists.txt`, without scanning the tree.
- `EXCLUDE`: LIST (optional). Project names to skip.
- With neither `DIRS` nor `ONLY`, every direct subdirectory of `ROOT` that contains a `CMakeLists.txt` is added.
- Each directory is added at most once per configure (global property `AWP_ADDED_DIRS`). Missing entries produce a warning.

## BuildType.cmake
- `PROJECT_BUILD_TYPE`: STRING (optional). Preferred build type; overrides `CMAKE_BUILD_TYPE`.
- `PROJECT_DEFAULT_BUILD_TYPE`: STRING (optional, default `Release`). Fallback build type.
- `CMAKE_BUILD_TYPE`: STRING (cache). Single-config generator build type.
- `CMAKE_CONFIGURATION_TYPES`: STRING (cache). Multi-config generator types.
- `CMAKE_DEFAULT_CONFIG`: STRING (cache). Default config for multi-config generators.

## UnifiedOutputDirs.cmake
- `UNIFIED_BIN_SUBDIR`: STRING or PATH (optional, default `bin`). Output subdir for binaries.
- `UNIFIED_LIB_SUBDIR`: STRING or PATH (optional, default `lib`). Output subdir for libraries.
- `CMAKE_RUNTIME_OUTPUT_DIRECTORY`: PATH. Set by this module.
- `CMAKE_LIBRARY_OUTPUT_DIRECTORY`: PATH. Set by this module.
- `CMAKE_ARCHIVE_OUTPUT_DIRECTORY`: PATH. Set by this module.
- Multi-config generators append `<Config>/` automatically (`bin/Debug`, `bin/Release`), so configs never overwrite each other.
- `CMAKE_BUILD_RPATH`: STRING (UNIX/APPLE). Set to library output dir.
- `CMAKE_INSTALL_RPATH_USE_LINK_PATH`: BOOL (UNIX/APPLE). Set to `TRUE`.

## Packaging.cmake
- `CPACK_GENERATOR`: LIST (optional, default `ZIP` on Windows, `TGZ` elsewhere). Archive format(s) for both binary and source packages.
- Package file names: `<Project>-<git-sha>-<System>-<Processor>` (binary) and `<Project>-<git-sha>-src` (source).

## SetupPackage.cmake
- `SP_PACKAGE_NAME`: STRING (required). Package base name.
- `SP_PACKAGE_NAMESPACE`: STRING (optional, default `${PROJECT_NAMESPACE}` or `project`). CMake namespace.
- `SP_EXPORT_NAME`: STRING (optional, default `${PROJECT_EXPORT_NAME}` or `${PROJECT_NAME}Targets`). Export set name.
- `SP_APPEND_GIT_HASH`: BOOL (optional). Record the git short hash as `<Name>_GIT_HASH` in the installed config file. The package name itself is unchanged, so `find_package(<Name>)` keeps working.
- `SP_GIT_LENGTH`: INTEGER (optional, default `6`). Git short hash length.
- `PROJECT_NAMESPACE`: STRING (optional). Used as default for `SP_PACKAGE_NAMESPACE`.
- `PROJECT_EXPORT_NAME`: STRING (optional). Used as default for `SP_EXPORT_NAME`.
- `PROJECT_VERSION`: STRING. Used for package version file.
