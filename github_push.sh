#!/bin/bash
# ============================================================
#  Kids Gateway — 一键推送到 GitHub
#  使用前：先在下方【二选一】配置好你的 GitHub 凭证
# ============================================================
set -e
cd "$(dirname "$0")/kids-gateway-final"

REPO="kids-gateway"          # 你的 GitHub 仓库名（可改）
USERNAME="${GITHUB_USERNAME:-你的用户名}"   # ← 改成你的 GitHub 用户名

# -------- 方式 A：HTTPS + Personal Access Token（推荐新手）--------
# 1. 在 https://github.com/settings/tokens 生成 token（勾选 repo 权限）
# 2. 取消下面两行注释，填入你的 token
# export GITHUB_USERNAME="你的用户名"
# export GITHUB_TOKEN="ghp_xxx你的tokenxxx"

# -------- 方式 B：SSH（推荐常用 Git 的人）--------
# 1. 在 https://github.com/settings/keys 添加你的 SSH 公钥
# 2. 直接用 SSH 地址：
# REMOTE="git@github.com:${USERNAME}/${REPO}.git"

REMOTE="https://github.com/${USERNAME}/${REPO}.git"

echo "▶ 初始化 git 仓库..."
git init -q 2>/dev/null || true
git branch -M main

# 若未全局配置 git 身份，用占位身份（推送前可 git commit --amend --reset-author）
git config user.name  "${GIT_USER_NAME:-kids-gateway}"
git config user.email "${GIT_USER_EMAIL:-dev@local}"

echo "▶ 添加文件并提交..."
git add .
git commit -q -m "feat: 儿童上网认证系统 v1.0" 2>/dev/null || echo "（无新提交）"

echo "▶ 添加远程仓库：$REMOTE"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

echo ""
echo "=============================================="
echo "  准备推送。请选择你的认证方式并完成推送："
echo ""
echo "  【HTTPS + Token】"
echo "    git push -u origin main"
echo "    # 用户名：你的用户名"
echo "    # 密码：粘贴你的 Personal Access Token"
echo ""
echo "  【SSH】"
echo "    git remote set-url origin git@github.com:${USERNAME}/${REPO}.git"
echo "    git push -u origin main"
echo "=============================================="
echo ""
echo "💡 首次推送若提示仓库不存在，请先在 GitHub 网页新建空仓库（不要勾选 README）。"
