import os
import json
import threading
import requests
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# قائمة التوكنات الفعلية والحقيقية الخاصة بحساباتك الثلاثة
AUTH_TOKENS = [
    "e4d6598cdb8da596f6287e7684d848b2673cce69",
    "b30bfc0179be3b8e287fb145ff4a81e1884b267",
    "5c73e094554345596a9140173e87c91a62a2958a"
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
            payload = {"variables": {"tweet_text": "تم التنفيذ السحابي الجذري بنجاح واستقرار فوري! 🚀", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": false, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": true, "longform_notetweets_inline_comments_enabled": true, "responsive_web_edit_tweet_api_enabled": true}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": true}}
        response = session.post(url, json=payload, headers=api_headers, cookies={'auth_token': token}, proxies=proxies, timeout=12)
        print(f"[💥 تقرير نجاح القذف] الحساب: {token[:10]}... | كود الاستجابة الفعلي لـ X: {response.status_code}")
    except:
        pass

class CloudBotServer(BaseHTTPRequestHandler):
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
        self.end_headers()
        try:
            order = json.loads(post_data.decode('utf-8'))
            service_type = order.get('service_type', 'comments')
            tweet_id     = order.get('tweet_id', '')
            quantity     = int(order.get('quantity', 1))
            
            print(f"\n📡 [إشارة فورية] تم استقبال أمر تشغيل من اللوحة!")
            free_proxies = fetch_free_proxies()
            selected_tokens = AUTH_TOKENS[:quantity]
            for token in selected_tokens:
                assigned_proxy = random.choice(free_proxies) if free_proxies else None
                threading.Thread(target=blast_x_with_proxy, args=(token, tweet_id, service_type, assigned_proxy), daemon=True).start()
        except:
            pass

    def do_GET(self):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        
        # [المسار الجذري الفوري]: استقبال ومعالجة الأوامر مباشرة من رابط شريط المتصفح فوراً
        if "/create_order" in self.path:
            try:
                query_components = parse_qs(urlparse(self.path).query)
                service_type = query_components.get("service_type", ["comments"])[0]
                tweet_id     = query_components.get("tweet_id", [""])[0]
                quantity     = int(query_components.get("quantity", [1])[0])
                
                print(f"\n📡 [إشارة جذريّة] لقط أمر تشغيل مباشر من المتصفح!")
                print(f"🚀 الخدمة: {service_type} | التغريدة: {tweet_id} | الكمية: {quantity}")
                
                free_proxies = fetch_free_proxies()
                selected_tokens = AUTH_TOKENS[:quantity]
                for token in selected_tokens:
                    assigned_proxy = random.choice(free_proxies) if free_proxies else None
                    threading.Thread(target=blast_x_with_proxy, args=(token, tweet_id, service_type, assigned_proxy), daemon=True).start()
                
                self.wfile.write("✅ تم استقبال أمر القذف المباشر بنجاح! جاري التنفيذ السحابي الفوري الحركي.".encode("utf-8"))
            except Exception as e:
                self.wfile.write(f"⚠️ خطأ أثناء التفكيك البرمجي: {e}".encode("utf-8"))
        else:
            self.wfile.write(b"X-Bot Pro Proxy Rotation Core is Live and Ready!")

def main():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), CloudBotServer)
    print("🛰️ المحرك انطلق سحابياً وهو جاهز للقذف المباشر...")
    server.serve_forever()

if __name__ == "__main__":
    main()
