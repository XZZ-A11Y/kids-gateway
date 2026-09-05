#!/bin/sh
# 初始化 git 仓库并提交，然后按提示推送到 GitHub
set -e
cd "$(dirname "$0")"

git init -q
git branch -M main

# ⚠️ 首次使用请先取消下面两行注释并改成你自己的信息
# git config user.name  "你的GitHub用户名"
# git config user.email "你的GitHub邮箱"

git add .
git commit -q -m "feat: 儿童上网认证系统 v1.0

- Flask 后端：登录/续期/注销/会话校验
- 参数校验：空值、非数字、负数/零
- 家长管理后台（隐藏入口：连续点击版本号 5 次）
- 在线会话/设备信息/操作日志审计/强制踢人
- 每日上网时长配额
- 冒烟测试 9/9 通过
- Dockerfile + README 部署文档"

echo "✅ 本地仓库已初始化并提交。"
echo ""
echo "👉 在 GitHub 上新建一个仓库（不要勾选 README），然后执行："
echo "  git remote add origin https://github.com/<你的用户名>/kids-gateway.git"
echo "  git push -u origin main"
