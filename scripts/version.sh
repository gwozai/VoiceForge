#!/bin/bash

# VoiceForge 版本管理脚本
# 用于管理项目版本和自动更新CHANGELOG

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CHANGELOG_FILE="$PROJECT_ROOT/docs/CHANGELOG.md"
VERSION_FILE="$PROJECT_ROOT/.version"

# 函数：打印消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 函数：获取当前版本
get_current_version() {
    if [ -f "$VERSION_FILE" ]; then
        cat "$VERSION_FILE"
    else
        echo "v1.0.0"
    fi
}

# 函数：增加版本号
increment_version() {
    local version=$1
    local type=$2
    
    # 移除v前缀
    version=${version#v}
    
    # 分解版本号
    IFS='.' read -r major minor patch <<< "$version"
    
    case $type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "错误：版本类型必须是 major、minor 或 patch"
            exit 1
            ;;
    esac
    
    echo "v${major}.${minor}.${patch}"
}

# 函数：更新CHANGELOG
update_changelog() {
    local version=$1
    local date=$(date +%Y-%m-%d)
    
    # 创建临时文件
    local temp_file=$(mktemp)
    
    # 写入新版本信息
    cat > "$temp_file" << EOF
# 更新日志

## $version ($date)

### 🎉 新特性
- 

### 🔧 改进
- 

### 🐛 修复
- 

### 📁 文件变更
- 

EOF
    
    # 如果CHANGELOG存在，追加旧内容（跳过第一行标题）
    if [ -f "$CHANGELOG_FILE" ]; then
        tail -n +3 "$CHANGELOG_FILE" >> "$temp_file"
    fi
    
    # 替换原文件
    mv "$temp_file" "$CHANGELOG_FILE"
    
    print_success "CHANGELOG已更新，请编辑 $CHANGELOG_FILE 添加具体变更内容"
}

# 函数：创建Git标签
create_git_tag() {
    local version=$1
    
    if git rev-parse --git-dir > /dev/null 2>&1; then
        print_info "创建Git标签: $version"
        git add .
        git commit -m "chore: release $version" || true
        git tag -a "$version" -m "Release $version"
        print_success "Git标签创建完成"
        print_info "推送标签: git push origin $version"
    else
        print_warning "不是Git仓库，跳过标签创建"
    fi
}

# 函数：显示帮助
show_help() {
    echo "VoiceForge 版本管理脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  current             显示当前版本"
    echo "  bump <type>         增加版本号 (major|minor|patch)"
    echo "  set <version>       设置指定版本号"
    echo "  changelog           仅更新CHANGELOG"
    echo "  tag                 为当前版本创建Git标签"
    echo ""
    echo "示例:"
    echo "  $0 current          # 显示当前版本"
    echo "  $0 bump patch       # 增加补丁版本号"
    echo "  $0 bump minor       # 增加次版本号"
    echo "  $0 set v2.1.0       # 设置为v2.1.0"
}

# 主函数
main() {
    case "${1:-current}" in
        current)
            current_version=$(get_current_version)
            print_info "当前版本: $current_version"
            ;;
        bump)
            if [ -z "$2" ]; then
                echo "错误：请指定版本类型 (major|minor|patch)"
                show_help
                exit 1
            fi
            
            current_version=$(get_current_version)
            new_version=$(increment_version "$current_version" "$2")
            
            print_info "版本更新: $current_version → $new_version"
            
            # 保存新版本
            echo "$new_version" > "$VERSION_FILE"
            
            # 更新CHANGELOG
            update_changelog "$new_version"
            
            print_success "版本已更新为: $new_version"
            ;;
        set)
            if [ -z "$2" ]; then
                echo "错误：请指定版本号"
                exit 1
            fi
            
            new_version="$2"
            # 确保版本号以v开头
            if [[ ! "$new_version" =~ ^v ]]; then
                new_version="v$new_version"
            fi
            
            echo "$new_version" > "$VERSION_FILE"
            update_changelog "$new_version"
            
            print_success "版本已设置为: $new_version"
            ;;
        changelog)
            current_version=$(get_current_version)
            update_changelog "$current_version"
            ;;
        tag)
            current_version=$(get_current_version)
            create_git_tag "$current_version"
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "错误：未知命令 '$1'"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
