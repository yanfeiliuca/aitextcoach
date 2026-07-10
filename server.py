#!/usr/bin/env python3
"""
AI Text Coach - Production Server with DeepSeek, PayPal, Quota & PostgreSQL
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
from urllib.parse import urlparse, parse_qs

# ============ DATABASE CONFIG ============
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_DB = bool(DATABASE_URL)

def get_db_conn():
    """Get a PostgreSQL connection"""
    if not USE_DB:
        return None
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    """Initialize database tables on startup"""
    if not USE_DB:
        return
    conn = get_db_conn()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    is_pro BOOLEAN DEFAULT FALSE,
                    subscription_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255),
                    chars_used INTEGER DEFAULT 0,
                    usage_date DATE DEFAULT CURRENT_DATE,
                    UNIQUE(email, usage_date)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS click_stats (
                    id SERIAL PRIMARY KEY,
                    button_type VARCHAR(50) NOT NULL,
                    click_date DATE DEFAULT CURRENT_DATE,
                    count INTEGER DEFAULT 1,
                    UNIQUE(button_type, click_date)
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"DB init warning: {e}")
    finally:
        conn.close()

init_db()

# ============ DATA ACCESS (DB-first, fallback to JSON) ============
PRO_USERS_FILE = "pro_users.json"

def _json_load_pro():
    if os.path.exists(PRO_USERS_FILE):
        try:
            with open(PRO_USERS_FILE, 'r') as f:
                return set(json.load(f).get('pro_users', []))
        except:
            return set()
    return set()

def _json_save_pro(users):
    try:
        with open(PRO_USERS_FILE, 'w') as f:
            json.dump({'pro_users': list(users)}, f)
    except:
        pass

# In-memory fallback
_mem_pro_users = _json_load_pro()
_mem_usage = {}
_mem_clicks = {}

# === User / Pro ===
def is_pro_user(email):
    """Check if email is Pro (DB or JSON)"""
    if not email:
        return False
    email = email.lower().strip()
    if USE_DB:
        conn = get_db_conn()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT is_pro FROM users WHERE email = %s", (email,))
                    row = cur.fetchone()
                    return row[0] if row else False
            finally:
                conn.close()
    return email in _mem_pro_users

def add_pro_user(email, subscription_id=None):
    """Add a Pro user (DB or JSON)"""
    email = email.lower().strip()
    if USE_DB:
        conn = get_db_conn()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (email, is_pro, subscription_id)
                        VALUES (%s, TRUE, %s)
                        ON CONFLICT (email) DO UPDATE
                        SET is_pro = TRUE, subscription_id = COALESCE(EXCLUDED.subscription_id, users.subscription_id)
                    """, (email, subscription_id))
                    conn.commit()
            finally:
                conn.close()
            return
    _mem_pro_users.add(email)
    _json_save_pro(_mem_pro_users)

# === Usage ===
def get_today_usage(email):
    """Get today's character usage"""
    today = time.strftime("%Y-%m-%d")
    if USE_DB and email:
        conn = get_db_conn()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT chars_used FROM usage_stats WHERE email = %s AND usage_date = %s", (email.lower(), today))
                    row = cur.fetchone()
                    return row[0] if row else 0
            finally:
                conn.close()
    key = f"{email}:{today}" if email else f"anon:{today}"
    return _mem_usage.get(key, 0)

def add_usage(email, chars):
    """Add characters to today's usage"""
    today = time.strftime("%Y-%m-%d")
    if USE_DB and email:
        conn = get_db_conn()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO usage_stats (email, chars_used, usage_date)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (email, usage_date) DO UPDATE
                        SET chars_used = usage_stats.chars_used + EXCLUDED.chars_used
                    """, (email.lower(), chars, today))
                    conn.commit()
            finally:
                conn.close()
            return
    key = f"{email}:{today}" if email else f"anon:{today}"
    _mem_usage[key] = _mem_usage.get(key, 0) + chars

# === Clicks ===
def track_click(button):
    """Track a button click"""
    today = time.strftime("%Y-%m-%d")
    if USE_DB:
        conn = get_db_conn()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO click_stats (button_type, click_date, count)
                        VALUES (%s, %s, 1)
                        ON CONFLICT (button_type, click_date) DO UPDATE
                        SET count = click_stats.count + 1
                    """, (button, today))
                    conn.commit()
            finally:
                conn.close()
            return
    if today not in _mem_clicks:
        _mem_clicks[today] = {}
    _mem_clicks[today][button] = _mem_clicks[today].get(button, 0) + 1

