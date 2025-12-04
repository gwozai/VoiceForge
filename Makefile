# TTS Website 根目录 Makefile
# 简化命令，委托给scripts目录中的Makefile

.PHONY: help build deploy quick-deploy test clean version dev run-oop update-voices

# 默认目标 - 显示帮助
help:
	@echo "VoiceForge - 语音合成工坊"
	@echo "可用命令:"
	@echo "  install       - 安装依赖"
	@echo "  run           - 运行原版应用"
	@echo "  run-oop       - 运行面向对象版本"
	@echo "  update-voices - 更新Edge-TTS语音列表"
	@echo "  clean         - 清理缓存"
	@echo "  test          - 运行测试"
	@cd scripts && make help

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
	@cd scripts && make run

run-oop:
	python main.py

update-voices:
	@echo "🎤 正在更新Edge-TTS语音列表..."
	python scripts/update_voices.py
	@echo "✅ 语音列表更新完成！"
