# aitextcoach.com 网站结构说明

> 通过浏览器实测 https://aitextcoach.com 生成，记录当前**线上实际运行**的页面结构、路由行为和已知问题。用于和本地仓库代码对照，发现两者的差异。生成日期：2026-08-07。

---

## 1. 域名与部署拓扑

| 域名 | 服务 | 内容来源 |
|------|------|---------|
| `aitextcoach.com` / `www.aitextcoach.com` | Cloudflare Pages | 本仓库 `public/` 目录 |
| `api.aitextcoach.com` | Cloudflare Worker | 本仓库 `src/` 目录（`npx wrangler deploy`） |

前端页面通过硬编码的 `const API_BASE = 'https://api.aitextcoach.com'` 调用后端，详见各 HTML 文件内联 `<script>`。

---

## 2. 实测页面清单

### 2.1 首页

`https://aitextcoach.com/` — 200，对应 `public/index.html`。

**页面结构（从上到下）：**
1. 顶部导航：`AI Text Coach`（Logo，链接 `/`）· `Home`（`/`）· `Blog`（`/blog`，**实际不可用，见 §3**）· `Reset`（清空表单，仅前端行为）
2. Hero：标题 "Make Your AI Writing Sound Human" + 副标题 + 3 个卖点（5 Writing Styles / Instant Results / Free to Start）
3. 改写工具表单：
   - 邮箱输入（可选，用于配额追踪与 Pro 状态识别）
   - 风格下拉框：`Casual`✓Free、`Concise`✓Free、`Academic`🔒Pro、`Business`🔒Pro、`Creative`🔒Pro（disabled）
   - 文本输入框 + "Try with sample text" 快捷填充
   - "Enhance My Text" 提交按钮
   - 改写前/改写后 Tab 切换 + "可读性"进度条（`humanBar`）
4. "Why Choose AI Text Coach?" 卖点区块（5 Writing Styles / Instant Results / Privacy First）
5. 定价区块：Free（$0，列出限制）vs Pro（$9.99/月，`RECOMMENDED` 标记）
6. PayPal 升级弹窗（`showPayPalModal`）：邮箱输入 + PayPal Smart Button（`vault=true&intent=subscription`）→ 成功后调用 `/api/activate-pro`
7. Footer："AI Text Coach" + 标语 + Home/Tool 链接（均指向 `/`）+ Privacy Policy / Terms of Service / Contact（纯文本，未做成可点击链接或对应页面不存在）

**页面内嵌的第三方脚本：**
- Tailwind CDN（`cdn.tailwindcss.com`，无构建步骤）
- Google Analytics 4（`gtag.js`，测量 ID `G-CZSYZXPKV1`）
- PayPal SDK（动态注入 `<script>`，`client-id` 来自 `/api/config` 返回值）

### 2.2 博客文章页（8 篇，root 路径，可正常访问）

| URL（extensionless，线上实测跳转后的地址） | 本地对应文件 |
|---|---|
| `/free-ai-humanizer-online` | `public/free-ai-humanizer-online.html` |
| `/best-ai-text-rewriter-for-students` | `public/best-ai-text-rewriter-for-students.html` |
| `/ai-humanizer-passes-turnitin` | `public/ai-humanizer-passes-turnitin.html` |
| `/ai-writing-enhancer-free` | `public/ai-writing-enhancer-free.html` |
| `/how-to-make-ai-text-sound-human` | `public/how-to-make-ai-text-sound-human.html` |
| `/why-does-ai-writing-sound-robotic` | `public/why-does-ai-writing-sound-robotic.html`（2026-08-07 补迁移） |
| `/how-to-make-chatgpt-output-sound-human` | `public/how-to-make-chatgpt-output-sound-human.html`（2026-08-07 补迁移） |
| `/how-to-remove-ai-detection-from-text` | `public/how-to-remove-ai-detection-from-text.html`（2026-08-07 补迁移） |

访问 `.html` 后缀 URL（如 `/free-ai-humanizer-online.html`）会自动跳转到无后缀地址，符合 `~/CLAUDE.md` 中"Extensionless URLs are mandatory"的 SEO 规范。

**文章页结构**：与首页共享同一份顶部导航（Home / Blog / 无表单），正文是纯静态 `<article>` 内容，不嵌入改写工具，结尾复用首页的 Footer。这些文章是从 `~/Developer/aitextcoach/blog/` 原样拷贝（无任何改动，diff 为空），文章导航栏的 `Blog` 链接指向 `/blog` 列表页（§2.3）。

### 2.3 `/blog` 列表页

`https://aitextcoach.com/blog` — 308 跳转到 `/blog/`，对应 `public/blog/index.html`（2026-08-08 新增）。同款 nav/footer，正文是按发布日期倒序排列的 8 篇文章卡片（标题 + 摘要 + 日期），每张卡片链接到对应文章的根路径。纯静态列表，无分页、无标签/分类。

---

## 3. 发现的问题（线上实测 vs 仓库代码/sitemap 不一致）

### 3.1 ~~`/blog` 路由实际不存在，静默 fallback 到首页~~ （已于 2026-08-08 修复并部署）

