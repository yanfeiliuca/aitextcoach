# AITextCoach Render → Cloudflare 迁移 SOP

> 记录本次迁移的完整操作步骤，供未来参考或复用。

**迁移日期**: 2026-07-17  
**执行者**: 阿龙 (OpenClaw Agent)  
**项目**: aitextcoach.com  
**状态**: ✅ 已上线

---

## 迁移原因

Render 免费 PostgreSQL 数据库收到通知：90 天后（2026-08-05）将被暂停。项目处于早期阶段（0 注册用户，仅 5 次点击统计），决定整体迁移到 Cloudflare 免费层，实现永久托管。

---

## 架构变更

| 组件 | 之前 | 之后 |
|------|------|------|
| 静态页面 | Render Web Service | Cloudflare Pages |
| API 后端 | Python + Uvicorn | Cloudflare Worker (TypeScript) |
| 数据库 | Render PostgreSQL | Cloudflare D1 (SQLite) |
| 预算控制 | 本地 JSON 文件 | Cloudflare KV |
| DNS | Namecheap | Cloudflare |

---

## 执行步骤

### 1. 评估项目状态

```bash
# 确认数据库内容
curl https://aitextcoach.com/api/stats
# 结果: 0 注册用户, 5 次点击, 无重要数据 → 无需数据迁移
```

### 2. 创建 Cloudflare 资源

```bash
# 登录
npx wrangler login

# D1 数据库
npx wrangler d1 create aitextcoach-db
# ID: 6326c54b-ecd0-4c93-be67-e8d2cfa0673d

# KV 命名空间
npx wrangler kv namespace create aitextcoach-kv
# ID: d7a5905888bd474e843f23554d565548

# 执行 schema 迁移
npx wrangler d1 execute aitextcoach-db --remote --file ./migrations/0001_initial.sql
```

### 3. 编写 Worker 代码

文件结构：
```
src/
├── index.ts      # 路由分发
├── db.ts         # D1 操作
└── deepseek.ts   # DeepSeek API + 预算
```

关键转换：
- Python `psycopg2` → D1 `prepare().bind().run()`
- `os.environ` → `env.VAR_NAME` (wrangler binding)
- `requests.post` → `fetch()`
- JSON 文件 → KV `get/put`

### 4. 部署 Worker

```bash
cd ~/Developer/aitextcoach-cf
npm install
npx wrangler deploy

# 设置密钥
npx wrangler secret put DS_API_KEY
npx wrangler secret put PAYPAL_CLIENT_SECRET

# Worker 域名: https://aitextcoach.xy4dan.workers.dev
```

### 5. 部署静态页面到 Pages

```bash
# 复制静态文件
mkdir public
cp ../aitextcoach/index.html public/
cp ../aitextcoach/blog public/

# 修改前端 API 指向（关键！）
# 添加: const API_BASE = 'https://api.aitextcoach.com';
# 所有 fetch('/api/xxx') → fetch(API_BASE + '/api/xxx')

# 创建并部署 Pages
npx wrangler pages project create aitextcoach --production-branch=main
npx wrangler pages deploy public --project-name=aitextcoach --branch=main

# Pages 域名: https://aitextcoach.pages.dev
```

### 6. DNS 迁移

**在 Cloudflare 添加域名**：
- dash.cloudflare.com → Add domain → aitextcoach.com → Free plan
- 获得 NS: `poppy.ns.cloudflare.com`, `yadiel.ns.cloudflare.com`

**在 Namecheap 修改 NS**：
- Domain List → Manage → Nameservers → Custom DNS
- 填入 Cloudflare 提供的两个 NS

**等待传播**：
```bash
dig +short NS aitextcoach.com
# 约 5-30 分钟后显示 Cloudflare NS
```

### 7. 域名绑定

**Pages 绑定**（aitextcoach.com）：
- Workers & Pages → aitextcoach (Pages) → Custom domains
- 添加: `aitextcoach.com`, `www.aitextcoach.com`

**Worker 绑定**（api.aitextcoach.com）：
- Workers & Pages → aitextcoach (Worker) → Custom domains
- 添加: `api.aitextcoach.com`

**⚠️ 关键教训**：Worker 必须绑定独立子域名，否则 POST 请求会被 Pages 拦截（405 错误）。

### 8. 验证

```bash
# 静态页面
curl -s https://aitextcoach.com/ | head -1
# <!DOCTYPE html> ✅

# API
curl -s https://api.aitextcoach.com/api/stats
# JSON 正常 ✅

# AI enhance
curl -s -X POST https://api.aitextcoach.com/api/enhance \
  -H "Content-Type: application/json" \
  -d '{"text":"test","style":"formal"}'
# AI 响应正常 ✅

# 前端配置
curl -s https://aitextcoach.com/ | grep API_BASE
# const API_BASE = 'https://api.aitextcoach.com'; ✅
```

---

## 遇到的问题及解决

### 问题 1: npm 依赖冲突

**现象**: `@cloudflare/workers-types` 版本与 wrangler 的 peer dependency 冲突。  
**解决**: 将 `workers-types` 从 `^4.x` 升级到 `^5.20260716.1`。

### 问题 2: Worker route 部署失败

**现象**: 在 wrangler.toml 添加 `[[routes]]` 后 `wrangler deploy` 报错。  
**解决**: 删除 routes 配置，改用 Worker 的 Custom Domain 功能绑定子域名。

### 问题 3: POST 请求返回 405

**现象**: `aitextcoach.com/api/enhance` 返回 405。  
**原因**: 请求被 Pages（静态文件服务）拦截。  
**解决**: 给 Worker 绑定独立子域名 `api.aitextcoach.com`，前端改为调用该域名。

### 问题 4: CDN 缓存未刷新

**现象**: 修改 `index.html` 后，访问 `aitextcoach.com` 仍显示旧代码。  
**解决**: 重新执行 `npx wrangler pages deploy`，等待 10-30 秒。

---

## 最终状态

| 地址 | 用途 | 状态 |
|------|------|------|
| https://aitextcoach.com | 主站 (Pages) | ✅ 200 |
| https://www.aitextcoach.com | 跳转 (Pages) | ✅ 200 |
| https://api.aitextcoach.com | API (Worker) | ✅ 200 |
| https://aitextcoach.pages.dev | Pages 预览 | ✅ 200 |
| https://aitextcoach.xy4dan.workers.dev | Worker 预览 | ✅ 200 |

---

## 后续待办

- [ ] 删除 Render Web Service `aitextcoach`
- [ ] 删除 Render Database `aitextcoach-db`
- [ ] 设置 Cloudflare Analytics 监控
- [ ] 考虑启用 Cloudflare Rate Limiting

---

## 参考文档

- 通用技能: `/Users/yanfeiliu/.kimi_openclaw/workspace/skills/render-to-cloudflare-migration/SKILL.md`
- Cloudflare 官方: https://developers.cloudflare.com/
