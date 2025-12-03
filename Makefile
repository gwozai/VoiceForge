# TTS Website 根目录 Makefile
# 简化命令，委托给scripts目录中的Makefile

.PHONY: help build deploy quick-deploy test clean version dev

# 默认目标 - 显示帮助
help:
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