def get_stats():
    """Return stats dict for dashboard"""
    today = time.strftime("%Y-%m-%d")
    if USE_DB:
        conn = get_db_conn()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT button_type, count FROM click_stats WHERE click_date = %s", (today,))
                    today_stats = {r[0]: r[1] for r in cur.fetchall()}
                    cur.execute("SELECT button_type, SUM(count) FROM click_stats GROUP BY button_type")
                    total = {r[0]: r[1] for r in cur.fetchall()}
                    cur.execute("SELECT click_date, button_type, count FROM click_stats ORDER BY click_date DESC")
                    breakdown = {}
                    for r in cur.fetchall():
                        d = str(r[0])
                        if d not in breakdown:
                            breakdown[d] = {}
                        breakdown[d][r[1]] = r[2]
                    return today_stats, total, breakdown
            finally:
                conn.close()
    t = _mem_clicks.get(today, {})
    total = {}
    for d in _mem_clicks.values():
        for k, v in d.items():
            total[k] = total.get(k, 0) + v
    return t, total, _mem_clicks

# ============ BUDGET CONTROL ============
BUDGET_FILE = "budget.json"
MONTHLY_BUDGET = 10.00        # USD
BUDGET_SOFT_LIMIT = 7.50      # Start limiting
BUDGET_HARD_LIMIT = 9.50      # Extreme limiting
BUDGET_STOP_LIMIT = 10.00     # Stop completely

# DeepSeek pricing (per 1M tokens) - DeepSeek V4 Flash approx
DS_PRICE_INPUT = 0.07         # $0.07 per 1M input tokens
DS_PRICE_OUTPUT = 0.30        # $0.30 per 1M output tokens

def load_budget():
    """Load current month's spending"""
    if os.path.exists(BUDGET_FILE):
        try:
            with open(BUDGET_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"month": time.strftime("%Y-%m"), "spent": 0.0, "calls": 0}

def save_budget(budget):
    try:
        with open(BUDGET_FILE, 'w') as f:
            json.dump(budget, f, indent=2)
    except:
        pass

def check_budget():
    """Check current budget status. Returns (allowed, mode, spent, message)"""
    budget = load_budget()
    current_month = time.strftime("%Y-%m")
    
    # Reset if new month
    if budget.get("month") != current_month:
        budget = {"month": current_month, "spent": 0.0, "calls": 0}
        save_budget(budget)
    
    spent = budget.get("spent", 0)
    
    if spent >= BUDGET_STOP_LIMIT:
        return False, "stopped", spent, f"Monthly budget exhausted (${spent:.2f}/${BUDGET_STOP_LIMIT:.2f}). Service temporarily unavailable."
    
    if spent >= BUDGET_HARD_LIMIT:
        return True, "extreme_limit", spent, "limited"
    
    if spent >= BUDGET_SOFT_LIMIT:
        return True, "limited", spent, "limited"
    
    return True, "normal", spent, "normal"

def record_cost(input_tokens, output_tokens):
    """Record API call cost and return updated spending"""
    budget = load_budget()
    current_month = time.strftime("%Y-%m")
    
    if budget.get("month") != current_month:
        budget = {"month": current_month, "spent": 0.0, "calls": 0}
    
    cost = (input_tokens / 1_000_000) * DS_PRICE_INPUT + (output_tokens / 1_000_000) * DS_PRICE_OUTPUT
    budget["spent"] = budget.get("spent", 0) + cost
    budget["calls"] = budget.get("calls", 0) + 1
    save_budget(budget)
    return budget["spent"]

