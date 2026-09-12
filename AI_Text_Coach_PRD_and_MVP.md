# AI Text Coach — 产品需求文档 (PRD) + MVP 开发文档

> **文档整合日期**：2026-08-10
> **原始项目**：AI Text Coach
> **域名**：https://aitextcoach.com
> **状态**：MVP 已上线，支付已验证

---

## 目录

1. [产品概述](#一产品概述)
2. [商业计划摘要](#二商业计划摘要)
3. [市场分析](#三市场分析)
4. [产品功能需求](#四产品功能需求)
5. [技术架构](#五技术架构)
6. [API 规范](#六api-规范)
7. [数据库设计](#七数据库设计)
8. [用户界面设计](#八用户界面设计)
9. [SEO 与内容策略](#九seo-与内容策略)
10. [支付集成](#十支付集成)
11. [部署指南](#十一部署指南)
12. [发布计划与路线图](#十二发布计划与路线图)
13. [风险评估](#十三风险评估)
14. [成本估算](#十四成本估算)
15. [关键指标与目标](#十五关键指标与目标)
16. [附录](#十六附录)

---

## 一、产品概述

| 字段 | 内容 |
|------|------|
| **产品名称** | AI Text Coach |
| **域名** | aitextcoach.com |
| **品牌标语** | Make Your AI Writing Sound Human |
| **核心功能** | 将AI生成的文本改写成更自然、更像人类写作的风格 |
| **付费模式** | 免费版 + Pro订阅 ($9.99/月) |
| **目标用户** | 学生、博主、营销人员、专业人士 |
| **上线日期** | 2026年7月3日 |
| **当前状态** | MVP 已上线 \| 可访问 \| 支付已验证 |

**产品愿景**：AI Text Coach 是将AI生成文本转换为自然人写作的最快、最简单、最经济的方式。我们相信每个人都应该拥有工具让他们的写作变得真实——无需技术复杂性、隐私妥协或高昂成本。

---

## 二、商业计划摘要

### 2.1 关键指标（当前）

| 指标 | 数值 | 状态 |
|------|------|------|
| MVP 开发时间 | 3天 | ✅ 完成 |
| 开发成本 | $0（开源栈） | ✅ |
| 月度基础设施 | $0（Render.com 免费层） | ✅ |
| PayPal 集成 | 已上线（sandbox → live ready） | ✅ |
| 博客内容发布 | 8篇SEO优化文章 | ✅ |
| SEO 索引 | Google Search Console 已验证 | ✅ |

### 2.2 市场规模

| 细分市场 | 2026年价值 | CAGR | 2030年预测 |
|----------|-----------|------|-----------|
| AI内容生成 | $15.7B | 27% | $40.2B |
| AI文本人性化（细分） | $380M | 45% | $1.7B |
| 学术写作工具 | $1.2B | 18% | $2.3B |

**关键洞察**：人性化细分领域以45%的复合年增长率增长——几乎是整体市场的两倍。

### 2.3 竞争定位

| 竞品 | 价格 | 弱点 | 我们的优势 |
|------|------|------|-----------|
| StealthGPT | $39.99/月 | 昂贵，复杂UI | **便宜67%** |
| Jasper | $49/月 | 企业级，过重 | 个人聚焦 |
| Copy.ai | $36/月 | 通用输出 | 5种专业风格 |
| SurferSEO | $89/月 | SEO聚焦，非人性化 | 纯人性化 |
| Walter Writes | $12/月 | 新品牌，未验证 | 更好UX，即时 |

**单位经济：**
- **获客成本 (CAC)**：~$2（有机SEO）
- **生命周期价值 (LTV)**：$9.99 × 6个月 = $59.94
- **LTV:CAC 比率**：30:1
- **毛利率**：85%+

---

## 三、市场分析

### 3.1 目标受众

| 细分 | 痛点 | 使用场景 | 规模 |
|------|------|---------|------|
| **学生** | 论文被Turnitin标记 | 学术写作人性化 | 4500万+（美/英/加） |
| **博主** | 内容被平台拒绝 | 博客文章人性化 | 3100万活跃博主 |
| **营销人员** | 邮件文案机械 | 营销文案增强 | 1500万+营销人员 |
| **专业人士** | 报告缺乏可信度 | 商务写作润色 | 5000万+知识工作者 |

### 3.2 用户画像

| 角色 | 人口统计 | 痛点 | 使用模式 |
|------|---------|------|---------|
| **学生Sarah** | 20岁，大学生 | 论文被Turnitin标记 | 每月3-5篇论文，学术风格 |
| **博主Ben** | 32岁，内容创作者 | 博客文章听起来像机器人 | 每日发文，创意/休闲风格 |
| **营销人员Maria** | 28岁，SaaS营销 | 邮件文案缺乏参与度 | 每周活动，商务风格 |
| **专业人士Paul** | 45岁，顾问 | 报告看起来像AI生成 | 每月报告，商务/学术风格 |

---

## 四、产品功能需求

### 4.1 核心功能：文本人性化

**FR-001: 文本输入**
- 用户可将文本粘贴到文本区
- 最小输入：10字符
- 最大输入：50,000字符（Pro），5,000（免费）
- 实时字符和字数统计

**FR-002: 风格选择**
- 5种写作风格：学术、商务、创意、休闲、精简
- 免费层：2种风格（休闲、精简）
- Pro层：全部5种风格
- 风格显示图标和描述

**FR-003: 文本增强**
- 系统将文本+风格发送到AI后端
- 5秒内返回人性化版本
- 显示"改写前"和"改写后"对比
- 人性化评分（0-100）客户端计算

**FR-004: 结果展示**
- 标签页界面：改写前 / 改写后
- 复制到剪贴板按钮
- 输出字数统计
- "人性化程度"视觉评分条

### 4.2 用户管理

**FR-005: 邮箱识别**
- 用户输入邮箱（免费层可选）
- 邮箱用于配额追踪和Pro验证
- 无需密码（MVP简化）

**FR-006: 配额系统**
- 免费：每日历日5,000字符
- Pro：无限
- 配额在UTC午夜重置
- 按邮箱追踪用量（或IP回退）

**FR-007: Pro状态验证**
- `/api/check-pro?email=` 端点
- 返回 {is_pro: boolean}
- 在邮箱输入失焦和增强后检查

### 4.3 支付与订阅

**FR-008: PayPal集成**
- 弹窗中的PayPal订阅按钮
- 计划：$9.99/月 USD
- 测试用sandbox模式，生产用live模式

**FR-009: Pro激活**
- PayPal批准后，前端调用 `/api/activate-pro`
- 后端用PayPal API验证订阅
- 数据库中将邮箱标记为Pro
- 立即UI解锁（无需刷新）

**FR-010: 订阅管理**
- 用户可查看订阅状态
- 通过PayPal取消（非内部管理）
- 每次API调用时检查Pro状态

### 4.4 分析与追踪

**FR-011: 点击追踪**
- 追踪"Enhance My Text"按钮点击
- 追踪"Upgrade to Pro"按钮点击
- 按按钮类型每日聚合

**FR-012: 使用统计**
- `/api/stats` 端点返回：
  - 今日总增强次数
  - 按类型总点击数
  - 活跃Pro用户
  - 每次增强平均字符数

### 4.5 内容管理

**FR-013: 博客系统**
- `/blog/` 目录中的静态HTML博客文章
- 列出所有文章的索引页
- 通过Git + Render.com 定时发布
- SEO优化的标题、meta描述、schema标记

---

## 五、技术架构

### 5.1 技术栈

| 层级 | 技术 | 理由 |
|------|------|------|
| 前端 | HTML + Tailwind CSS CDN | 零构建，零依赖 |
| 后端 | Python 3 + 内置http.server | 零外部框架 |
| AI引擎 | DeepSeek Chat API | 性价比高，质量好 |
| 数据库 | PostgreSQL (Render.com) | 免费层，自动扩展 |
| 支付 | PayPal Subscription API | 全球覆盖，简单KYC |
| 托管 | Render.com | 免费层，GitHub自动部署 |
| CDN | Cloudflare | 免费SSL，全球边缘节点 |

### 5.2 架构哲学："最小可行复杂度"

- 单文件前端 (index.html)
- 单文件后端 (server.py)
- 零npm依赖
- 零构建步骤
- 30秒部署

**结果**：3天MVP，$0基础设施成本，99.9%正常运行时间。

### 5.3 系统架构图

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   用户浏览器    │────▶│  Cloudflare CDN  │────▶│  Render.com     │
│                 │     │  (SSL + 缓存)    │     │  (Python Server)│
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                               ┌──────────────────────────┼──────────┐
                               │                          │          │
                               ▼                          ▼          ▼
                        ┌─────────────┐          ┌─────────────┐ ┌──────────┐
                        │ PostgreSQL  │          │  DeepSeek   │ │  PayPal  │
                        │ (Render)    │          │  API        │ │  API     │
                        └─────────────┘          └─────────────┘ └──────────┘
```

### 5.4 前端架构

**单文件方案：**
- `index.html` 包含：HTML结构、Tailwind CSS、JavaScript
- 零构建步骤
- 零npm依赖
- CDN资源：Tailwind、Google Fonts、PayPal SDK

**状态管理：**
- 原生JavaScript
- localStorage用于Pro状态（仅客户端）
- 服务器对配额/支付检查有权威

---

## 六、API 规范

### POST /api/enhance

**请求：**
```json
{
  "text": "string (10-50000 chars)",
  "style": "academic|business|creative|casual|concise",
  "email": "string (optional)"
}
```

**响应：**
```json
{
  "success": true,
  "result": "humanized text",
  "is_pro": false,
  "chars_used": 1500,
  "chars_remaining": 3500
}
```

**错误代码：**
- `400`: 输入无效
- `402`: 需要付费（Pro功能）
- `429`: 配额超限
- `500`: 服务器错误

### POST /api/activate-pro

**请求：**
```json
{
  "email": "user@example.com",
  "subscription_id": "I-SUBSCRIPTION123"
}
```

**响应：**
```json
{
  "success": true,
  "message": "Pro activated"
}
```

### GET /api/check-pro

**查询：** `?email=user@example.com`

**响应：**
```json
{
  "is_pro": true
}
```

### GET /api/config

**响应：**
```json
{
  "paypal_client_id": "AaBbCc...",
  "paypal_plan_id": "P-123..."
}
```

---

## 七、数据库设计

```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_pro BOOLEAN DEFAULT FALSE,
    subscription_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 每日用量追踪
CREATE TABLE usage_stats (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    chars_used INTEGER DEFAULT 0,
    usage_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(email, usage_date)
);

-- 点击分析
CREATE TABLE click_stats (
    id SERIAL PRIMARY KEY,
    button_type VARCHAR(50) NOT NULL,
    click_date DATE DEFAULT CURRENT_DATE,
    count INTEGER DEFAULT 1,
    UNIQUE(button_type, click_date)
);
```

---

## 八、用户界面设计

### 8.1 页面结构

```
┌─────────────────────────────────────┐
│  导航: Logo | 首页 | 博客 | 重置    │
├─────────────────────────────────────┤
│  主视觉区: 标题 + 副标题 + 徽章     │
├─────────────────────────────────────┤
│  工具区:                            │
│  ├─ 邮箱输入                        │
│  ├─ 风格选择器                      │
│  ├─ 文本输入（带字数统计）          │
│  ├─ 增强按钮                        │
│  ├─ 错误显示                        │
│  └─ 结果（改写前/后标签页）         │
│      ├─ 人性化评分                  │
│      └─ 复制按钮                    │
├─────────────────────────────────────┤
│  功能: 3列网格                      │
├─────────────────────────────────────┤
│  定价: 免费 vs Pro 对比             │
├─────────────────────────────────────┤
│  页脚: 链接 + 版权                  │
└─────────────────────────────────────┘
```

### 8.2 设计系统

| 元素 | 规范 |
|------|------|
| 主色 | Charcoal #1C1C1E |
| 强调色 | Rose Gold #B76E79 |
| 背景色 | Cream #FAF9F6 |
| 字体（标题） | Playfair Display (serif) |
| 字体（正文） | DM Sans (sans-serif) |
| 圆角 | 0（锐利，编辑风格） |
| 阴影 | 无（扁平设计） |
| 间距 | 大量留白，编辑感 |

### 8.3 响应式断点

| 断点 | 宽度 | 调整 |
|------|------|------|
| 移动端 | < 640px | 单列，堆叠布局 |
| 平板 | 640-1024px | 两列（适用处） |
| 桌面端 | > 1024px | 完整布局，最大宽度768px容器 |

---

## 九、SEO 与内容策略

### 9.1 核心SEO原则

**主攻策略：高转化、低竞争的长尾关键词**

**我们 targeting：**
- `how to make AI text sound human` (how-to意图，低竞争)
- `AI text rewriter for emails` (特定用例，低竞争)
- `remove AI detection patterns from writing` (问题-解决，低竞争)
- `why does my AI writing sound robotic` (问题格式，低竞争)
- `make ChatGPT output less formal` (工具特定，低竞争)

**我们不 targeting（除非明确批准）：**
- `AI humanizer` (高竞争，工具聚焦)
- `bypass AI detection` (高竞争，声誉风险)
- `undetectable AI writing` (高竞争，垃圾关联)

### 9.2 内容发布日历（前8周）

| 周次 | 内容 |
|------|------|
| 第1-2周 | Landing Page: "AI Humanizer" / "Free AI Text Rewriter" / Blog: "How to Make AI Writing Sound Human" |
| 第3-4周 | Blog: "5 Best AI Humanizers Compared" / "How to Bypass AI Detection" / Landing: "AI Text Rewriter for Students" |
| 第5-6周 | Blog: "How to Humanize ChatGPT Output" / "AI Writing Enhancer for Marketing" / Landing: "AI Humanizer for Bloggers" |
| 第7-8周 | Blog: "AI Detection Tools Comparison" / "Science of Making AI Text Sound Human" / Landing: "AI Concise Rewriter" |

### 9.3 SEO关键词目标

| 优先级 | 关键词 | 月搜索量 | 难度 | 内容类型 |
|--------|--------|---------|------|---------|
| P0 | AI humanizer | 12,000 | 中 | Landing page |
| P0 | make AI text sound human | 6,200 | 低 | Blog post |
| P0 | AI text rewriter | 8,500 | 中 | Landing page |
| P1 | how to remove AI detection | 2,800 | 中 | Blog post |
| P1 | AI writing enhancer free | 1,500 | 低 | Landing page |
| P2 | best AI text rewriter for students | 800 | 低 | Blog post |

### 9.4 Schema 标记 (JSON-LD)

```json
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "AI Text Coach",
  "description": "AI text humanizer and rewriter that makes AI-generated text sound natural and human-like",
  "url": "https://aitextcoach.com",
  "applicationCategory": "TextEditor",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
```

---

## 十、支付集成

### 10.1 PayPal（已启用）

| 字段 | 状态 |
|------|------|
| **集成状态** | ✅ 已验证可用 |
| **账户** | yanfei.liu.ca@gmail.com |
| **支付链接** | 网站上可见 |
| **测试记录** | 已通过收款测试 |

### 10.2 PayPal 付费闭环流程

```
用户点击 "Upgrade to Pro"
    ↓
弹出 PayPal 支付窗口
    ↓
用户完成 PayPal 订阅
    ↓
前端调用 /api/activate-pro
    ↓
后端验证 PayPal 订阅状态
    ↓
标记用户为 Pro
    ↓
前端解锁所有功能
```

### 10.3 定价对比

| 竞品价格 | 我们的价格 | 节省 |
|---------|-----------|------|
| $39.99 (StealthGPT) | $9.99 | 75% |
| $49.00 (Jasper) | $9.99 | 80% |
| $36.00 (Copy.ai) | $9.99 | 72% |
| $89.00 (SurferSEO) | $9.99 | 89% |

---

## 十一、部署指南

### 11.1 部署前检查清单

- [ ] 本地测试通过（`./start.sh` 能跑，浏览器能打开）
- [ ] API Key 有效（测试过改写功能）
- [ ] 域名 aitextcoach.com 已注册 ✅

### 11.2 部署步骤

**第一步：创建 GitHub 仓库**
1. 打开 github.com 登录账号
2. 点击右上角 + → New repository
3. 仓库名填：`aitextcoach`
4. 推送代码

**第二步：注册 Render.com**
1. 打开 render.com
2. 点击 Get Started for Free
3. 选择 Continue with GitHub

**第三步：创建 Web Service**
1. Render 控制台点击 New + → Web Service
2. 选择 `aitextcoach` 仓库
3. 配置：Runtime: Python 3, Start Command: `python server.py`
4. 设置环境变量（DS_API_KEY, PAYPAL_CLIENT_ID 等）
5. 点击 Create Web Service

**第四步：绑定域名**
1. Render 控制台 → Settings → Custom Domains
2. 添加：`aitextcoach.com`
3. 在 Cloudflare DNS 添加 CNAME 记录
4. 等待 DNS 生效

### 11.3 环境变量

```bash
DS_API_KEY=你的DeepSeek API Key
PAYPAL_CLIENT_ID=你的PayPal Client ID
PAYPAL_CLIENT_SECRET=你的PayPal Secret
PAYPAL_MODE=sandbox          # 测试用，上线后改 live
PAYPAL_PLAN_ID=你的Plan ID
```

---

## 十二、发布计划与路线图

### 12.1 已完成 ✅

| 日期 | 里程碑 |
|------|--------|
| 2026-07-03 | MVP 上线（前端 + API） |
| 2026-07-04 | PayPal 订阅集成 |
| 2026-07-05 | SEO 基础设施（sitemap, schema, GSC） |
| 2026-07-06 | 博客内容引擎（8篇文章） |
| 2026-07-09 | AI 后端迁移（Gemini → DeepSeek） |

### 12.2 Q3 2026（近期）

| 周次 | 里程碑 |
|------|--------|
| 7月第3周 | 修复HTTP/HTTPS重定向，优化标题 |
| 7月第4周 | Product Hunt 上线，Reddit 存在 |
| 8月第1-2周 | 用户登录系统（邮箱/密码） |
| 8月第3-4周 | 批量处理功能 |
| 9月第1-2周 | Word/PDF 导出 |
| 9月第3-4周 | 年度计划上线，推荐计划 |

### 12.3 Q4 2026（中期）

| 月份 | 里程碑 |
|------|--------|
| 10月 | Chrome 扩展，开发者API |
| 11月 | 多语言支持（西班牙语、法语、中文） |
| 12月 | 移动应用（PWA），团队协作功能 |

### 12.4 2027 愿景

- **$10K MRR** 到2027年3月
- **50K 月活用户**
- **集成生态**：WordPress插件，Google Docs 插件
- **企业层**：$49/月 团队版

---

## 十三、风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| AI检测技术进化 | 高 | 高 | 持续模型更新 |
| 竞品价格战 | 中 | 中 | UX/速度差异化 |
| API成本上涨 | 中 | 中 | 多供应商回退 |
| PayPal政策变化 | 低 | 高 | Stripe 备用集成 |
| SEO算法更新 | 中 | 中 | 流量来源多样化 |
| 学术政策反弹 | 低 | 高 | 聚焦"增强"而非"绕过" |

---

## 十四、成本估算

| 项目 | 月成本 | 年成本 |
|------|--------|--------|
| 域名 (Namecheap) | — | $12 |
| 托管 (Render.com 免费) | $0 | $0 |
| 数据库 (Render.com 免费) | $0 | $0 |
| AI API (DeepSeek) | ~$5 | ~$60 |
| CDN (Cloudflare 免费) | $0 | $0 |
| PayPal 手续费 | 2.9% + $0.30/笔 | 变动 |
| **固定成本总计** | **~$5** | **~$72** |

**盈亏平衡分析：**

| 场景 | 所需用户 | 月收入 |
|------|---------|--------|
| 盈亏平衡 | 1个Pro用户 | $9.99 |
| 盈利 | 10个Pro用户 | $99.90 |
| 创始人薪水 ($3K/月) | 300个Pro用户 | $2,997 |
| 完全独立 ($5K/月) | 500个Pro用户 | $4,995 |

**当前跑道**：无限（成本 < $10/月）。

---

## 十五、关键指标与目标

| 指标 | 当前值 | 目标 | 期限 |
|------|--------|------|------|
| **站点访问** | 待补充 | 100/天 | 30天内 |
| **首笔订单** | 未 | 1 | 7天内 |
| **月度收入** | ¥0 | ¥500+ | 90天内 |
| **用户注册** | 0 | 50+ | 90天内 |

### 6个月财务预测

| 月份 | 免费用户 | Pro用户 | MRR | 累计收入 |
|------|---------|---------|-----|---------|
| 7月（上线） | 50 | 2 | $20 | $20 |
| 8月 | 200 | 8 | $80 | $100 |
| 9月 | 500 | 20 | $200 | $300 |
| 10月 | 1,200 | 50 | $500 | $800 |
| 11月 | 2,500 | 100 | $1,000 | $1,800 |
| 12月 | 5,000 | 200 | $2,000 | $3,800 |

---

## 十六、附录

### 附录A：五种写作风格

| 风格 | 用途 | 特点 |
|------|------|------|
| **Academic** | 论文、学术写作 | 正式、客观、被动语态 |
| **Business** | 邮件、报告 | 简洁、行动导向、专业 |
| **Creative** | 博客、故事 | 生动、意象丰富、有节奏 |
| **Casual** | 社交媒体 | 对话式、轻松、像朋友聊天 |
| **Concise** | 精简内容 | 去掉废话、保留核心 |

### 附录B：功能对比矩阵

| 功能 | 免费层 | Pro ($9.99/月) |
|------|--------|----------------|
| 每日字符限制 | 5,000 | 无限 |
| 写作风格 | 2 (Casual, Concise) | 5 (全部) |
| 语气调整 | ❌ | ✅ |
| Word/PDF 导出 | ❌ | ✅ |
| 历史与保存 | ❌ | ✅ |
| 批量处理 | ❌ | ✅ |
| 人性化评分 | ✅ | ✅ |
| 复制结果 | ✅ | ✅ |
| 隐私（无存储） | ✅ | ✅ |

### 附录C：AI OPC 运营团队

| 角色 | 员工 | 职责 |
|------|------|------|
| **项目经理** | 阿宝 (Abao) | 策略、调度、QA |
| **主力开发** | 小代 (Codex) | 核心工程 |
| **代码审查** | 小扣 (Claude) | 架构、安全审查 |
| **SEO专家** | 小弟 (DeepSeek) | 内容生成、关键词研究 |
| **研究主管** | 小琪 (Kimi) | 市场分析、竞品情报 |
| **原型工程师** | 小咪 (Kimi Code) | 沙盒实验 |
| **外包代理** | 小麦 (Manus) | 独立验证 |

### 附录D：原始文档索引

| 文档 | 路径 |
|------|------|
| 商业计划与PRD v1.0 | `Desktop/AI_Text_Coach_Business_Plan_and_PRD_v1.0.md` |
| 项目档案 | `AI_OPC/项目档案/01_aitextcoach.md` |
| README | `Developer/aitextcoach/README.md` |
| SEO策略 | `Developer/aitextcoach/SEO_STRATEGY.md` |
| PayPal方案 | `Developer/aitextcoach/PAYPAL_PLAN.md` |
| 部署指南 | `Developer/aitextcoach/DEPLOY.md` |
| 博客发布日历 | `Developer/aitextcoach/PUBLISH_CALENDAR.md` |
| PayPal设置 | `Developer/aitextcoach/PAYPAL_SETUP.md` |

---

> **文档整合**：阿龙 (Abao)
> **整合日期**：2026-08-10
> **版本**：v1.0（综合版）
