#!/bin/bash
set -euo pipefail
echo "=== 启动 Echo 插件本地测试 ==="
# 测试脚本已提供 AstrBot mock，不需要安装宿主或第三方 asyncio 包。
cd "$(dirname "$0")"
"${PYTHON_BIN:-python3}" test_echo.py
