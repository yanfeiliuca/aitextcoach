# AI Text Coach

> **域名**: aitextcoach.com
> **品牌**: AI Text Coach — Make Your AI Writing Sound Human
> **核心功能**: 将 AI 生成的文本改写成更自然、更像人类写作的风格
> **付费模式**: 免费版 + Pro 订阅 ($9.99/月)

本项目已从 Render（Python + PostgreSQL）迁移至 Cloudflare（Worker + D1 + KV + Pages）。迁移历史与踩坑记录见 `docs/sop/MIGRATION_SOP.md`（仅本地保留，不进 git）。

---

## 快速启动

```bash
npm install
npm run dev      # wrangler dev，本地跑 Worker（API）
```

静态页面（`public/`）直接用浏览器打开，或通过 `wrangler pages dev public` 本地预览。前端硬编码请求 `https://api.aitextcoach.com`，本地联调需要临时改 `public/*.html` 里的 `API_BASE`，或对本地 Worker 起对应的域名代理。

---

## 功能

### 免费版
- 500 字符/天（`src/index.ts` 中 `FREE_LIMIT`，以后端为准）
- Casual / Concise 等基础风格
- 即时改写结果

### Pro 版（$9.99/月）
- 无限字符
- 全部写作风格（Formal / Casual / Academic / Simple / Creative / Business，见 `src/deepseek.ts`）
- PayPal 订阅解锁

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 静态前端 | HTML + Tailwind CSS CDN | `public/`，通过 Cloudflare Pages 部署，零构建 |
| API 后端 | Cloudflare Worker (TypeScript) | `src/`，通过 `wrangler deploy` 部署 |
| 数据库 | Cloudflare D1 (SQLite) | 用户、用量、点击统计，见 `migrations/0001_initial.sql` |
| KV | Cloudflare KV | DeepSeek 调用预算状态（`budget_state`） |
| AI | DeepSeek Chat API | 文本改写，见 `src/deepseek.ts` |
| 支付 | PayPal Subscription API | 全球覆盖、开发者友好 |

---

## 写作风格

后端 `src/deepseek.ts` 中定义的风格（`prompts` 字典）：

| 风格 | 用途 |
|------|------|
| **formal** | 正式、专业 |
| **casual** | 对话式、轻松（默认） |
| **academic** | 学术、正式、复杂词汇 |
| **simple** | 简化、易懂 |
| **creative** | 生动、叙事性强 |
| **business** | 商务、清晰、可执行 |

---

## 文件结构

```
aitextcoach-cf/
├── src/
│   ├── index.ts           ← Worker 路由分发、CORS
│   ├── db.ts               ← D1 数据库操作
│   └── deepseek.ts         ← DeepSeek API 调用 + 预算控制
├── public/                 ← 静态前端页面（Pages 部署）
├── migrations/
│   └── 0001_initial.sql    ← D1 schema
├── docs/sop/                ← 迁移 SOP（gitignored，仅本地）
├── wrangler.toml            ← Worker 绑定（D1 / KV / vars）
└── PAYPAL_SETUP.md          ← PayPal 集成设置指南
```

---

## 配置环境变量 / Secrets

Cloudflare 上没有 `.env` 文件，配置分两部分：

**`wrangler.toml` 中的 `[vars]`（明文，可提交）**：
```toml
PAYPAL_MODE = "sandbox"       # 上线后改 "live"
PAYPAL_PLAN_ID = "P-7SB75295DK0602635NJFH34Q"
```

**通过 `wrangler secret` 设置的密钥（不进 git）**：
```bash
npx wrangler secret put DS_API_KEY
npx wrangler secret put PAYPAL_CLIENT_SECRET
```

`PAYPAL_CLIENT_ID` 目前直接硬编码在 `src/index.ts`（`handleConfig`）里，不通过环境变量注入，前端通过 `/api/config` 获取。

详细 PayPal 设置步骤见 [PAYPAL_SETUP.md](PAYPAL_SETUP.md)。

---

## 部署

**Worker（API，绑定 api.aitextcoach.com）：**
```bash
npx wrangler deploy
```

**静态页面（Pages，绑定 aitextcoach.com）：**
```bash
npx wrangler pages deploy public --project-name=aitextcoach --branch=main
```

⚠️ Worker 必须绑定独立子域名 `api.aitextcoach.com`，不能走 Pages 的路由，否则 POST 请求会被拦截返回 405。详见 `docs/sop/MIGRATION_SOP.md`。

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/enhance` | POST | 改写文本 |
| `/api/activate-pro` | POST | 激活 Pro 订阅（验证 PayPal） |
| `/api/config` | GET | 前端配置（PayPal Client ID 等） |
| `/api/check-pro` | GET | 查询邮箱是否为 Pro |
| `/api/track-click` | POST | 点击统计 |
| `/api/stats` | GET | 数据仪表盘（含预算状态） |
| `/api/debug-add-pro` | POST | 调试用：手动标记邮箱为 Pro（无鉴权，谨慎暴露） |

---

## 付费闭环流程

```
用户点击 "Upgrade to Pro"
    ↓
弹出 PayPal 支付窗口
    ↓
用户完成 PayPal 订阅
    ↓
前端调用 /api/activate-pro
    ↓
Worker 验证 PayPal 订阅状态
    ↓
D1 中标记该邮箱为 Pro (users.is_pro)
    ↓
前端解锁所有功能
```

---

*迁移自 Render 版本（`~/Developer/aitextcoach`）*
