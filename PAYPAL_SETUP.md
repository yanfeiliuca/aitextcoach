# PayPal 集成设置指南（Cloudflare 版）

> 迁移自 Render 版本的 `PAYPAL_SETUP.md`，PayPal API 调用步骤不变，仅第四步的环境变量配置方式改为 Cloudflare。

## 第一步：创建 PayPal 开发者账号

1. 访问 https://developer.paypal.com
2. 用你的 PayPal 账号登录（没有就注册一个）
3. 进入 Dashboard → My Apps & Credentials

## 第二步：创建 App 获取凭证

1. 在 Sandbox 模式下，点击 "Create App"
2. App Name: `aitextcoach`
3. 复制 **Client ID** 和 **Secret**

当前生产环境使用的 Client ID（已硬编码在 `src/index.ts` 的 `handleConfig` 中，非 sandbox）：
```
AdtYR0zkWzQfqViuiRqDPao6Dp1nwr-nXNNcBG3scWj0BFr3_zUTc-1IsGf95NqDb2gLaD8S20LLaFBl
```

## 第三步：创建订阅计划

在终端执行（替换 `YOUR_CLIENT_ID` 和 `YOUR_SECRET`）：

```bash
# 1. 获取 Access Token
curl -v https://api.sandbox.paypal.com/v1/oauth2/token \
  -H "Accept: application/json" \
  -H "Accept-Language: en_US" \
  -u "YOUR_CLIENT_ID:YOUR_SECRET" \
  -d "grant_type=client_credentials"

# 保存返回的 access_token

# 2. 创建产品
curl -v -X POST https://api.sandbox.paypal.com/v1/catalogs/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "AI Text Coach Pro",
    "description": "Unlimited AI text humanization",
    "type": "SERVICE",
    "category": "SOFTWARE",
    "image_url": "https://aitextcoach.com/logo.png",
    "home_url": "https://aitextcoach.com"
  }'

# 保存返回的 product id (e.g., PROD-XXXXXXXX)

# 3. 创建订阅计划
curl -v -X POST https://api.sandbox.paypal.com/v1/billing/plans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "product_id": "YOUR_PRODUCT_ID",
    "name": "Pro Monthly",
    "description": "Unlimited access to all writing styles",
    "status": "ACTIVE",
    "billing_cycles": [
      {
        "frequency": {
          "interval_unit": "MONTH",
          "interval_count": 1
        },
        "tenure_type": "REGULAR",
        "sequence": 1,
        "total_cycles": 0,
        "pricing_scheme": {
          "fixed_price": {
            "value": "9.99",
            "currency_code": "USD"
          }
        }
      }
    ],
    "payment_preferences": {
      "auto_bill_outstanding": true,
      "setup_fee_failure_action": "CONTINUE",
      "payment_failure_threshold": 3
    }
  }'

# 保存返回的 plan id (e.g., P-XXXXXXXX)
```

## 第四步：配置到 Cloudflare（关键差异）

Render 版本用平台环境变量 + 本地 `.env` 文件；Cloudflare 版本没有 `.env`，配置拆成两处：

**A. `wrangler.toml` 的 `[vars]`（明文，可提交到 git）：**

```toml
[vars]
PAYPAL_MODE = "sandbox"       # 测试用，正式上线后改为 "live"
PAYPAL_PLAN_ID = "P-7SB75295DK0602635NJFH34Q"
```

修改后需要重新部署 Worker（`[vars]` 的变更不会自动生效）：
```bash
npx wrangler deploy
```

**B. Secret（敏感值，不进 git，通过 wrangler CLI 设置）：**

```bash
npx wrangler secret put PAYPAL_CLIENT_SECRET
# 交互式提示中粘贴 Secret，回车确认
```

`PAYPAL_CLIENT_ID` 本项目不走 secret/vars，而是直接硬编码在 `src/index.ts` 的 `handleConfig()` 里（因为它本来就会暴露给前端，不算敏感信息）。切换 sandbox/live 环境时记得同步更新这个硬编码值。

**本地开发**（`npm run dev` / `wrangler dev`）如需用到 secret，可以在项目根目录建 `.dev.vars`（已被 `.gitignore` 忽略）：
```bash
DS_API_KEY=你的DeepSeek Key
PAYPAL_CLIENT_SECRET=你的PayPal Secret
```

## 第五步：测试支付流程

1. 启动本地开发环境：`npm run dev`
2. 用浏览器打开 `public/index.html`（或部署到 Pages 预览环境）
3. 点击 "Upgrade to Pro"
4. 使用 PayPal 沙盒测试账号登录支付

### 沙盒测试账号获取

在 https://developer.paypal.com → Sandbox → Accounts 查看或创建测试买家账号。

## 上线前检查清单

- [ ] Sandbox 支付测试通过
- [ ] 支付后 Pro 功能正常解锁（`users.is_pro` 在 D1 中被置 1）
- [ ] 免费额度限制正常工作（`src/index.ts` 中 `FREE_LIMIT`）
- [ ] `wrangler.toml` 中 `PAYPAL_MODE` 改为 `"live"` 并重新 `wrangler deploy`
- [ ] `src/index.ts` 中硬编码的 `PAYPAL_CLIENT_ID` 换成 live 环境的 Client ID
- [ ] `PAYPAL_CLIENT_SECRET`（wrangler secret）换成 live 环境的 Secret
- [ ] 确认 `PAYPAL_PLAN_ID` 是 live 环境创建的 Plan

---

*原始文档创建于 2026-07-05（Render 版本），迁移适配于 aitextcoach-cf。*
