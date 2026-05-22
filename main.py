import os
import json
import threading
import requests
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

# قائمة التوكنات الحقيقية الخاصة بحساباتك الثلاثة المأخوذة من لقطاتك السابقة
AUTH_TOKENS = [
    "b30b6fc0179be3b8e287fb145ff4a81e1884b267",
    "f5c73c894554345596a9140173e87c91a62a29da",
    "a9ba182b6424133a4bf4aa3e8c0dbcd947c32229"
]

def fetch_free_proxies():
    url = "https://proxyscrape.com"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxies_list = response.text.strip().split("\r\n")
            if not proxies_list or len(proxies_list) < 5:
                proxies_list = response.text.strip().split("\n")
            return [p.strip() for p in proxies_list if p.strip()]
    except:
        pass
    return []

def blast_x_with_proxy(token, tweet_id, service_type, proxy_ip):
    session = requests.Session()
    proxies = {"http": f"http://{proxy_ip}", "https": f"http://{proxy_ip}"} if proxy_ip else None
    init_url = "https://x.com"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        init_res = session.get(init_url, cookies={'auth_token': token}, headers=headers, proxies=proxies, timeout=12)
        csrf_token = session.cookies.get('ct0', domain='.x.com')
        if not csrf_token:
            return
        url = "https://x.com" if service_type == "comments" else "https://x.com"
        api_headers = {
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'X-Twitter-Auth-Type': 'OAuth2Session',
            'X-Twitter-Active-User': 'yes',
            'X-Csrf-Token': csrf_token,
            'Content-Type': 'application/json',
            'User-Agent': headers['User-Agent']
        }
        payload = {}
        if service_type == "comments":
            payload = {"variables": {"tweet_text": "تم التنفيذ السحابي الجذري بنجاح واستقرار فوري! 🚀", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}
        response = session.post(url, json=payload, headers=api_headers, cookies={'auth_token': token}, proxies=proxies, timeout=12)
        print(f"[✅ نجاح القذف] الحساب: {token[:10]}... | الكود المرجعي: {response.status_code}")
    except:
        pass

class CloudBotServer(BaseHTTPRequestHandler):
    # السطور السحرية للسماح لمتصفحك الشخصي بالقذف الفوري المباشر دون حظر
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_cors_headers()
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            order = json.loads(post_data.decode('utf-8'))
            service_type = order.get('service_type', 'comments')
            tweet_id     = order.get('tweet_id', '')
            quantity     = int(order.get('quantity', 1))
            
            print(f"\n📡 [إشارة فورية] تم استلام أمر تشغيل مباشر من المتصفح في نفس الميلي ثانية!")
            print(f"🎯 الخدمة المطلوبة: {service_type} | التغريدة المستهدفة: {tweet_id} | كمية الحسابات الموجهة: {quantity}")
            
            free_proxies = fetch_free_proxies()
            selected_tokens = AUTH_TOKENS[:quantity]
            for token in selected_tokens:
                assigned_proxy = random.choice(free_proxies) if free_proxies else None
                threading.Thread(target=blast_x_with_proxy, args=(token, tweet_id, service_type, assigned_proxy), daemon=True).start()
                
            self.wfile.write(json.dumps({"status": "launched"}).encode('utf-8'))
        except Exception as e:
            print(f"⚠️ خطأ فني أثناء المعالجة الحية: {e}")

    def do_GET(self):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"X-Bot Pro Proxy Rotation Core is Live and Ready!")

def main():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), CloudBotServer)
    print("🛰️ المحرك الجذري انطلق سحابياً وهو يراقب اللوحة الحية...")
    server.serve_forever()

if __name__ == "__main__":
    main()
