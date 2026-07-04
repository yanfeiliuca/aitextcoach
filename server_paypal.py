#!/usr/bin/env python3
"""
AI Text Coach - PayPal Integration (Phase 4)
Minimal viable payment: Email + PayPal subscription
Compatible with Render.com free tier

NOTE: This is PREP code. Deploy ONLY after Phase 1-3 (free users, user system, quota tracking)

REQUIRED ENV VARS:
- GOOGLE_API_KEY (existing)
- PAYPAL_CLIENT_ID
- PAYPAL_CLIENT_SECRET
- PAYPAL_MODE=sandbox (change to 'live' for production)
"""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import base64
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============ CONFIG ============
API_KEY = os.environ.get("GOOGLE_API_KEY", "")
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox")

if PAYPAL_MODE == "live":
    PAYPAL_API = "https://api.paypal.com"
else:
    PAYPAL_API = "https://api.sandbox.paypal.com"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# ============ IN-MEMORY STORE (Render free tier has no persistent DB) ============
# For production, switch to Render PostgreSQL or Supabase
pro_users = {}  # email -> {subscribed_at, expires_at, subscription_id}
usage_quota = {}  # email -> {date, count}  # date = YYYY-MM-DD

# ============ PAYPAL API ============

def get_paypal_token():
    """Get OAuth access token from PayPal"""
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        return None
    
    credentials = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    
    data = "grant_type=client_credentials"
    req = urllib.request.Request(
        f"{PAYPAL_API}/v1/oauth2/token",
        data=data.encode(),
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result.get("access_token")
    except Exception as e:
        print(f"PayPal auth error: {e}")
        return None


def create_subscription_plan():
    """Create a subscription plan (run once manually)"""
    token = get_paypal_token()
    if not token:
        print("No PayPal token. Check credentials.")
        return None
    
    # Step 1: Create product
    product_data = json.dumps({
        "name": "AI Text Coach Pro",
        "description": "Unlimited AI text enhancement",
        "type": "SERVICE",
        "category": "SOFTWARE"
    }).encode()
    
    req = urllib.request.Request(
        f"{PAYPAL_API}/v1/catalogs/products",
        data=product_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            product = json.loads(resp.read().decode())
            product_id = product["id"]
            print(f"Product created: {product_id}")
    except Exception as e:
        print(f"Product creation error: {e}")
        return None
    
    # Step 2: Create plan
    plan_data = json.dumps({
        "product_id": product_id,
        "name": "Pro Monthly",
        "billing_cycles": [{
            "frequency": {"interval_unit": "MONTH", "interval_count": 1},
            "tenure_type": "REGULAR",
            "sequence": 1,
            "total_cycles": 0,  # 0 = infinite
            "pricing_scheme": {"fixed_price": {"value": "9.99", "currency_code": "USD"}}
        }],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        }
    }).encode()
    
    req = urllib.request.Request(
        f"{PAYPAL_API}/v1/billing/plans",
        data=plan_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            plan = json.loads(resp.read().decode())
            plan_id = plan["id"]
            print(f"Plan created: {plan_id}")
            print(f"\n=== IMPORTANT ===")
            print(f"Save this PLAN_ID in your environment: {plan_id}")
            print(f"=================\n")
            return plan_id
    except Exception as e:
        print(f"Plan creation error: {e}")
        return None


# ============ GEMINI API ============

PROMPTS = {
    "academic": """Rewrite the following text in an academic style...
Text: {input}""",
    "business": """Rewrite the following text in a professional business style...
Text: {input}""",
    "creative": """Rewrite the following text in a creative, engaging style...
Text: {input}""",
    "casual": """Rewrite the following text in a casual, conversational style...
Text: {input}""",
    "concise": """Rewrite the following text to be SIGNIFICANTLY more concise...
Text: {input}""",
}


def call_gemini(text, style):
    prompt = PROMPTS.get(style, PROMPTS["casual"]).replace("{input}", text)
    data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(GEMINI_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


# ============ QUOTA SYSTEM ============

def check_quota(email, text_length):
    """Check if user has exceeded daily quota. Returns (is_allowed, remaining)"""
    if not email:
        return (True, 500)  # Anonymous users get full free quota (but we track IP ideally)
    
    # Check if Pro user
    if email in pro_users:
        return (True, -1)  # -1 = unlimited
    
    # Free user: 500 words/day
    today = time.strftime("%Y-%m-%d")
    key = f"{email}:{today}"
    
    if key not in usage_quota:
        usage_quota[key] = 0
    
    # Simple char count as proxy for words
    current = usage_quota[key]
    if current + text_length > 5000:  # 5000 chars ≈ 500 words
        return (False, max(0, 5000 - current))
    
    usage_quota[key] = current + text_length
    return (True, 5000 - usage_quota[key])


# ============ SERVER ============

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        # Serve static files
        if self.path == '/':
            self.serve_file('index.html', 'text/html')
        elif self.path in ['/index.html', '/index-a.html', '/index-b.html']:
            self.serve_file(self.path.lstrip('/'), 'text/html')
        elif self.path == '/api/paypal-config':
            # Return PayPal Client ID for frontend (safe to expose)
            self.send_json({"client_id": PAYPAL_CLIENT_ID, "mode": PAYPAL_MODE})
        elif self.path == '/api/check-pro':
            # Check if email is Pro
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            email = params.get('email', [''])[0]
            is_pro = email in pro_users
            self.send_json({"is_pro": is_pro, "email": email})
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/enhance':
            self.handle_enhance()
        elif self.path == '/api/paypal-webhook':
            self.handle_paypal_webhook()
        elif self.path == '/api/create-subscription':
            self.handle_create_subscription()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_enhance(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            text = data.get('text', '').strip()
            style = data.get('style', 'casual')
            email = data.get('email', '').strip().lower()
            
            if not text:
                self.send_json({'error': 'Text is required'}, 400)
                return
            
            if style not in PROMPTS:
                self.send_json({'error': 'Valid style is required'}, 400)
                return
            
            # Check quota
            is_allowed, remaining = check_quota(email, len(text))
            if not is_allowed:
                self.send_json({
                    'error': 'Daily quota exceeded. Upgrade to Pro for unlimited.',
                    'upgrade_url': '/#pricing',
                    'remaining': remaining
                }, 403)
                return
            
            result = call_gemini(text, style)
            self.send_json({
                'result': result,
                'remaining': remaining if remaining >= 0 else 'unlimited',
                'is_pro': email in pro_users
            })
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_create_subscription(self):
        """Frontend creates subscription via PayPal SDK, then tells us about it"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            email = data.get('email', '').strip().lower()
            subscription_id = data.get('subscription_id', '')
            
            if not email or not subscription_id:
                self.send_json({'error': 'Email and subscription_id required'}, 400)
                return
            
            # Verify with PayPal
            token = get_paypal_token()
            if token:
                req = urllib.request.Request(
                    f"{PAYPAL_API}/v1/billing/subscriptions/{subscription_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        sub = json.loads(resp.read().decode())
                        if sub.get("status") in ["ACTIVE", "APPROVED"]:
                            pro_users[email] = {
                                "subscribed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "subscription_id": subscription_id,
                                "status": sub["status"]
                            }
                            self.send_json({'success': True, 'email': email, 'status': 'pro'})
                            return
                except Exception as e:
                    print(f"PayPal verification error: {e}")
            
            # Fallback: trust frontend for now (MVP only!)
            pro_users[email] = {
                "subscribed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "subscription_id": subscription_id,
                "status": "pending_verification"
            }
            self.send_json({'success': True, 'email': email, 'status': 'pro', 'note': 'Pending PayPal verification'})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_paypal_webhook(self):
        """PayPal sends webhook events here"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        # In production: verify webhook signature
        # For MVP: log and process
        print(f"PayPal Webhook: {body[:500]}")
        
        try:
            data = json.loads(body)
            event_type = data.get("event_type", "")
            
            if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
                resource = data.get("resource", {})
                subscription_id = resource.get("id", "")
                # Find user by subscription_id and mark active
                for email, info in pro_users.items():
                    if info.get("subscription_id") == subscription_id:
                        info["status"] = "ACTIVE"
                        print(f"Subscription activated: {email}")
                        break
            
            elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
                resource = data.get("resource", {})
                subscription_id = resource.get("id", "")
                for email, info in list(pro_users.items()):
                    if info.get("subscription_id") == subscription_id:
                        del pro_users[email]
                        print(f"Subscription cancelled: {email}")
                        break
            
            self.send_json({'received': True})
            
        except Exception as e:
            print(f"Webhook error: {e}")
            self.send_json({'received': True})  # Always return 200 to PayPal
    
    def serve_file(self, filename, content_type):
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def run_server():
    port = int(os.environ.get('PORT', 3000))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🚀 AI Text Coach (PayPal Ready) running at http://localhost:{port}")
    print(f"📁 PayPal Mode: {PAYPAL_MODE}")
    print(f"💳 PayPal API: {PAYPAL_API}")
    if not PAYPAL_CLIENT_ID:
        print(f"⚠️  WARNING: PAYPAL_CLIENT_ID not set. PayPal features disabled.")
    print(f"⏹️  Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)


if __name__ == '__main__':
    # Check if we should create a plan (run once manually)
    if len(sys.argv) > 1 and sys.argv[1] == '--create-plan':
        plan_id = create_subscription_plan()
        if plan_id:
            print(f"\nAdd this to your environment:")
            print(f"PAYPAL_PLAN_ID={plan_id}")
    else:
        run_server()
