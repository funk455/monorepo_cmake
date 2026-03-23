# BuildReport.cmake
# Generates a lightweight build report in the build tree.

if(NOT DEFINED REPORTS_DIR)
  message(FATAL_ERROR "REPORTS_DIR is required")
endif()
if(NOT DEFINED REPORT_BUILD_DIR)
  message(FATAL_ERROR "REPORT_BUILD_DIR is required")
endif()
if(NOT DEFINED REPORT_SOURCE_DIR)
  message(FATAL_ERROR "REPORT_SOURCE_DIR is required")
endif()
if(NOT DEFINED REPORT_PROJECT_NAME)
  set(REPORT_PROJECT_NAME "UnknownProject")
endif()
if(NOT DEFINED REPORT_TESTS_INCLUDED)
  set(REPORT_TESTS_INCLUDED "false")
endif()

string(TIMESTAMP _ts "%Y-%m-%d %H:%M:%S")
string(TIMESTAMP _ts_epoch "%s")

set(_elapsed "unknown")
if(DEFINED REPORT_START_EPOCH AND NOT REPORT_START_EPOCH STREQUAL "")
  math(EXPR _elapsed "${_ts_epoch} - ${REPORT_START_EPOCH}")
endif()

execute_process(
  COMMAND git rev-parse --short HEAD
  WORKING_DIRECTORY "${REPORT_SOURCE_DIR}"
  OUTPUT_VARIABLE _git_hash
  OUTPUT_STRIP_TRAILING_WHITESPACE
  RESULT_VARIABLE _git_ok
)
if(NOT _git_ok EQUAL 0 OR _git_hash STREQUAL "")
  set(_git_hash "nogit")
endif()

set(_build_type "${REPORT_BUILD_TYPE}")
if(NOT _build_type AND REPORT_CONFIGS)
  set(_build_type "${REPORT_CONFIGS}")
endif()

file(WRITE "${REPORTS_DIR}/build-report.json" "{\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"project\": \"${REPORT_PROJECT_NAME}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"timestamp\": \"${_ts}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"timestamp_epoch\": ${_ts_epoch},\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"source_dir\": \"${REPORT_SOURCE_DIR}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"build_dir\": \"${REPORT_BUILD_DIR}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"generator\": \"${REPORT_GENERATOR}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"build_type_or_configs\": \"${_build_type}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"tests_included\": ${REPORT_TESTS_INCLUDED},\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"elapsed_seconds\": \"${_elapsed}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"compiler_cxx\": \"${REPORT_COMPILER_CXX}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"compiler_cxx_id\": \"${REPORT_COMPILER_CXX_ID}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"compiler_cxx_version\": \"${REPORT_COMPILER_CXX_VERSION}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"system_name\": \"${REPORT_SYSTEM_NAME}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"system_version\": \"${REPORT_SYSTEM_VERSION}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"system_processor\": \"${REPORT_SYSTEM_PROCESSOR}\",\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "  \"git_hash\": \"${_git_hash}\"\n")
file(APPEND "${REPORTS_DIR}/build-report.json" "}\n")
