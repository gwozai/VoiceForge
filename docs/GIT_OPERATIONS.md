# Git 操作指南

VoiceForge项目的Git版本控制和GitHub推送操作指南。

## 📋 基本信息

- **项目名称**: VoiceForge
- **GitHub仓库**: https://github.com/gwozai/VoiceForge
- **主分支**: main
- **SSH密钥**: 已配置 (~/.ssh/id_ed25519)

## 🚀 日常开发流程

### 1. 代码修改后的提交流程

```bash
# 1. 查看修改状态
git status

# 2. 查看具体修改内容
git diff

# 3. 添加修改到暂存区
git add .                    # 添加所有修改
# 或
git add 文件名               # 添加特定文件

# 4. 提交修改
git commit -m "描述修改内容"

# 5. 推送到GitHub
git push origin main
```

### 2. 完整的功能开发流程

```bash
# 开发新功能
# ... 编写代码 ...

# 测试功能
make test                    # 运行测试
python main.py               # 本地测试
make dev                    # Docker测试

# 版本管理
make bump-patch             # 增加补丁版本 (v1.0.0 -> v1.0.1)
make bump-minor             # 增加次版本 (v1.0.0 -> v1.1.0)  
make bump-major             # 增加主版本 (v1.0.0 -> v2.0.0)

# 提交和推送
git add .
git commit -m "feat: 新功能描述"
git push origin main

# 推送标签
git push origin --tags      # 推送所有标签
```

## 📝 提交消息规范

使用约定式提交格式：

```bash
# 功能添加
git commit -m "feat: 添加新的语音合成功能"

# 问题修复
git commit -m "fix: 修复音频播放问题"

# 文档更新
git commit -m "docs: 更新API文档"

# 样式修改
git commit -m "style: 优化界面布局"

# 重构代码
git commit -m "refactor: 重构音频处理模块"

# 性能优化
git commit -m "perf: 优化音频生成速度"

# 测试相关
git commit -m "test: 添加单元测试"

# 构建配置
git commit -m "build: 更新Docker配置"

# 配置修改
git commit -m "chore: 更新环境变量配置"
```

## 🏷️ 版本标签管理

### 查看版本

```bash
# 查看当前版本
make version
# 或
cat .version

# 查看所有标签
git tag -l

# 查看标签详情
git show v2.0.0
```

### 创建和推送标签

```bash
# 自动版本管理（推荐）
make bump-patch             # 自动增加版本并更新CHANGELOG
git push origin main
git push origin --tags

# 手动创建标签
git tag -a v2.1.0 -m "版本v2.1.0发布说明"
git push origin v2.1.0

# 删除标签（如果需要）
git tag -d v2.1.0           # 删除本地标签
git push origin :refs/tags/v2.1.0  # 删除远程标签
```

## 🔄 同步和更新

### 拉取最新代码

```bash
# 拉取最新代码
git pull origin main

# 查看远程分支状态
git remote -v
git branch -a

# 强制同步（谨慎使用）
git fetch origin
git reset --hard origin/main
```

### 解决冲突

```bash
# 如果推送时有冲突
git pull origin main        # 先拉取最新代码
# 解决冲突文件
git add .
git commit -m "resolve: 解决合并冲突"
git push origin main
```

## 🐳 Docker发布流程

### 本地测试发布

```bash
# 1. 本地开发测试
python main.py

# 2. Docker本地测试
make build
make dev
# 测试功能...
make dev-stop

# 3. 版本管理
make bump-minor
# 编辑 docs/CHANGELOG.md 添加更新说明

# 4. 提交代码
git add .
git commit -m "feat: 新版本功能完成"
git push origin main
git push origin --tags

# 5. 发布到Docker Hub
make quick-deploy
```

### 完整发布流程

```bash
# 使用完整部署脚本
make deploy VERSION=v2.1.0

# 或使用脚本
./scripts/deploy.sh v2.1.0
```

## 🔧 常用Git命令

### 查看状态和历史

```bash
# 查看状态
git status
git log --oneline -10       # 查看最近10次提交
git log --graph --oneline   # 图形化显示提交历史

# 查看修改
git diff                    # 查看工作区修改
git diff --cached           # 查看暂存区修改
git diff HEAD~1             # 与上一次提交比较
```

### 撤销操作

```bash
# 撤销工作区修改
git checkout -- 文件名

# 撤销暂存区修改
git reset HEAD 文件名

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 修改最后一次提交消息
git commit --amend -m "新的提交消息"
```

### 分支操作

```bash
# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

## 🔑 SSH密钥管理

### 检查SSH连接

```bash
# 测试GitHub连接
ssh -T git@github.com

# 查看SSH密钥
ls -la ~/.ssh/
cat ~/.ssh/id_ed25519.pub
```

### 重新配置SSH（如果需要）

```bash
# 生成新密钥
ssh-keygen -t ed25519 -C "gwozai@github.com" -f ~/.ssh/id_ed25519 -N ""

# 添加到SSH代理
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥到剪贴板
pbcopy < ~/.ssh/id_ed25519.pub
# 然后在GitHub设置中添加SSH密钥
```

## 🚨 故障排除

### 推送失败

```bash
# 如果推送失败，检查：
git remote -v              # 确认远程仓库地址
ssh -T git@github.com      # 测试SSH连接
git status                 # 检查本地状态

# 强制推送（谨慎使用）
git push origin main --force
```

### 网络问题

```bash
# 如果网络有问题，可以配置代理
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 权限问题

```bash
# 如果出现权限问题
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 重新添加SSH密钥
ssh-add ~/.ssh/id_ed25519
```

## 📋 快速参考

### 常用命令组合

```bash
# 快速提交推送
git add . && git commit -m "update" && git push origin main

# 查看状态和日志
git status && git log --oneline -5

# 完整发布流程
make bump-patch && git push origin main && git push origin --tags && make quick-deploy
```

### Make命令快捷方式

```bash
# 开发相关
make help                   # 查看所有命令
make version               # 查看版本
make build                 # 构建Docker镜像
make dev                   # 启动开发环境
make test                  # 运行测试

# 版本管理
make bump-patch            # 补丁版本
make bump-minor            # 次版本
make bump-major            # 主版本

# 部署相关
make deploy                # 完整部署
make quick-deploy          # 快速部署
make clean                 # 清理镜像
```

## 🎯 最佳实践

1. **提交频率**: 小功能完成后及时提交
2. **提交消息**: 使用清晰的描述性消息
3. **版本管理**: 使用语义化版本号
4. **测试**: 推送前先本地测试
5. **文档**: 重要更改及时更新文档
6. **备份**: 定期推送到远程仓库

## 🔗 相关文档

- [本地开发指南](LOCAL_DEVELOPMENT.md)
- [Docker测试指南](DOCKER_LOCAL_TEST.md)
- [Docker Hub发布指南](DOCKERHUB_DEPLOY.md)
- [部署脚本指南](DEPLOY_SCRIPTS.md)

---

**VoiceForge Git操作指南** - 让版本控制变得简单高效！ 🎙️✨
