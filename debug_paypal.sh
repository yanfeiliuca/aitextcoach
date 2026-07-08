#!/bin/bash

curl -s -w "\nHTTP_CODE:%{http_code}" https://api.sandbox.paypal.com/v1/oauth2/token \
  -H "Accept: application/json" \
  -H "Accept-Language: en_US" \
  -u "AeyMyUFXSCS4qKsiQxrhRblS5k8XeQt8Np9x46:YOUR_SECRET" \
  -d "grant_type=client_credentials" > paypal_response.txt

echo "--- 完整返回 ---"
cat paypal_response.txt
echo ""
