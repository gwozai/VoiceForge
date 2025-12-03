#!/bin/bash

# TTS Website 快速部署脚本
# 简化版本，用于日常快速部署

set -e

# 配置
DOCKER_REPO="gwozai/voiceforge"
VERSION=${1:-"v$(date +%Y%m%d-%H%M%S)"}

echo "🚀 开始快速部署..."
echo "📦 版本: $VERSION"

# 设置代理（如果需要）
if [ "${USE_PROXY:-true}" = "true" ]; then
    echo "🌐 设置代理..."
    export https_proxy="http://127.0.0.1:7897"
    export http_proxy="http://127.0.0.1:7897"
    export all_proxy="socks5://127.0.0.1:7897"
fi

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 构建镜像
echo "🔨 构建镜像..."
docker build -f docker/Dockerfile -t "${DOCKER_REPO}:latest" -t "${DOCKER_REPO}:${VERSION}" .

# 推送镜像
echo "📤 推送镜像..."
docker push "${DOCKER_REPO}:latest"
docker push "${DOCKER_REPO}:${VERSION}"

echo "✅ 部署完成!"
echo "🌐 Docker Hub: https://hub.docker.com/r/${DOCKER_REPO}"
echo "📋 使用命令: docker pull ${DOCKER_REPO}:${VERSION}"
