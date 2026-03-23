# CMake 工作区示例（monorepo-cmake-sample）

这是一个基于 CMake 的多项目工作区示例，统一了构建输出、构建类型、目标创建、安装导出与测试注册，并提供命令行引导生成新项目骨架。

## 目录结构
- `cmake/`：自定义 CMake 模块与引导式模板生成器（`cli.py`）。
- `projects/`：工作区内子项目（示例包含 `netlib`、`projectlib`、`utils`）。
- `CMakeLists.txt`：工作区入口，统一加载模块并聚合子项目。
- `config.md`：`cmake/` 中可配置变量说明。
- `SUMMARY.md` / `DIAGRAMS.md`：项目总结与图示说明。

## 快速开始
```bash
cmake -S . -B build
cmake --build build
```

运行测试（若启用）：
```bash
ctest --test-dir build
```

## 生成新项目（引导式）
交互式创建：
```bash
python cmake/cli.py
```

使用预设直接生成：
```bash
python cmake/cli.py --preset preset.json
```

> 首次引导会保存 `preset.json`，方便复用配置。

## 打包（可选）
根据当前结构打包构建产物、源码与文档：
```bash
cmake -P cmake/DeployPackage.cmake
```

可通过缓存变量控制是否复制源码/文档：
- `DEPLOY_COPY_PROJECTS`（默认 ON）
- `DEPLOY_COPY_DOCS`（默认 ON）

## 构建/测试报告
生成构建报告（`build/reports/build-report.json`）：
```bash
cmake --build build
cmake --build build --target report-build
```
构建报告包含时间戳、`tests_included`、编译器信息、系统信息与 `elapsed_seconds` 等字段。

生成测试报告（`build/reports/tests.log`，若 CMake >= 3.21 还会生成 `tests.junit.xml`）：
```bash
cmake --build build
cmake --build build --target report-test
```

一次生成全部报告：
```bash
cmake --build build
cmake --build build --target report-all
```

## 目标创建与导出
库目标使用 `AddTarget.cmake` 创建，导出与安装由 `SetupPackage.cmake` 完成。  
目前导出配置在 **库目标所在目录** 管理，命名空间在 **上级项目目录** 统一设置：
```cmake
# projects/<proj>/CMakeLists.txt
set(PROJECT_NAMESPACE "your_ns")

# projects/<proj>/<lib>/CMakeLists.txt
set(PKG_TARGET_NAME "your_lib")
set(DIR_TARGET_NAME ${PKG_TARGET_NAME})
include(${CMAKE_SOURCE_DIR}/cmake/AddTarget.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/SetupPackage.cmake)
setup_package(
  PACKAGE_NAME      "${PKG_TARGET_NAME}"
  PACKAGE_NAMESPACE "${PROJECT_NAMESPACE}"
  EXPORT_NAME       "${PKG_TARGET_NAME}Targets"
  APPEND_GIT_HASH   ON
)
```

## 说明
- 为减少不必要的重新配置，目标源文件必须显式列出（不使用 glob）。
- 工作区入口使用 `add_workspace_projects(DIRS ...)` 聚合子项目。
