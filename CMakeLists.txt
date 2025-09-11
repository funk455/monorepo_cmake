cmake_minimum_required(VERSION 3.20)
project(Workspace LANGUAGES CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(UnifiedOutputDirs)

# Enable tests at the root so CTest can discover tests in subprojects
include(CTest)
enable_testing()

include(AddWorkspaces)
add_workspace_projects(
  ROOT "${CMAKE_SOURCE_DIR}/projects"
  MODE LEAF
)
