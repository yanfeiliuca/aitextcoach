# AI Text Coach

> **域名**: aitextcoach.com (已注册)  
> **品牌**: AI Text Coach — Make Your AI Writing Sound Human  
> **核心功能**: 将AI生成的文本改写成更自然、更像人类写作的风格

---

## 文件结构

```
aitextcoach/
├── index.html      ← 网站前端（纯HTML + Tailwind CDN）
├── server.py       ← API后端（纯Python，零依赖）
├── start.sh        ← 一键启动脚本
└── README.md       ← 本文档
```

---

## 启动方法

### 方法一：双击启动（推荐）

1. 打开终端
2. 输入以下命令：
   ```bash
   cd ~/Desktop/aitextcoach
   ./start.sh
   ```
3. 浏览器会自动打开 `http://localhost:3000`

### 方法二：手动启动

```bash
cd ~/Desktop/aitextcoach
python3 server.py
```

---

## 使用说明

### 本地测试

1. 启动服务器（见上方）
2. 浏览器打开 `http://localhost:3000`
3. 在文本框粘贴AI生成的文本
4. 选择写作风格（Academic / Business / Creative / Casual / Concise）
5. 点击 "Enhance My Text"
6. 查看 Before/After 对比和质量评分

### 部署到线上（Vercel）

**第一步：创建 GitHub 仓库**

1. 去 [github.com](https://github.com) 登录
2. 创建新仓库，命名为 `aitextcoach`
3. 不要初始化（不要选 README、.gitignore）

**第二步：推送代码**

```bash
cd ~/Desktop/aitextcoach
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/aitextcoach.git
git push -u origin main
```

**第三步：部署到 Vercel**

1. 去 [vercel.com](https://vercel.com) 登录（用 GitHub 账号）
2. 点击 "New Project"
3. 选择 `aitextcoach` 仓库
4. 框架选择 "Other"
5. 构建命令留空
6. 输出目录留空
7. 环境变量添加：`GOOGLE_API_KEY` = 你的 Gemini API Key
8. 点击 Deploy

**注意**: Vercel 的免费版不支持 Python 后端。需要改用 Node.js 版本或 Vercel Serverless Function。

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

## 技术栈

| 层级 | 技术 | 理由 |
|------|------|------|
| 前端 | HTML + Tailwind CSS CDN | 零构建、零依赖、浏览器直接跑 |
| 后端 | Python 3 + 内置 http.server | 零外部依赖、Mac自带 |
| AI | Gemini 2.5 Flash | 快速、免费额度大、质量好 |
| 部署 | Vercel / 自有服务器 | 待配置 |

---

## 免费版 vs Pro版

| 功能 | 免费版 | Pro版 ($9.99/月) |
|------|--------|-----------------|
| 每日字数 | 500字 | 无限 |
| 风格数量 | 2种 | 8种 |
| 语气调整 | ❌ | ✅ |
| 导出格式 | 复制文本 | Word/PDF |
| 历史记录 | ❌ | ✅ |
| 批量处理 | ❌ | ✅ |

---

## 下一步（阿龙执行）

- [ ] 部署到 Vercel 或自有服务器
- [ ] 配置 Stripe 支付
- [ ] 添加用户登录系统
- [ ] SEO内容生产（小笔）
- [ ] Product Hunt 发布（龙哥）

---

*版本: MVP v0.1*  
*日期: 2026-07-04*  
*创建者: 阿龙（总策划师）*
