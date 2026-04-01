#!/usr/bin/env bash
set -euo pipefail

CMAKE_BIN="${CMAKE_BIN:-cmake}"
BUILD_DIR="${BUILD_DIR:-build-perf}"
BUILD_TYPE="${BUILD_TYPE:-Release}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_PATH="${ROOT_DIR}/${BUILD_DIR}"

echo "== Configure =="
t0=$(date +%s)
"${CMAKE_BIN}" -S "${ROOT_DIR}" -B "${BUILD_PATH}" -DCMAKE_BUILD_TYPE="${BUILD_TYPE}"
t1=$(date +%s)
echo "--------------Configure time: $((t1 - t0))s----------------"

echo "== Build (clean) =="
t2=$(date +%s)
"${CMAKE_BIN}" --build "${BUILD_PATH}"
t3=$(date +%s)
echo "---------------Build time (clean $((t3 - t2))s)------------------:"

# 触发增量构建：在任意 .cpp 文件末尾追加一行注释
CPP_FILE="$(find "${ROOT_DIR}/projects" -name "*.cpp" | head -n 1 || true)"
if [[ -n "${CPP_FILE}" ]]; then
  echo "// perf touch" >> "${CPP_FILE}"
  echo "== Build (incremental) =="
  t4=$(date +%s)
  "${CMAKE_BIN}" --build "${BUILD_PATH}"
  t5=$(date +%s)
  echo "---------------Build time (incremental): $((t5 - t4))s----------------"
else
  echo "No .cpp file found to trigger incremental build."
fi
