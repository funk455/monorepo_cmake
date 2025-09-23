# cmake/DeployPackage.cmake

execute_process(
    COMMAND git rev-parse --short HEAD
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    OUTPUT_VARIABLE GIT_HASH
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

set(DEFAULT_BIN_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/bin")
set(DEFAULT_LIB_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/lib")
set(DEFAULT_INCLUDE_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/include")
set(DEFAULT_SOURCE_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/source")

set(BIN_DIR ${DEFAULT_BIN_DIR} CACHE PATH "Directory for binary files")
set(LIB_DIR ${DEFAULT_LIB_DIR} CACHE PATH "Directory for library files")
set(INCLUDE_DIR ${DEFAULT_INCLUDE_DIR} CACHE PATH "Directory for include files")
set(SOURCE_DIR ${DEFAULT_SOURCE_DIR} CACHE PATH "Directory for source files")

file(MAKE_DIRECTORY ${BIN_DIR})
file(MAKE_DIRECTORY ${LIB_DIR})
file(MAKE_DIRECTORY ${INCLUDE_DIR})
file(MAKE_DIRECTORY ${SOURCE_DIR})

execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/bin ${BIN_DIR})
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/lib ${LIB_DIR})
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/include ${INCLUDE_DIR})
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/src ${SOURCE_DIR})

execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/README.md ${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/README.md)
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/LICENSE ${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/LICENSE)

set(PACKAGE_NAME "project_${GIT_HASH}")

if(WIN32)
    # Windows：ZIP 
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.zip" -C "${CMAKE_BINARY_DIR}" "deploy_package_${GIT_HASH}"
    )
    message(STATUS "Windows package created: ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.zip")
else()
    # Linux/Mac：tar.gz
    execute_process(
        COMMAND tar -czvf ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz -C ${CMAKE_BINARY_DIR} deploy_package_${GIT_HASH}
    )
    message(STATUS "Linux/Mac package created: ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz")
endif()

# enable to upload to remote system like AWS S3、FTP....
# execute_process(COMMAND aws s3 cp ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz s3://your-bucket/path/)
