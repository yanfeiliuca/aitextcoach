#!/usr/bin/env python3
"""
AI Text Coach - Production Server with PayPal & Quota
Compatible with Render.com free tier
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============ CONFIG ============
API_KEY = os.environ.get("GOOGLE_API_KEY", "")
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox")
PAYPAL_PLAN_ID = os.environ.get("PAYPAL_PLAN_ID", "")

PAYPAL_API = "https://api.paypal.com" if PAYPAL_MODE == "live" else "https://api.sandbox.paypal.com"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# ============ PERSISTENCE ============
PRO_USERS_FILE = "pro_users.json"

def load_pro_users():
    """Load Pro users from JSON file"""
    if os.path.exists(PRO_USERS_FILE):
        try:
            with open(PRO_USERS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('pro_users', []))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()

def save_pro_users(users):
    """Save Pro users to JSON file"""
    try:
        with open(PRO_USERS_FILE, 'w') as f:
            json.dump({'pro_users': list(users)}, f)
    except IOError:
        pass

# MVP: Persistent Pro users (survives restarts)
pro_users = load_pro_users()

# MVP: In-memory storage (resets on deploy/restart — acceptable for early stage)
usage_today = {}           # ip_or_email -> chars_used_today
FREE_DAILY_LIMIT = 5000    # chars per day

# Click tracking (MVP: in-memory, resets on restart)
# Format: { "YYYY-MM-DD": { "enhance": N, "upgrade": N } }
click_stats = {}

# ============ PROMPTS ============
PROMPTS = {
    "academic": """Rewrite the following text in an academic style suitable for college essays and research papers.
- Use formal, precise vocabulary
- Maintain an objective, analytical tone
- Use passive voice where appropriate for formality
- Avoid contractions and colloquialisms entirely
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "business": """Rewrite the following text in a professional business style suitable for emails, reports, and proposals.
- Use clear, action-oriented language
- Keep sentences concise and direct
- Use active voice for stronger statements
- Maintain a professional but approachable tone
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "creative": """Rewrite the following text in a creative, engaging style suitable for blogs, stories, and marketing copy.
- Use vivid imagery and sensory details, but keep it grounded
- Vary sentence length for rhythm and flow
- Include emotional resonance
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "casual": """Rewrite the following text in a casual, conversational style suitable for social media and personal communication.
- Use everyday language and natural phrasing
- Include contractions and colloquial expressions
- Write as if talking to a friend over coffee
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "concise": """Rewrite the following text to be SIGNIFICANTLY more concise and direct.
- CUT at least 40% of the words
- Remove ALL redundant words and phrases
- Use stronger, more specific verbs
- Cut filler words (very, really, basically, actually, etc.)
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note"
- Do NOT add new information or facts

