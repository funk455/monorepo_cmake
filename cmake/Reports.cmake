# Reports.cmake
# Adds convenience targets for build and test reports (written to <build>/reports/).
#   report-build : build-report.json
#   report-test  : run ctest -> tests.log + tests.junit.xml, then build-report.json

set(REPORTS_DIR "${CMAKE_BINARY_DIR}/reports")

# 多配置生成器的配置列表以逗号连接，避免 ";" 在 COMMAND 中被拆成多个参数。
list(JOIN CMAKE_CONFIGURATION_TYPES "," _report_configs)

set(_report_args
  -DREPORTS_DIR=${REPORTS_DIR}
  -DREPORT_BUILD_DIR=${CMAKE_BINARY_DIR}
  -DREPORT_SOURCE_DIR=${CMAKE_SOURCE_DIR}
  -DREPORT_PROJECT_NAME=${PROJECT_NAME}
  -DREPORT_GENERATOR=${CMAKE_GENERATOR}
  -DREPORT_BUILD_TYPE=${CMAKE_BUILD_TYPE}
  -DREPORT_CONFIGS=${_report_configs}
  -DREPORT_COMPILER_CXX=${CMAKE_CXX_COMPILER}
  -DREPORT_COMPILER_CXX_ID=${CMAKE_CXX_COMPILER_ID}
  -DREPORT_COMPILER_CXX_VERSION=${CMAKE_CXX_COMPILER_VERSION}
  -DREPORT_SYSTEM_NAME=${CMAKE_SYSTEM_NAME}
  -DREPORT_SYSTEM_VERSION=${CMAKE_SYSTEM_VERSION}
  -DREPORT_SYSTEM_PROCESSOR=${CMAKE_SYSTEM_PROCESSOR}
)

add_custom_target(report-build
  COMMAND ${CMAKE_COMMAND} -E make_directory ${REPORTS_DIR}
  COMMAND ${CMAKE_COMMAND} ${_report_args} -DREPORT_TESTS_INCLUDED=false
          -P ${CMAKE_SOURCE_DIR}/cmake/BuildReport.cmake
  COMMENT "Generate build report"
  VERBATIM
)

set(_ctest_cmd ${CMAKE_CTEST_COMMAND} --output-on-failure --output-log ${REPORTS_DIR}/tests.log)
if(CMAKE_CONFIGURATION_TYPES)
  # 多配置生成器：用生成器表达式在构建时传入当前配置
  list(APPEND _ctest_cmd -C $<CONFIG>)
endif()
if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.21")
  list(APPEND _ctest_cmd --output-junit ${REPORTS_DIR}/tests.junit.xml)
endif()

add_custom_target(report-test
  COMMAND ${CMAKE_COMMAND} -E make_directory ${REPORTS_DIR}
  COMMAND ${_ctest_cmd}
  COMMAND ${CMAKE_COMMAND} ${_report_args} -DREPORT_TESTS_INCLUDED=true
          -P ${CMAKE_SOURCE_DIR}/cmake/BuildReport.cmake
  WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
  COMMENT "Run tests and generate test + build reports"
  VERBATIM
)

unset(_report_args)
unset(_report_configs)
unset(_ctest_cmd)