def estimate_tokens(text):
    """Rough token estimation (1 token ≈ 4 chars for English)"""
    return max(1, len(text) // 4)

# ============ API KEYS ============
DS_API_KEY = os.environ.get("DS_API_KEY", os.environ.get("DEEPSEEK_API_KEY", ""))
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox")
PAYPAL_PLAN_ID = os.environ.get("PAYPAL_PLAN_ID", "")

PAYPAL_API = "https://api.paypal.com" if PAYPAL_MODE == "live" else "https://api.sandbox.paypal.com"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

FREE_DAILY_LIMIT = 5000

ALL_STYLES_FREE = ["academic", "business", "creative", "casual", "concise"]
FREE_STYLES = ["casual", "concise"]

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


def call_deepseek(text, style, budget_mode="normal"):
    """Call DeepSeek API with budget-aware settings"""
    prompt = PROMPTS.get(style, PROMPTS["casual"]).replace("{input}", text)
    
    # Budget-aware model selection
    model = "deepseek-chat"  # Default: DeepSeek V3 (fast, cheap)
    max_tokens = 2048
    
    if budget_mode == "extreme_limit":
        # Reduce output to save costs
        max_tokens = 1024
    
    data = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional writing assistant. Rewrite text according to the user's instructions. Keep the original meaning. Do not add disclaimers or explanations."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()
    
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {DS_API_KEY}'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            output = result['choices'][0]['message']['content'].strip()
            usage = result.get('usage', {})
            input_tokens = usage.get('prompt_tokens', estimate_tokens(prompt))
            output_tokens = usage.get('completion_tokens', estimate_tokens(output))
            
            # Record cost
            spent = record_cost(input_tokens, output_tokens)
            
            return output, spent
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"API Error ({e.code}): {error_body}")
    except Exception as e:
        raise Exception(f"Failed to call DeepSeek: {str(e)}")


def get_client_ip(headers):
    forwarded = headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    real_ip = headers.get('X-Real-Ip', '')
    if real_ip:
        return real_ip
    return 'anonymous'


