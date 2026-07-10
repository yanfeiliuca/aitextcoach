#!/bin/bash

PAYPAL_SECRET="${PAYPAL_SECRET:?Set PAYPAL_SECRET in your environment}"

echo "=== 测试 Token 获取 ==="

curl -s https://api.sandbox.paypal.com/v1/oauth2/token \
  -H "Accept: application/json" \
  -H "Accept-Language: en_US" \
  -u "${PAYPAL_CLIENT_ID:?Set PAYPAL_CLIENT_ID in your environment}:${PAYPAL_SECRET}" \
  -d "grant_type=client_credentials" > response.json

echo "完整返回内容："
cat response.json
echo ""
echo ""

# 用 Python 稳健解析（Mac 自带 Python3）
TOKEN=$(python3 -c "
import json, sys
try:
    data = json.load(open('response.json'))
    print(data.get('access_token', 'NOT_FOUND'))
except Exception as e:
    print('JSON_ERROR:', e)
")

echo "提取的 token: ${TOKEN:0:40}..."
