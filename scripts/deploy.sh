#!/bin/bash
# 服务器部署脚本

set -e

echo "🚀 开始部署 AI Tech Blog..."

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 构建并启动容器
echo "🔨 构建 Docker 镜像..."
docker-compose build

echo "🚀 启动容器..."
docker-compose up -d

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker image prune -f

# 健康检查
echo "🏥 健康检查..."
sleep 5
if curl -f http://localhost:8001 > /dev/null 2>&1; then
    echo "✅ 部署成功！"
    echo "🌐 访问地址: http://101.42.11.124:8001"
else
    echo "❌ 部署失败，请检查日志"
    docker-compose logs
    exit 1
fi
