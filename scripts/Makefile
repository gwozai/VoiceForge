# TTS Website Makefile
# 简化常用命令

.PHONY: help build deploy quick-deploy test clean version

# 默认目标
help:
	@echo "TTS Website 部署命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make build         - 仅构建Docker镜像"
	@echo "  make deploy        - 完整部署（构建+推送）"
	@echo "  make quick-deploy  - 快速部署"
	@echo "  make test          - 构建并测试镜像"
	@echo "  make clean         - 清理Docker镜像"
	@echo "  make version       - 显示当前版本"
	@echo "  make bump-patch    - 增加补丁版本号"
	@echo "  make bump-minor    - 增加次版本号"
	@echo "  make bump-major    - 增加主版本号"
	@echo ""
	@echo "示例:"
	@echo "  make deploy VERSION=v2.1.0"
	@echo "  make quick-deploy"

# 构建镜像
build:
	@echo "🔨 构建Docker镜像..."
	@chmod +x deploy.sh
	@./deploy.sh --build-only $(VERSION)

# 完整部署
deploy:
	@echo "🚀 开始完整部署..."
	@chmod +x deploy.sh
	@./deploy.sh $(VERSION)

# 快速部署
quick-deploy:
	@echo "⚡ 快速部署..."
	@chmod +x quick-deploy.sh
	@./quick-deploy.sh $(VERSION)

# 构建并测试
test:
	@echo "🧪 构建并测试镜像..."
	@chmod +x deploy.sh
	@./deploy.sh --test $(VERSION)

# 清理镜像
clean:
	@echo "🧹 清理Docker镜像..."
	@docker image prune -f
	@docker images gwozai/tts-website --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"

# 版本管理
version:
	@chmod +x version.sh
	@./version.sh current

bump-patch:
	@chmod +x version.sh
	@./version.sh bump patch

bump-minor:
	@chmod +x version.sh
	@./version.sh bump minor

bump-major:
	@chmod +x version.sh
	@./version.sh bump major

# 本地开发
dev:
	@echo "🔧 启动本地开发环境..."
	@cd ../docker && docker-compose up -d
	@echo "✅ 开发环境已启动: http://localhost:8080"

dev-stop:
	@echo "⏹️  停止开发环境..."
	@cd ../docker && docker-compose down

dev-logs:
	@echo "📋 查看开发环境日志..."
	@cd ../docker && docker-compose logs -f

# 发布流程（版本管理+部署）
release-patch: bump-patch deploy
release-minor: bump-minor deploy  
release-major: bump-major deploy

# 安装依赖
install:
	@echo "📦 安装Python依赖..."
	@pip install -r ../requirements.txt

# 运行本地应用
run:
	@echo "🏃 启动本地应用..."
	@cd .. && python app.py