def verify_paypal_subscription(subscription_id):
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        return False, "PayPal credentials not configured"
    import base64
    creds = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    req = urllib.request.Request(
        f"{PAYPAL_API}/v1/oauth2/token",
        data="grant_type=client_credentials".encode(),
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            token = json.loads(resp.read().decode()).get("access_token")
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
            self.send_json({
                "paypal_client_id": PAYPAL_CLIENT_ID,
                "paypal_plan_id": PAYPAL_PLAN_ID,
                "paypal_mode": PAYPAL_MODE,
                "free_styles": FREE_STYLES,
                "all_styles": ALL_STYLES_FREE,
                "free_daily_limit": FREE_DAILY_LIMIT
            })
        elif self.path == '/api/stats':
            today_stats, total, breakdown = get_stats()
            # Also include budget info
            _, budget_mode, spent, _ = check_budget()
            self.send_json({
                "today": today_stats,
                "total": total,
                "daily_breakdown": breakdown,
                "budget": {
                    "spent": round(spent, 4),
                    "limit": MONTHLY_BUDGET,
                    "mode": budget_mode
                }
            })
        elif self.path.startswith('/api/check-pro'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            email = params.get('email', [''])[0].strip().lower()
            if not email:
                self.send_json({'is_pro': False, 'error': 'Email required'})
                return
            self.send_json({
                'email': email,
                'is_pro': is_pro_user(email)
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
            ip = get_client_ip(self.headers)

            if not text:
                self.send_json({'error': 'Text is required'}, 400)
                return
            if style not in PROMPTS:
                self.send_json({'error': 'Valid style is required'}, 400)
                return

            # === BUDGET CHECK ===
            allowed, budget_mode, spent, budget_msg = check_budget()
            if not allowed:
                self.send_json({
                    'error': budget_msg,
                    'code': 'BUDGET_EXHAUSTED',
                    'budget_spent': round(spent, 2),
                    'budget_limit': MONTHLY_BUDGET
                }, 503)
                return

            is_pro = is_pro_user(email)
            text_len = len(text)

            if not is_pro:
                used = get_today_usage(email)
                if used + text_len > FREE_DAILY_LIMIT:
                    remaining = max(0, FREE_DAILY_LIMIT - used)
                    self.send_json({
                        'error': 'Daily free limit reached (5000 characters). Upgrade to Pro for unlimited access.',
                        'code': 'QUOTA_EXCEEDED',
                        'remaining': remaining,
                        'is_pro': False
                    }, 403)
                    return
                if style not in FREE_STYLES:
                    self.send_json({
                        'error': f'"{style}" style is Pro-only. Free users can use: Casual and Concise. Upgrade to Pro for all 5 styles.',
                        'code': 'PRO_REQUIRED',
                        'is_pro': False
                    }, 403)
                    return
                add_usage(email, text_len)
                remaining = FREE_DAILY_LIMIT - (used + text_len)
            else:
                remaining = -1

            # === BUDGET MODE LIMITS ===
            if budget_mode == "extreme_limit" and not is_pro:
                # In extreme limit mode, only serve Pro users
                self.send_json({
                    'error': 'Service temporarily limited due to high demand. Pro users still have full access.',
                    'code': 'BUDGET_LIMIT',
                    'budget_spent': round(spent, 2),
                    'is_pro': False
                }, 503)
                return

            result, new_spent = call_deepseek(text, style, budget_mode)
            
            self.send_json({
                'result': result,
                'remaining': remaining,
                'is_pro': is_pro,
                'budget_spent': round(new_spent, 4)
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_activate_pro(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            email = data.get('email', '').strip().lower()
            subscription_id = data.get('subscription_id', '')
            if not email:
                self.send_json({'error': 'Email is required'}, 400)
                return
            if PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET and subscription_id:
                is_valid, status = verify_paypal_subscription(subscription_id)
                if not is_valid:
                    self.send_json({'error': f'PayPal verification failed: {status}'}, 400)
                    return
            add_pro_user(email, subscription_id)
            self.send_json({
                'success': True,
                'email': email,
                'is_pro': True,
                'message': 'Pro activated! Refresh the page to unlock all features.'
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_debug_add_pro(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            email = data.get('email', '').strip().lower()
            token = data.get('token', '')
            if not email:
                self.send_json({'error': 'Email is required'}, 400)
                return
            if token != 'aitextcoach_debug_2024':
                self.send_json({'error': 'Invalid token'}, 403)
                return
            add_pro_user(email, 'debug')
            self.send_json({
                'success': True,
                'email': email,
                'is_pro': True,
                'message': f'{email} added as Pro user for testing.'
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_track_click(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            button = data.get('button', '')
            track_click(button)
            self.send_json({'success': True, 'button': button})
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
    
    # Check budget on startup
    allowed, mode, spent, msg = check_budget()
    budget_status = "✅ Normal" if mode == "normal" else ("⚠️ Limited" if mode == "limited" else ("🔴 Extreme" if mode == "extreme_limit" else "🚫 Stopped"))
    
    print(f"🚀 AI Text Coach running at http://localhost:{port}")
    print(f"💳 PayPal Mode: {PAYPAL_MODE}")
    print(f"🗄️  Database: {'PostgreSQL' if USE_DB else 'JSON (fallback)'}")
    print(f"🧠 AI: DeepSeek Chat (via OpenAI-compatible API)")
    print(f"💰 Budget: ${spent:.2f}/${MONTHLY_BUDGET:.2f} — {budget_status}")
    print(f"   Soft: ${BUDGET_SOFT_LIMIT}, Hard: ${BUDGET_HARD_LIMIT}, Stop: ${BUDGET_STOP_LIMIT}")
    print("⏹️  Press Ctrl+C to stop")
    
    if not DS_API_KEY:
        print("\n⚠️  WARNING: DS_API_KEY not set! Text enhancement will fail.")
    
    try:
        server = HTTPServer(('0.0.0.0', port), APIHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)


if __name__ == '__main__':
    run_server()
