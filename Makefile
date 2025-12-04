# VoiceForge Makefile
# 专业语音合成工坊

.PHONY: help run install clean test docker-build docker-run docker-stop docker-push update-voices

# 默认目标 - 显示帮助
help:
	@echo "VoiceForge 2.0 - 专业语音合成工坊"
	@echo ""
	@echo "开发命令:"
	@echo "  run           - 运行应用 (开发模式)"
	@echo "  install       - 安装依赖"
	@echo "  update-voices - 更新Edge-TTS语音列表"
	@echo "  clean         - 清理缓存"
	@echo "  test          - 运行测试"
	@echo ""
	@echo "Docker命令:"
	@echo "  docker-build  - 构建Docker镜像"
	@echo "  docker-run    - 运行Docker容器"
	@echo "  docker-stop   - 停止Docker容器"
	@echo "  docker-push   - 推送镜像到Docker Hub"
	@echo "  docker-dev    - 开发模式运行Docker"
	@echo ""
	@echo "部署命令:"
	@echo "  deploy        - 完整部署流程"
	@echo "  quick-deploy  - 快速部署"

# 构建和部署
build:
	@cd scripts && make build

deploy:
	@cd scripts && make deploy $(ARGS)

quick-deploy:
	@cd scripts && make quick-deploy $(ARGS)

test:
	@cd scripts && make test

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	@cd scripts && make clean

# 版本管理
version:
	@cd scripts && make version

bump-patch:
	@cd scripts && make bump-patch

bump-minor:
	@cd scripts && make bump-minor

bump-major:
	@cd scripts && make bump-major

# 开发环境
dev:
	@cd scripts && make dev

dev-stop:
	@cd scripts && make dev-stop

dev-logs:
	@cd scripts && make dev-logs

# 发布流程
release-patch:
	@cd scripts && make release-patch

release-minor:
	@cd scripts && make release-minor

release-major:
	@cd scripts && make release-major

# 本地开发
install:
	@cd scripts && make install

run:
	python main.py

update-voices:
	@echo "🎤 正在更新Edge-TTS语音列表..."
	python scripts/update_voices.py
	@echo "✅ 语音列表更新完成！"

# Docker命令
docker-build:
	@echo "🐳 构建Docker镜像..."
	docker build -t voiceforge:latest .
	@echo "✅ 镜像构建完成！"

docker-run:
	@echo "🚀 启动Docker容器..."
	docker-compose up -d
	@echo "✅ 容器已启动: http://localhost:8080"

docker-stop:
	@echo "🛑 停止Docker容器..."
	docker-compose down
	@echo "✅ 容器已停止"

docker-dev:
	@echo "🔧 开发模式启动Docker..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

docker-logs:
	docker-compose logs -f

docker-push:
	@echo "📤 推送镜像到Docker Hub..."
	./scripts/deploy.sh
