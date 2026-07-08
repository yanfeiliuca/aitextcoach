# Render.com 环境变量配置步骤

## 1. 登录 Render
打开 https://dashboard.render.com

## 2. 找到你的项目
点击你的 Web Service（aitextcoach）

## 3. 进入 Environment 标签页
左侧菜单 → Environment

## 4. 添加环境变量
点击 "Add Environment Variable" 按钮

添加以下变量：

| Key | Value |
|-----|-------|
| GOOGLE_API_KEY | 你的 Gemini API Key |
| PAYPAL_CLIENT_SECRET | 你的 PayPal 真实 Secret |

注意：
- PAYPAL_CLIENT_ID 和 PAYPAL_PLAN_ID 已经在 render.yaml 里了，不需要手动添加
- 但 PAYPAL_CLIENT_SECRET 必须手动添加（因为 render.yaml 里写的是 sync: false）

## 5. 重新部署
添加完变量后，点击页面顶部的 "Manual Deploy" → "Deploy latest commit"

## 6. 等待部署完成
大约 1-2 分钟

## 7. 测试
打开网站 → 点击 "Upgrade to Pro" → 应该能看到 PayPal 支付按钮
