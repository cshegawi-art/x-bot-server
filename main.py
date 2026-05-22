import os
import json
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# مصفوفة التوكنات الخاصة بحساباتك الفعلية المأخوذة من صورتك السابقة
AUTH_TOKENS = [
    "b30b6fc0179be3b8e287fb145ff4a81e1884b267",
    "f5c73c894554345596a9140173e87c91a62a29da",
    "a9ba182b6424133a4bf4aa3e8c0dbcd947c32229"
]

def send_x_action(token, tweet_id, service_type):
    # إعداد جلسة اتصال لالتقاط وتمرير توكنات الأمان المتغيرة تلقائياً
    session = requests.Session()
    
    # 1. الاتصال المبدئي لتهيئة الكوكيز وجلب توكن الـ CSRF (ct0) من الحساب
    init_url = "https://x.com"
    cookies = {'auth_token': token}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        init_res = session.get(init_url, cookies=cookies, headers=headers, timeout=10)
        csrf_token = session.cookies.get('ct0', domain='.x.com')
        
        if not csrf_token:
            print(f"[FAILED] الحساب {token[:10]}... فشل استخراج توكن الأمان ct0 (تأكد من صلاحية الحساب)")
            return

        # 2. تحديد رابط الخدمة وصياغة الهيدرز الأمنية الإجبارية لمنصة X
        url = "https://x.com" if service_type == "comments" else "https://x.com"
        
        api_headers = {
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'X-Twitter-Auth-Type': 'OAuth2Session',
            'X-Twitter-Active-User': 'yes',
            'X-Csrf-Token': csrf_token, # السطر السحري لتخطي نظام حماية X
            'Content-Type': 'application/json',
            'User-Agent': headers['User-Agent']
        }
        
        payload = {}
        if service_type == "comments":
            payload = {"variables": {"tweet_text": "تم الإرسال بنجاح واستقرار! 🚀", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}

        # قذف العملية فوراً
        response = session.post(url, json=payload, headers=api_headers, cookies=cookies, timeout=10)
        print(f"[REPORT] الحساب: {token[:10]}... | الخدمة: {service_type} | كود الاستجابة: {response.status_code}")
        
    except Exception as e:
        print(f"[ERROR] خطأ اتصال بالحساب {token[:10]}... : {e}")

# دالة استقبال طلبات الـ API الفورية الصادرة من موقعك
def start_api_web_server():
    port = int(os.environ.get("PORT", 10000))
    class APIServerHandler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

        def do_POST(self):
            if self.path == "/create_order":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                try:
                    order = json.loads(post_data.decode('utf-8'))
                    service_type = order.get('service_type', 'comments')
                    tweet_id     = order.get('tweet_id', '')
                    quantity     = int(order.get('quantity', 1))
                    
                    print(f"\n📡 تم استقبال أمر قذف سحابي متزامن وموثوق!")
                    print(f"🚀 الخدمة: {service_type} | المعرف: {tweet_id} | العدد: {quantity}")
                    
                    # إطلاق الأتمتة فوراً بالتوازي لكل الحسابات عبر الـ Threads الخفيفة
                    selected_tokens = AUTH_TOKENS[:quantity]
                    for token in selected_tokens:
                        threading.Thread(target=send_x_action, args=(token, tweet_id, service_type), daemon=True).start()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "processing"}).encode('utf-8'))
                except:
                    self.send_response(400)
                    self.end_headers()

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"X-Bot Secure API Server is Active!")

    server = HTTPServer(('0.0.0.0', port), APIServerHandler)
    server.serve_forever()

def main():
    start_api_web_server()

if __name__ == "__main__":
    main()
