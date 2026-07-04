# 🚀 AI Text Coach - 部署指南

> **目标**：把本地能跑的网站，部署到线上，让全世界都能访问
> **预计时间**：30-45 分钟
> **费用**：免费（Render.com 免费版）

---

## 部署前检查清单

- [ ] 本地测试通过（`./start.sh` 能跑，浏览器能打开）
- [ ] Gemini API Key 有效（测试过改写功能）
- [ ] 域名 aitextcoach.com 已注册 ✅

---

## 第一步：创建 GitHub 仓库（5分钟）

1. 打开 [github.com](https://github.com) 登录你的账号
2. 点击右上角 **+** → **New repository**
3. 仓库名填：`aitextcoach`
4. **不要**勾选 "Initialize this repository with a README"
5. **不要**勾选 "Add .gitignore"
6. 点击 **Create repository**

### 推送代码到 GitHub

在终端执行以下命令（复制粘贴）：

```bash
cd ~/Desktop/aitextcoach
git remote add origin https://github.com/你的用户名/aitextcoach.git
git branch -M main
git push -u origin main
```

**如果遇到密码问题**：GitHub 不再支持密码，需要用 **Personal Access Token**。
- 去 GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- 生成一个 Token，复制，粘贴到密码框

---

## 第二步：注册 Render.com（5分钟）

1. 打开 [render.com](https://render.com)
2. 点击 **Get Started for Free**
3. 选择 **Continue with GitHub**
4. 授权 Render 访问你的 GitHub 仓库

---

## 第三步：创建 Web Service（10分钟）

1. Render 控制台点击 **New +** → **Web Service**
2. 选择你的 `aitextcoach` 仓库
3. 配置：
   - **Name**: `aitextcoach`
   - **Runtime**: Python 3
   - **Build Command**: 留空（或填 `pip install -r requirements.txt`）
   - **Start Command**: `python server.py`
4. 点击 **Create Web Service**

### 设置环境变量（关键！）

1. 在 Render 控制台找到你的服务 → **Environment** 标签
2. 点击 **Add Environment Variable**
3. Key: `GOOGLE_API_KEY`
4. Value: 你的 Gemini API Key（`AIzaSyDFdDJ4OkP6P9SmaFufkITGUBMH_r4B7O0`）
5. 点击 **Save**

**为什么这样做？**
- API Key 放在环境变量里，不会暴露在代码中
- 即使有人看你的 GitHub 代码，也看不到 Key

---

## 第四步：部署完成（5分钟）

1. Render 会自动从 GitHub 拉代码、部署
2. 等待状态变成 **Live**（绿色）
3. 你会得到一个网址：`https://aitextcoach.onrender.com`
4. 打开网址测试！

---

## 第五步：绑定域名（10分钟）

1. Render 控制台 → 你的服务 → **Settings** → **Custom Domains**
2. 点击 **Add Custom Domain**
3. 输入：`aitextcoach.com`
4. Render 会给你一个 **CNAME 记录**
5. 去你的域名注册商（Namecheap/Cloudflare）
6. 在 DNS 设置里添加 CNAME：
   - Host: `@` 或 `www`
   - Value: Render 给你的 CNAME 地址
7. 等待 DNS 生效（通常几分钟到几小时）
8. 测试：`https://aitextcoach.com`

---

## 部署后验证清单

- [ ] 访问 `https://aitextcoach.com` 能看到首页
- [ ] 粘贴文本，选择风格，点击 Enhance
- [ ] 能看到改写结果
- [ ] Before/After 对比正常
- [ ] 评分显示正常

---

## 如果出问题

### 问题1：部署失败，日志显示 "GOOGLE_API_KEY not set"
**解决**：检查环境变量是否设置正确，Key 有没有错别字

### 问题2：网站打开但 API 报错
**解决**：检查 Render 日志，可能是 API Key 配额用完了

### 问题3：域名绑定不生效
**解决**：DNS 生效需要时间，等 1-2 小时再试。检查 CNAME 是否配置正确

### 问题4：改写结果和本地不一样
**解决**：正常。线上用的是相同代码，但网络延迟可能导致体验略有不同

---

## 下一步（部署后）

1. **SEO 内容生产**（小笔）
   - 写 10 篇博客文章
   - 发布到网站

2. **Product Hunt 发布**（龙哥）
   - 准备发布材料
   - 选个好日子上线

3. **收集用户反馈**
   - 让朋友试用
   - 记录 bug 和改进建议

---

**橘子，按这个清单一步一步来。有任何问题随时喊我。** 🐉
