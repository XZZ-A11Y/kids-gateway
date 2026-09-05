# 🛡️ Kids Gateway — 儿童上网认证系统

> 防止小孩无节制上网的家庭上网认证网关。小孩需通过认证才能上网，家长可设置时长、远程踢人、查看日志。

---

## ✨ 功能

- 🔐 **账号认证**：固定账号登录，密码错误 / 时长为空 / 负数均有校验
- ⏱️ **免认证时长**：登录时设置上网时长，倒计时归零后需重新认证
- 🔄 **一键续期 / 注销**：免认证时间内可延长 10 分钟，或立即注销
- 👨‍👩‍👧 **家长管理后台**：连续点击页面底部版本号 `v1.0.0` 5 次进入，可查看在线会话、设备、操作日志、强制踢人
- 📊 **操作日志审计**：登录 / 注销 / 续期 / 踢出全记录
- 🚫 **会话管理**：可远程注销其他设备、强制下线
- 📅 **每日时长配额**：默认每日 180 分钟，用完即断

---

## 🚀 本地启动

```bash
git clone https://github.com/你的用户名/kids-gateway.git
cd kids-gateway
pip install -r requirements.txt
python app.py
# 浏览器打开 http://localhost:5000
```

冒烟测试：

```bash
python test_smoke.py
# 通过 9/9
```

---

## 🔑 默认账号（**首次部署务必改密码**）

| 角色 | 账号 | 密码 |
|------|------|------|
| 小孩 | `小猪猪` | `ZhuZhu@2026` |
| 家长后台 | — | `Parent@2026` |

> 密码位置：`app.py` 的 `ADMIN_PASS` 与 `data/users.json`。改密码直接改这两处。

---

## 📁 项目结构

```
kids-gateway/
├── app.py              # Flask 后端（登录/续期/注销/管理员接口）
├── requirements.txt
├── test_smoke.py       # 冒烟测试（9 项断言）
├── Dockerfile          # 容器化部署
├── .gitignore
├── init_git.sh         # 一键初始化 git 仓库 + 推送提示
├── data/               # 运行时自动生成（用户/会话/设备/日志 JSON）
└── templates/
    └── index.html      # 前端单页（登录 + 倒计时 + 家长后台）
```

---

## 🐳 Docker 一键部署

```bash
docker build -t kids-gateway .
docker run -d -p 5000:5000 --restart unless-stopped kids-gateway
```

---

## 🌐 配合路由器实现「全屋强制认证」（进阶）

> 本系统是**认证门户**，默认只拦截对本机的访问。要做到「不登录不能上网」，需配合路由器做流量劫持。

### 方案一：OpenWrt / 软路由（iptables）

```bash
# 把小孩设备的 MAC/IP 的 80/443 端口重定向到认证服务器
iptables -t nat -A PREROUTING -i br-lan -m mac --mac-source AA:BB:CC:DD:EE:FF \
    -p tcp --dport 80 -j DNAT --to-destination 192.168.1.100:5000
iptables -t nat -A PREROUTING -i br-lan -m mac --mac-source AA:BB:CC:DD:EE:FF \
    -p tcp --dport 443 -j DNAT --to-destination 192.168.1.100:5000
```

### 方案二：DNS 劫持（推荐家庭场景）

在路由器 DNS 中将常用域名指向认证服务器，配合本系统的「未登录拦截」实现跳转。

### 方案三：部署到公网

1. 将本仓库推送到 GitHub
2. 一键部署到 [Railway](https://railway.app) / [Fly.io](https://fly.io) / 树莓派
3. 路由器把网关指向该公网地址

---

## ⚙️ 配置说明

| 配置项 | 位置 | 默认值 |
|--------|------|--------|
| 每日上网配额 | `data/users.json` → `daily_quota` | 180 分钟 |
| 家长管理密码 | `app.py` → `ADMIN_PASS` | `Parent@2026` |
| 服务端口 | 环境变量 `PORT` | 5000 |

---

## ⚠️ 安全提醒

1. **改密码！** 默认密码仅用于演示，首次部署务必修改
2. **HTTPS 绕过**：纯 HTTP 拦截可被 HTTPS 绕过，家庭场景建议配合路由器白名单
3. **生产环境**：已默认 `debug=False`，建议用 gunicorn + nginx 反向代理
4. **数据存储**：当前使用本地 JSON 文件，重启不丢数据；多实例部署请换成数据库

---

## 📝 License

MIT
