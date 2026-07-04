#!/usr/bin/env python3
"""
AI Text Coach - Production Server
Compatible with Render.com, Railway, Heroku, or any Python host
"""

import json
import os
import sys
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

# Read API key from environment variable (secure)
API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not API_KEY:
    print("⚠️  WARNING: GOOGLE_API_KEY not set. API will not work.")
    print("   Set it with: export GOOGLE_API_KEY=your_key_here")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + API_KEY

PROMPTS = {
    "academic": """Rewrite the following text in an academic style suitable for college essays and research papers.
- Use formal, precise vocabulary
- Maintain an objective, analytical tone
- Use passive voice where appropriate for formality
- Include transitional phrases between paragraphs
- Avoid contractions and colloquialisms entirely
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note", "It should be noted"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "business": """Rewrite the following text in a professional business style suitable for emails, reports, and proposals.
- Use clear, action-oriented language
- Keep sentences concise and direct
- Use active voice for stronger statements
- Include specific, measurable outcomes where possible
- Maintain a professional but approachable tone
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note", "It should be noted"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "creative": """Rewrite the following text in a creative, engaging style suitable for blogs, stories, and marketing copy.
- Use vivid imagery and sensory details, but keep it grounded and authentic (avoid purple prose)
- Vary sentence length for rhythm and flow
- Include emotional resonance
- Use "show, don't tell" techniques
- Make the writing memorable but believable
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note", "It should be noted"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "casual": """Rewrite the following text in a casual, conversational style suitable for social media, personal blogs, and friendly communication.
- Use everyday language and natural phrasing
- Include contractions and colloquial expressions where appropriate
- Write as if talking to a friend over coffee
- Keep it relaxed, approachable, and authentic
- Use humor or personal touches where natural
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note", "It should be noted"
- Keep the original meaning intact
- Do NOT add new information or facts

Text: {input}""",

    "concise": """Rewrite the following text to be SIGNIFICANTLY more concise and direct.
- CUT at least 40% of the words
- Remove ALL redundant words and phrases
- Use stronger, more specific verbs
- Cut filler words (very, really, basically, actually, etc.)
- Keep only essential information and key points
- Aim for maximum clarity with minimum word count
- AVOID: "Furthermore", "Moreover", "Additionally", "In conclusion", "It is important to note", "It should be noted"
- Do NOT add new information or facts

Text: {input}""",
}


def call_gemini(text, style):
    """Call Gemini API directly using urllib"""
    prompt = PROMPTS.get(style, PROMPTS["concise"]).replace("{input}", text)
    
    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode('utf-8')
    
    req = urllib.request.Request(
        GEMINI_URL,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"API Error: {error_body}")
    except Exception as e:
        raise Exception(f"Failed to call Gemini: {str(e)}")


class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html', 'text/html')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        if self.path == '/api/enhance':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)
                
                text = data.get('text', '').strip()
                style = data.get('style', 'casual')
                
                if not text:
                    self.send_json({'error': 'Text is required'}, 400)
                    return
                
                if style not in PROMPTS:
                    self.send_json({'error': 'Valid style is required'}, 400)
                    return
                
                if len(text) > 5000:
                    self.send_json({'error': 'Text too long. Free tier limit: 5000 characters.'}, 413)
                    return
                
                result = call_gemini(text, style)
                self.send_json({'result': result})
                
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()
    
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
    print(f"📁 Serving files from: {os.getcwd()}")
    print("⏹️  Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)


if __name__ == '__main__':
    run_server()
