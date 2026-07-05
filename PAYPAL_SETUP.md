# PayPal 集成设置指南

## 第一步：创建 PayPal 开发者账号

1. 访问 https://developer.paypal.com
2. 用你的 PayPal 账号登录（没有就注册一个）
3. 进入 Dashboard → My Apps & Credentials

## 第二步：创建 App 获取凭证

1. 在 Sandbox 模式下，点击 "Create App"
2. App Name: `aitextcoach`
3. 复制 **Client ID** 和 **Secret**

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

## 第四步：配置环境变量

在 Render.com 或其他部署平台添加：

```
PAYPAL_CLIENT_ID=你的Client ID
PAYPAL_CLIENT_SECRET=你的Secret
PAYPAL_MODE=sandbox      # 测试用，正式上线后改为 live
PAYPAL_PLAN_ID=你的Plan ID
```

本地测试时创建 `.env` 文件：

```bash
cat > .env << 'EOF'
GOOGLE_API_KEY=你的Gemini API Key
PAYPAL_CLIENT_ID=你的PayPal Client ID
PAYPAL_CLIENT_SECRET=你的PayPal Secret
PAYPAL_MODE=sandbox
PAYPAL_PLAN_ID=你的Plan ID
EOF
```

## 第五步：测试支付流程

1. 启动服务器：`python server.py`
2. 打开 http://localhost:3000
3. 点击 "Pay with PayPal"
4. 使用 PayPal 沙盒测试账号登录支付

### 沙盒测试账号获取

在 https://developer.paypal.com → Sandbox → Accounts 查看或创建测试买家账号。

## 上线前检查清单

- [ ] Sandbox 支付测试通过
- [ ] 支付后 Pro 功能正常解锁
- [ ] 免费额度限制正常工作
- [ ] 把 `PAYPAL_MODE` 改为 `live`
- [ ] 把 PayPal API 切换到 live 环境的 Client ID 和 Secret
- [ ] 确认 Plan ID 是 live 环境的

---

*创建于 2026-07-05*
