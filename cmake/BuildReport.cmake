# BuildReport.cmake
# Generates a lightweight build report in the build tree (script mode: cmake -P).

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
if(NOT REPORT_TESTS_INCLUDED)
  set(REPORT_TESTS_INCLUDED "false")
endif()

string(TIMESTAMP _ts "%Y-%m-%d %H:%M:%S")
string(TIMESTAMP _ts_epoch "%s")

execute_process(
  COMMAND git rev-parse --short HEAD
  WORKING_DIRECTORY "${REPORT_SOURCE_DIR}"
  OUTPUT_VARIABLE _git_hash
  OUTPUT_STRIP_TRAILING_WHITESPACE
  RESULT_VARIABLE _git_ok
  ERROR_QUIET
)
if(NOT _git_ok EQUAL 0 OR _git_hash STREQUAL "")
  set(_git_hash "nogit")
endif()

set(_build_type "${REPORT_BUILD_TYPE}")
if(NOT _build_type AND REPORT_CONFIGS)
  set(_build_type "${REPORT_CONFIGS}")
endif()

# 以 JSON 字符串字面量写入：转义反斜杠和引号，Windows 路径（C:\...）才能生成合法 JSON。
# 用 function 而不是 macro：macro 参数会被文本替换，C:\work 里的 \w 会被当成 CMake 转义而报错。
set(_json "{}")
function(_report_str key value)
  string(REPLACE "\\" "\\\\" _v "${value}")
  string(REPLACE "\"" "\\\"" _v "${_v}")
  string(JSON _out SET "${_json}" "${key}" "\"${_v}\"")
  set(_json "${_out}" PARENT_SCOPE)
endfunction()

_report_str(project              "${REPORT_PROJECT_NAME}")
_report_str(timestamp            "${_ts}")
string(JSON _json SET "${_json}" timestamp_epoch "${_ts_epoch}")
_report_str(source_dir           "${REPORT_SOURCE_DIR}")
_report_str(build_dir            "${REPORT_BUILD_DIR}")
_report_str(generator            "${REPORT_GENERATOR}")
_report_str(build_type_or_configs "${_build_type}")
string(JSON _json SET "${_json}" tests_included "${REPORT_TESTS_INCLUDED}")
_report_str(compiler_cxx         "${REPORT_COMPILER_CXX}")
_report_str(compiler_cxx_id      "${REPORT_COMPILER_CXX_ID}")
_report_str(compiler_cxx_version "${REPORT_COMPILER_CXX_VERSION}")
_report_str(system_name          "${REPORT_SYSTEM_NAME}")
_report_str(system_version       "${REPORT_SYSTEM_VERSION}")
_report_str(system_processor     "${REPORT_SYSTEM_PROCESSOR}")
_report_str(git_hash             "${_git_hash}")

file(WRITE "${REPORTS_DIR}/build-report.json" "${_json}\n")
