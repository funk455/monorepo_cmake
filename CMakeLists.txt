cmake_minimum_required(VERSION 3.20)
project(Workspace LANGUAGES CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(UnifiedOutputDirs)
include(AddUninstall)
include(BuildType)
include(Reports)
add_uninstall_target()
# Enable tests at the root so CTest can discover tests in subprojects
include(CTest)

include(AddWorkspaces)
add_workspace_projects(
  ROOT "${CMAKE_SOURCE_DIR}/projects"
  ONLY
    netlib
    projectlib
    utils
    project1
    perf_p001
    perf_p002
    perf_p003
    perf_p004
    perf_p005
    perf_p006
    perf_p007
    perf_p008
    perf_p009
    perf_p010
    perf_p011
    perf_p012
    perf_p013
    perf_p014
    perf_p015
    perf_p016
    perf_p017
    perf_p018
    perf_p019
    perf_p020
    perf_p021
    perf_p022
    perf_p023
    perf_p024
    perf_p025
    perf_p026
    perf_p027
    perf_p028
    perf_p029
    perf_p030
    perf_p031
    perf_p032
    perf_p033
    perf_p034
    perf_p035
    perf_p036
    perf_p037
    perf_p038
    perf_p039
    perf_p040
    perf_p041
    perf_p042
    perf_p043
    perf_p044
    perf_p045
    perf_p046
    perf_p047
    perf_p048
    perf_p049
    perf_p050
)
