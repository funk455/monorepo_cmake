# 图示化说明

## 1) `cmake/cli.py` 引导步骤（流程图）

```mermaid
flowchart TD
  A["运行: python cmake/cli.py"] --> B["进入交互式引导"]
  B --> C["输入项目名/版本/命名空间"]
  C --> D["选择是否生成: 库/应用/测试"]
  D --> E["为每个目标输入: 目录名/目标名/类型/源文件(必填项)"]
  E --> F["保存 preset.json (首次必写)"]
  F --> G["生成项目骨架: projects/<name>"]
  G --> H["写入各子模块 CMakeLists.txt"]
  H --> I["更新根 CMakeLists.txt 的 DIRS 列表"]
  I --> J["CMake 配置与构建"]
```

## 2) 基于 `cmake/` 的不同项目架构与所需函数（结构图）

### 2.1 仅库（Library-Only）
```mermaid
flowchart LR
  R["根 CMakeLists.txt"] --> AW["AddWorkspaces.cmake<br/>add_workspace_projects"]
  R --> UO["UnifiedOutputDirs.cmake"]
  R --> BT["BuildType.cmake"]
  R --> AU["AddUninstall.cmake"]

  P["projects/<lib>/CMakeLists.txt"] --> AM["AddModules.cmake<br/>add_modules"]
  M["<lib>/CMakeLists.txt"] --> AT["AddTarget.cmake<br/>DIR_TARGET_NAME/TYPE/SOURCES"]
  P --> SP["SetupPackage.cmake<br/>setup_package"]
```

### 2.2 仅应用（App-Only）
```mermaid
flowchart LR
  R["根 CMakeLists.txt"] --> AW["AddWorkspaces.cmake<br/>add_workspace_projects"]
  R --> UO["UnifiedOutputDirs.cmake"]
  R --> BT["BuildType.cmake"]
  R --> AU["AddUninstall.cmake"]

  P["projects/<app>/CMakeLists.txt"] --> AM["AddModules.cmake<br/>add_modules"]
  M["app/CMakeLists.txt"] --> AT["AddTarget.cmake<br/>DIR_TARGET_NAME/TYPE/SOURCES"]
```

### 2.3 库 + 应用（Library + App）
```mermaid
flowchart LR
  R["根 CMakeLists.txt"] --> AW["AddWorkspaces.cmake<br/>add_workspace_projects"]
  R --> UO["UnifiedOutputDirs.cmake"]
  R --> BT["BuildType.cmake"]
  R --> AU["AddUninstall.cmake"]

  P["projects/<proj>/CMakeLists.txt"] --> AM["AddModules.cmake<br/>add_modules"]
  L["<lib>/CMakeLists.txt"] --> AT1["AddTarget.cmake<br/>LIBRARY"]
  A["app/CMakeLists.txt"] --> AT2["AddTarget.cmake<br/>EXECUTABLE"]
  A --> DEP["DIR_PRIVATE_DEPS = <ns>::<lib>"]
  P --> SP["SetupPackage.cmake<br/>setup_package"]
```

### 2.4 库 + 应用 + 测试（Library + App + Tests）
```mermaid
flowchart LR
  R["根 CMakeLists.txt"] --> AW["AddWorkspaces.cmake<br/>add_workspace_projects"]
  R --> UO["UnifiedOutputDirs.cmake"]
  R --> BT["BuildType.cmake"]
  R --> AU["AddUninstall.cmake"]

  P["projects/<proj>/CMakeLists.txt"] --> AM["AddModules.cmake<br/>add_modules"]
  P --> CT["CTest / enable_testing"]
  L["<lib>/CMakeLists.txt"] --> AT1["AddTarget.cmake<br/>LIBRARY"]
  A["app/CMakeLists.txt"] --> AT2["AddTarget.cmake<br/>EXECUTABLE"]
  T["tests/<name>/CMakeLists.txt"] --> AT3["AddTarget.cmake<br/>EXECUTABLE"]
  AT3 --> REG["DIR_REGISTER_TEST = ON (或默认 tests/ 目录自动开启)"]
  A --> DEP["DIR_PRIVATE_DEPS = <ns>::<lib>"]
  T --> DEP2["DIR_PRIVATE_DEPS = <ns>::<lib>"]
  P --> SP["SetupPackage.cmake<br/>setup_package"]
```

### 2.5 多工作区聚合（Multi-Workspace）
```mermaid
flowchart LR
  R["根 CMakeLists.txt"] --> AW["AddWorkspaces.cmake<br/>add_workspace_projects(DIRS ...)"]
  AW --> P1["projects/a"]
  AW --> P2["projects/b"]
  AW --> P3["projects/c"]

  R --> UO["UnifiedOutputDirs.cmake"]
  R --> BT["BuildType.cmake"]
  R --> AU["AddUninstall.cmake"]

  P1 --> AM1["AddModules.cmake"]
  P2 --> AM2["AddModules.cmake"]
  P3 --> AM3["AddModules.cmake"]
```

## 说明
- 以上图示对应本仓库 `cmake/` 中的模块分工与调用关系。
- 所有目标必须显式设置 `DIR_SOURCES`（最小化重新配置与重编译）。