- 问题原状：请求 `https://aitextcoach.com/blog` 返回 **HTTP 200**，但响应内容是首页 `index.html` 的内容（非 404，也非博客列表页）。原因是 `public/` 目录下没有 `blog/index.html`，Cloudflare Pages 找不到匹配文件时默认 fallback 到根 `index.html`。
- 修复：新增 `public/blog/index.html` 作为真正的博客列表页，收录全部 8 篇文章（标题/摘要/日期，按发布时间倒序），链接到各文章的根路径（`/free-ai-humanizer-online` 等，文章本体保持原位不动）。Cloudflare Pages 对目录型静态资源的默认行为是 `/blog` → 308 跳转到 `/blog/` → 命中 `blog/index.html`，无需额外配置 `_redirects`。
- `sitemap.xml` 补上 `https://aitextcoach.com/blog` 一条（priority 0.9，changefreq weekly），现在共 10 条 URL。
- 线上已验证：`/blog` 308 跳转到 `/blog/`，返回博客列表页，8 篇文章链接全部可点击且各自 200。首页与文章页导航栏的 "Blog" 链接现在指向真实存在的页面。

### 3.2 ~~`sitemap.xml` 是 Render 时代的旧文件，8/9 条目已失效~~ （已于 2026-08-07 修复并部署）

`public/sitemap.xml` 已重新生成为 6 条有效 URL（首页 + 5 篇实际存在的博客文章，均为无后缀路径），并通过 `wrangler pages deploy` 上线，线上已验证生效。以下为修复前的记录：

```
/                                              ✅ 有效
/blog/                                          ❌ fallback 到首页（§3.1）
/blog/how-to-make-ai-text-sound-human.html      ❌ 路径不存在（现在是 /how-to-make-ai-text-sound-human）
/blog/why-does-ai-writing-sound-robotic.html    ❌ 文章本体在本次迁移中被丢弃，仓库里已不存在
/blog/how-to-make-chatgpt-output-sound-human.html ❌ 同上，已丢弃
/blog/how-to-remove-ai-detection-from-text.html ❌ 同上，已丢弃
/blog/free-ai-humanizer-online.html             ❌ 路径不存在（现在是 /free-ai-humanizer-online）
/blog/best-ai-text-rewriter-for-students.html   ❌ 路径不存在（现在是 /best-ai-text-rewriter-for-students）
/blog/ai-humanizer-passes-turnitin.html         ❌ 路径不存在（现在是 /ai-humanizer-passes-turnitin）
/blog/ai-writing-enhancer-free.html             ❌ 路径不存在（现在是 /ai-writing-enhancer-free）
```

对照旧项目 `~/Developer/aitextcoach/blog/`，一共有 8 篇文章 + 1 个 blog 首页；这次迁移到 Cloudflare 时只把其中 5 篇搬到了 `public/` 根目录（且改成无 `/blog/` 前缀），另外 3 篇（`why-does-ai-writing-sound-robotic.html`、`how-to-make-chatgpt-output-sound-human.html`、`how-to-remove-ai-detection-from-text.html`）和 blog 首页本身都没有迁移过来。

**2026-08-07 更新**：3 篇缺失文章已从 `~/Developer/aitextcoach/blog/` 原样拷贝到 `public/`，`sitemap.xml` 扩充到 9 条 URL（首页 + 8 篇文章），并通过 `wrangler pages deploy` 部署上线，线上已验证生效。

**2026-08-08 更新**：`/blog` 列表页已补上（见 §3.1），`sitemap.xml` 现为 10 条 URL（首页 + `/blog` + 8 篇文章）。至此本文档记录的问题均已修复。

### 3.3 `robots.txt` 被 Cloudflare 自动追加内容

线上 `robots.txt` 除了仓库里的两行（`User-agent: * / Allow: /` + `Sitemap:`），额外被 Cloudflare 自动注入了一段 "Content Signal"（AI 训练/抓取许可声明）区块，屏蔽了 GPTBot、Google-Extended、ClaudeBot、Bytespider、CCBot 等 AI 训练爬虫，但保留搜索引擎正常抓取（`Content-Signal: search=yes,ai-train=no,use=reference`）。这是 Cloudflare 平台层面的托管功能，不在仓库文件里，修改需要去 Cloudflare Dashboard 的 "Content Signals" / Bot 设置里调整，不是改 `public/robots.txt` 能控制的。

### 3.4 前端文案与后端实际配额不一致

首页定价区块和博客文章正文都写"Free tier = 5000 characters/day，2 种免费风格（Casual + Concise）"，但 `src/index.ts` 里 `FREE_LIMIT = 500`，且 `src/deepseek.ts` 的 `prompts` 字典里根本没有 `concise` 这个 key（只有 `formal/casual/academic/simple/creative/business`）。前端下拉框选 "Concise" 提交后，后端会 `prompts[style] || prompts.casual` 兜底成 casual 效果。这是迁移前后端时遗留的文案/实现不同步，仅记录不在本次任务范围内修复。

---

## 4. 与本仓库代码的对应关系速查

| 线上行为 | 仓库来源 |
|---|---|
| 首页 UI / PayPal 弹窗 / GA 埋点 | `public/index.html` |
| 5 篇博客文章页 | `public/*.html`（除 `index.html` 外） |
| `/api/*` 全部接口 | `src/index.ts`（路由）+ `src/db.ts`（D1）+ `src/deepseek.ts`（AI 调用+预算） |
| 免费额度 500 字/天 | `src/index.ts` `FREE_LIMIT` |
| PayPal Client ID（写死，非 secret） | `src/index.ts` `handleConfig()` |
| `PAYPAL_MODE` / `PAYPAL_PLAN_ID` | `wrangler.toml` `[vars]` |
| `DS_API_KEY` / `PAYPAL_CLIENT_SECRET` | Cloudflare Worker Secret（`wrangler secret put`，不在仓库） |
