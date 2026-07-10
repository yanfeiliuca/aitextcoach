#!/bin/bash

curl -s -w "\nHTTP_CODE:%{http_code}" https://api.sandbox.paypal.com/v1/oauth2/token \
  -H "Accept: application/json" \
  -H "Accept-Language: en_US" \
  -u "${PAYPAL_CLIENT_ID:?Set PAYPAL_CLIENT_ID in your environment}:${PAYPAL_SECRET:?Set PAYPAL_SECRET in your environment}" \
  -d "grant_type=client_credentials" > paypal_response.txt

echo "--- 完整返回 ---"
cat paypal_response.txt
echo ""
