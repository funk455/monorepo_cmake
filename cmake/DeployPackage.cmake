# cmake/DeployPackage.cmake
# 从构建产物生成可部署包。

execute_process(
    COMMAND git rev-parse --short HEAD
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    OUTPUT_VARIABLE GIT_HASH
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

# 在构建目录下设置默认的打包暂存结构。
set(DEFAULT_BIN_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/bin")
set(DEFAULT_LIB_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/lib")
set(DEFAULT_INCLUDE_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/include")
set(DEFAULT_SOURCE_DIR "${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/source")

# 允许通过缓存变量覆盖输出目录。
set(BIN_DIR ${DEFAULT_BIN_DIR} CACHE PATH "Directory for binary files")
set(LIB_DIR ${DEFAULT_LIB_DIR} CACHE PATH "Directory for library files")
set(INCLUDE_DIR ${DEFAULT_INCLUDE_DIR} CACHE PATH "Directory for include files")
set(SOURCE_DIR ${DEFAULT_SOURCE_DIR} CACHE PATH "Directory for source files")

# 确保暂存目录存在。
file(MAKE_DIRECTORY ${BIN_DIR})
file(MAKE_DIRECTORY ${LIB_DIR})
file(MAKE_DIRECTORY ${INCLUDE_DIR})
file(MAKE_DIRECTORY ${SOURCE_DIR})

# 将构建产物与源码复制到暂存目录。
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/bin ${BIN_DIR})
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/lib ${LIB_DIR})
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_BINARY_DIR}/include ${INCLUDE_DIR})
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_SOURCE_DIR}/src ${SOURCE_DIR})

# 复制项目元数据到包根目录。
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/README.md ${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/README.md)
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CMAKE_SOURCE_DIR}/LICENSE ${CMAKE_BINARY_DIR}/deploy_package_${GIT_HASH}/LICENSE)

# 包名包含当前 git 短哈希。
set(PACKAGE_NAME "project_${GIT_HASH}")

# 根据平台创建归档包。
if(WIN32)
    # Windows：zip 包
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E tar "cfv" "${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.zip" -C "${CMAKE_BINARY_DIR}" "deploy_package_${GIT_HASH}"
    )
    message(STATUS "Windows package created: ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.zip")
else()
    # Linux/Mac：tar.gz 包
    execute_process(
        COMMAND tar -czvf ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz -C ${CMAKE_BINARY_DIR} deploy_package_${GIT_HASH}
    )
    message(STATUS "Linux/Mac package created: ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz")
endif()

# 如需上传到远端（如 S3/FTP），可在此处添加命令。
# execute_process(COMMAND aws s3 cp ${CMAKE_BINARY_DIR}/${PACKAGE_NAME}.tar.gz s3://your-bucket/path/)