Text: {input}""",
}

ALL_STYLES_FREE = ["academic", "business", "creative", "casual", "concise"]
FREE_STYLES = ["casual", "concise"]


def call_gemini(text, style):
    prompt = PROMPTS.get(style, PROMPTS["casual"]).replace("{input}", text)
    data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(GEMINI_URL, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except urllib.error.HTTPError as e:
        raise Exception(f"API Error: {e.read().decode()}")
    except Exception as e:
        raise Exception(f"Failed to call Gemini: {str(e)}")


def get_client_ip(headers):
    """Extract client IP from headers (best effort)"""
    forwarded = headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    real_ip = headers.get('X-Real-Ip', '')
    if real_ip:
        return real_ip
    return 'anonymous'


def check_quota(email, ip, text_length):
    """Check if user can use the service. Returns (allowed, remaining, is_pro)"""
    # Pro users always allowed
    if email and email.lower() in pro_users:
        return (True, -1, True)
    
    # Use email as key if provided, otherwise IP
    key = email.lower() if email else ip
    today = time.strftime("%Y-%m-%d")
    usage_key = f"{key}:{today}"
    
    used = usage_today.get(usage_key, 0)
    if used + text_length > FREE_DAILY_LIMIT:
        remaining = max(0, FREE_DAILY_LIMIT - used)
        return (False, remaining, False)
    
    usage_today[usage_key] = used + text_length
    remaining = FREE_DAILY_LIMIT - usage_today[usage_key]
    return (True, remaining, False)


def verify_paypal_subscription(subscription_id):
    """Verify subscription with PayPal API (MVP: basic token auth)"""
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        return False, "PayPal credentials not configured"
    
    # Get access token
    import base64
    creds = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    token_data = "grant_type=client_credentials"
    req = urllib.request.Request(
        f"{PAYPAL_API}/v1/oauth2/token",
        data=token_data.encode(),
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            token = json.loads(resp.read().decode()).get("access_token")
        
        # Verify subscription
        req2 = urllib.request.Request(
            f"{PAYPAL_API}/v1/billing/subscriptions/{subscription_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req2, timeout=15) as resp:
            sub = json.loads(resp.read().decode())
            status = sub.get("status", "")
            return status in ["ACTIVE", "APPROVED"], status
    except Exception as e:
        return False, str(e)


# ============ HTTP HANDLER ============

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
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif self.path == '/index-ab-test.html':
            self.serve_file('index-ab-test.html', 'text/html')
        elif self.path == '/blog' or self.path == '/blog/':
            self.serve_file('blog/index.html', 'text/html')
        elif self.path.startswith('/blog/'):
            self.serve_file(self.path.lstrip('/'), 'text/html')
        elif self.path == '/sitemap.xml':
            self.serve_file('sitemap.xml', 'application/xml')
        elif self.path == '/robots.txt':
            self.serve_file('robots.txt', 'text/plain')
        elif self.path == '/api/config':
            # Return public config for frontend
            self.send_json({
                "paypal_client_id": PAYPAL_CLIENT_ID,
                "paypal_plan_id": PAYPAL_PLAN_ID,
                "paypal_mode": PAYPAL_MODE,
                "free_styles": FREE_STYLES,
                "all_styles": ALL_STYLES_FREE,
                "free_daily_limit": FREE_DAILY_LIMIT
            })
        elif self.path == '/api/stats':
            # Simple stats dashboard
            today = time.strftime("%Y-%m-%d")
            today_stats = click_stats.get(today, {"enhance": 0, "upgrade": 0})
            total = {"enhance": 0, "upgrade": 0}
            for day_data in click_stats.values():
                total["enhance"] += day_data.get("enhance", 0)
                total["upgrade"] += day_data.get("upgrade", 0)
            self.send_json({
                "today": today_stats,
                "total": total,
                "daily_breakdown": click_stats
            })
        elif self.path.startswith('/api/check-pro'):
            # Check if an email has Pro status
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            email = params.get('email', [''])[0].strip().lower()
            
            if not email:
                self.send_json({'error': 'Email is required', 'is_pro': False})
                return
            
            is_pro = email in pro_users
            self.send_json({
                'email': email,
                'is_pro': is_pro
            })
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/enhance':
            self.handle_enhance()
        elif self.path == '/api/activate-pro':
            self.handle_activate_pro()
        elif self.path == '/api/debug-add-pro':
            self.handle_debug_add_pro()
        elif self.path == '/api/track-click':
            self.handle_track_click()
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
            ip = get_client_ip(self.headers)
            allowed, remaining, is_pro = check_quota(email, ip, len(text))
            
            if not allowed:
                self.send_json({
                    'error': 'Daily free limit reached (5000 characters). Upgrade to Pro for unlimited access.',
                    'code': 'QUOTA_EXCEEDED',
                    'remaining': remaining,
                    'is_pro': False
                }, 403)
                return
            
            # Free users only get casual + concise
            if not is_pro and style not in FREE_STYLES:
                self.send_json({
                    'error': f'"{style}" style is Pro-only. Free users can use: Casual and Concise. Upgrade to Pro for all 5 styles.',
                    'code': 'PRO_REQUIRED',
                    'is_pro': False
                }, 403)
                return
            
            result = call_gemini(text, style)
            self.send_json({
                'result': result,
                'remaining': remaining,
                'is_pro': is_pro
            })
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_activate_pro(self):
        """Activate Pro after PayPal subscription"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            email = data.get('email', '').strip().lower()
            subscription_id = data.get('subscription_id', '')
            
            if not email:
                self.send_json({'error': 'Email is required'}, 400)
                return
            
            # Verify with PayPal if credentials are set
            if PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET and subscription_id:
                is_valid, status = verify_paypal_subscription(subscription_id)
                if not is_valid:
                    self.send_json({'error': f'PayPal verification failed: {status}'}, 400)
                    return
            
            # Mark as Pro and save
            pro_users.add(email)
            save_pro_users(pro_users)
            self.send_json({
                'success': True,
                'email': email,
                'is_pro': True,
                'message': 'Pro activated! Refresh the page to unlock all features.'
            })
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_debug_add_pro(self):
        """Debug endpoint to manually add a Pro user (for testing only)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            email = data.get('email', '').strip().lower()
            token = data.get('token', '')
            
            if not email:
                self.send_json({'error': 'Email is required'}, 400)
                return
            
            # Simple token check for basic security (change in production)
            if token != 'aitextcoach_debug_2024':
                self.send_json({'error': 'Invalid token'}, 403)
                return
            
            pro_users.add(email)
            save_pro_users(pro_users)
            self.send_json({
                'success': True,
                'email': email,
                'is_pro': True,
                'message': f'{email} added as Pro user for testing. Total Pro users: {len(pro_users)}'
            })
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_track_click(self):
        """Track button clicks for analytics"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            button = data.get('button', '')  # 'enhance' or 'upgrade'
            today = time.strftime("%Y-%m-%d")
            
            if today not in click_stats:
                click_stats[today] = {"enhance": 0, "upgrade": 0}
            
            if button in click_stats[today]:
                click_stats[today][button] += 1
            
            self.send_json({'success': True, 'button': button, 'today': click_stats[today]})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
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
    print(f"🚀 AI Text Coach server running at http://localhost:{port}")
    print(f"💳 PayPal Mode: {PAYPAL_MODE}")
    print(f"📧 Pro users loaded: {len(pro_users)}")
    print("⏹️  Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)


if __name__ == '__main__':
    run_server()
