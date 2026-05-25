#!/bin/bash
echo "=== 启动 Echo 插件本地测试 ==="

# 检查是否安装了依赖
if ! python -c "import astrbot" 2>/dev/null; then
    echo "安装测试依赖..."
    pip install -r ../requirements.txt
fi

# 运行测试
cd "$(dirname "$0")"
python test_echo.py
