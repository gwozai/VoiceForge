#!/bin/bash

# VoiceForge Docker 自动部署脚本
# 作者: gwozai
# 用途: 自动构建、标记和推送Docker镜像到Docker Hub

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
DOCKER_USERNAME="gwozai"
IMAGE_NAME="voiceforge"
DOCKER_REPO="${DOCKER_USERNAME}/${IMAGE_NAME}"

# 代理配置（如果需要）
PROXY_HOST="127.0.0.1"
PROXY_PORT="7897"
USE_PROXY=${USE_PROXY:-true}

# 函数：打印彩色消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：设置代理
setup_proxy() {
    if [ "$USE_PROXY" = true ]; then
        print_info "设置代理..."
        export https_proxy="http://${PROXY_HOST}:${PROXY_PORT}"
        export http_proxy="http://${PROXY_HOST}:${PROXY_PORT}"
        export all_proxy="socks5://${PROXY_HOST}:${PROXY_PORT}"
        print_success "代理设置完成"
    fi
}

# 函数：检查Docker是否运行
check_docker() {
    print_info "检查Docker状态..."
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker未运行，请启动Docker后重试"
        exit 1
    fi
    print_success "Docker运行正常"
}

# 函数：检查Docker Hub登录状态
check_docker_login() {
    print_info "检查Docker Hub登录状态..."
    if ! docker info 2>/dev/null | grep -q "Username: ${DOCKER_USERNAME}"; then
        print_warning "未登录Docker Hub，正在登录..."
        docker login -u "${DOCKER_USERNAME}"
        if [ $? -eq 0 ]; then
            print_success "Docker Hub登录成功"
        else
            print_error "Docker Hub登录失败"
            exit 1
        fi
    else
        print_success "已登录Docker Hub"
    fi
}

# 函数：获取版本号
get_version() {
    if [ -n "$1" ]; then
        VERSION="$1"
    else
        # 尝试从git tag获取版本
        if git describe --tags --exact-match 2>/dev/null; then
            VERSION=$(git describe --tags --exact-match)
        else
            # 使用日期时间作为版本
            VERSION="v$(date +%Y%m%d-%H%M%S)"
        fi
    fi
    print_info "使用版本号: ${VERSION}"
}

# 函数：构建Docker镜像
build_image() {
    print_info "开始构建Docker镜像..."
    
    # 切换到项目根目录
    cd "$(dirname "$0")/.."
    
    # 构建镜像，同时标记latest和版本号
    docker build \
        -f Dockerfile \
        -t "${DOCKER_REPO}:latest" \
        -t "${DOCKER_REPO}:${VERSION}" \
        .
    
    if [ $? -eq 0 ]; then
        print_success "镜像构建完成"
        print_info "镜像标签: ${DOCKER_REPO}:latest, ${DOCKER_REPO}:${VERSION}"
    else
        print_error "镜像构建失败"
        exit 1
    fi
}

# 函数：推送镜像到Docker Hub
push_image() {
    print_info "推送镜像到Docker Hub..."
    
    # 推送latest标签
    print_info "推送 latest 标签..."
    docker push "${DOCKER_REPO}:latest"
    
    # 推送版本标签
    print_info "推送 ${VERSION} 标签..."
    docker push "${DOCKER_REPO}:${VERSION}"
    
    if [ $? -eq 0 ]; then
        print_success "镜像推送完成"
        print_success "Docker Hub地址: https://hub.docker.com/r/${DOCKER_REPO}"
    else
        print_error "镜像推送失败"
        exit 1
    fi
}

# 函数：清理本地镜像（可选）
cleanup_images() {
    if [ "$CLEANUP" = true ]; then
        print_info "清理旧的Docker镜像..."
        docker image prune -f
        print_success "镜像清理完成"
    fi
}

# 函数：显示镜像信息
show_image_info() {
    print_info "镜像信息:"
    docker images "${DOCKER_REPO}" --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
}

# 函数：测试镜像
test_image() {
    if [ "$TEST_IMAGE" = true ]; then
        print_info "测试镜像..."
        
        # 停止现有容器（如果存在）
        docker stop voiceforge-test 2>/dev/null || true
        docker rm voiceforge-test 2>/dev/null || true
        
        # 运行测试容器
        docker run -d \
            --name voiceforge-test \
            -p 8081:8080 \
            "${DOCKER_REPO}:latest"
        
        # 等待容器启动
        sleep 5
        
        # 测试健康检查
        if curl -f http://localhost:8081/ >/dev/null 2>&1; then
            print_success "镜像测试通过"
        else
            print_warning "镜像测试失败，但继续部署"
        fi
        
        # 清理测试容器
        docker stop voiceforge-test
        docker rm voiceforge-test
    fi
}

# 函数：显示帮助信息
show_help() {
    echo "VoiceForge Docker 部署脚本"
    echo ""
    echo "用法: $0 [选项] [版本号]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -t, --test          构建后测试镜像"
    echo "  -c, --cleanup       推送后清理本地镜像"
    echo "  --no-proxy          不使用代理"
    echo "  --build-only        仅构建，不推送"
    echo "  --push-only         仅推送（假设镜像已存在）"
    echo ""
    echo "示例:"
    echo "  $0                  # 自动版本号部署"
    echo "  $0 v2.1            # 指定版本号部署"
    echo "  $0 -t v2.1         # 构建、测试并部署"
    echo "  $0 --build-only    # 仅构建镜像"
    echo ""
    echo "环境变量:"
    echo "  USE_PROXY=false    # 禁用代理"
    echo "  CLEANUP=true       # 启用清理"
    echo "  TEST_IMAGE=true    # 启用测试"
}

# 主函数
main() {
    print_info "=== VoiceForge Docker 部署脚本 ==="
    print_info "开始时间: $(date)"
    
    # 解析命令行参数
    BUILD_ONLY=false
    PUSH_ONLY=false
    TEST_IMAGE=false
    CLEANUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--test)
                TEST_IMAGE=true
                shift
                ;;
            -c|--cleanup)
                CLEANUP=true
                shift
                ;;
            --no-proxy)
                USE_PROXY=false
                shift
                ;;
            --build-only)
                BUILD_ONLY=true
                shift
                ;;
            --push-only)
                PUSH_ONLY=true
                shift
                ;;
            -*)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                VERSION="$1"
                shift
                ;;
        esac
    done
    
    # 获取版本号
    get_version "$VERSION"
    
    # 设置代理
    setup_proxy
    
    # 检查Docker
    check_docker
    
    if [ "$PUSH_ONLY" = false ]; then
        # 构建镜像
        build_image
        
        # 测试镜像
        test_image
    fi
    
    if [ "$BUILD_ONLY" = false ]; then
        # 检查登录状态
        check_docker_login
        
        # 推送镜像
        push_image
    fi
    
    # 清理镜像
    cleanup_images
    
    # 显示镜像信息
    show_image_info
    
    print_success "=== 部署完成 ==="
    print_info "结束时间: $(date)"
    print_info "镜像地址: ${DOCKER_REPO}:${VERSION}"
    print_info "最新地址: ${DOCKER_REPO}:latest"
}

# 执行主函数
main "$@"
