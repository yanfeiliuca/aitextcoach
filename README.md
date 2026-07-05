# AI Text Coach

> **域名**: aitextcoach.com (已注册)  
> **品牌**: AI Text Coach — Make Your AI Writing Sound Human  
> **核心功能**: 将AI生成的文本改写成更自然、更像人类写作的风格  
> **付费模式**: 免费版 + Pro订阅 ($9.99/月)

---

## 快速启动

```bash
cd ~/Desktop/aitextcoach
python server.py
```

浏览器打开 http://localhost:3000

---

## 功能

### 免费版
- 5000 字符/天
- 2 种写作风格 (Casual, Concise)
- 基础可读性评分
- 复制结果

### Pro版 ($9.99/月)
- 无限字符
- 全部 5 种写作风格
- 语气微调
- Word/PDF 导出
- 历史记录
- 批量处理

---

## 技术栈

| 层级 | 技术 | 理由 |
|------|------|------|
| 前端 | HTML + Tailwind CSS CDN | 零构建、零依赖 |
| 后端 | Python 3 + 内置 http.server | 零外部依赖 |
| AI | Gemini 2.5 Flash | 快速、免费额度大 |
| 支付 | PayPal Subscription API | 全球覆盖、开发者友好 |
| 部署 | Render.com (免费版) | 一键部署 |

---

## 5种写作风格

| 风格 | 用途 | 示例变化 |
|------|------|---------|
| **Academic** | 论文、学术写作 | 正式、客观、被动语态 |
| **Business** | 邮件、报告 | 简洁、行动导向、专业 |
| **Creative** | 博客、故事 | 生动、意象丰富、有节奏 |
| **Casual** | 社交媒体、个人 | 对话式、轻松、像朋友聊天 |
| **Concise** | 精简内容 | 去掉废话、保留核心 |

---

## 文件结构

```
aitextcoach/
├── index.html              ← 主站前端
├── server.py               ← API后端（含PayPal集成）
├── start.sh                ← 一键启动脚本
├── blog/                   ← 已发布博客文章
├── blog-to-publish/        ← 待发布队列
├── render.yaml             ← Render.com 部署配置
├── PAYPAL_SETUP.md         ← PayPal集成设置指南
├── PUBLISH_CALENDAR.md     ← 博客发布日历
├── SEO_STRATEGY.md         ← SEO策略文档
└── README.md               ← 本文档
```

---

## 配置环境变量

本地测试创建 `.env` 文件：

```bash
GOOGLE_API_KEY=你的Gemini API Key
PAYPAL_CLIENT_ID=你的PayPal Client ID
PAYPAL_CLIENT_SECRET=你的PayPal Secret
PAYPAL_MODE=sandbox          # 测试用，上线后改 live
PAYPAL_PLAN_ID=你的Plan ID
```

详细 PayPal 设置步骤见 [PAYPAL_SETUP.md](PAYPAL_SETUP.md)。

---

## 部署到 Render.com

1. 推送代码到 GitHub
2. 登录 [render.com](https://render.com)
3. New Web Service → 选择 GitHub 仓库
4. 框架选 "Other"
5. 添加环境变量（见上方）
6. 点击 Deploy

---

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/enhance` | POST | 改写文本 |
| `/api/activate-pro` | POST | 激活Pro订阅 |
| `/api/config` | GET | 前端配置（PayPal Client ID等） |
| `/api/track-click` | POST | 点击统计 |
| `/api/stats` | GET | 数据仪表盘 |

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
后端验证 PayPal 订阅状态
    ↓
标记用户为 Pro
    ↓
前端解锁所有功能
```

---

## 状态

- ✅ MVP 前端
- ✅ API 后端
- ✅ 5 种写作风格
- ✅ 配额系统
- ✅ 博客系统
- ✅ SEO 优化
- ✅ PayPal 订阅集成
- ⏳ 用户登录系统（邮箱+密码）
- ⏳ 数据库持久化（PostgreSQL）
- ⏳ 批量处理功能

---

*版本: MVP v0.2*  
*日期: 2026-07-05*  
*创建者: 阿龙（总策划师）*
