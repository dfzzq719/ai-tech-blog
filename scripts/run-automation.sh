#!/bin/bash
# 手动运行自动化流水线

set -e

cd "$(dirname "$0")/../automation"

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 运行流水线
echo "🔄 运行自动化流水线..."
python main.py --max 3

echo "✅ 完成"
