import os
import json
import threading
import requests
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# قائمة التوكنات الفعلية والحقيقية الخاصة بحساباتك الثلاثة
AUTH_TOKENS = [
    "b30b6fc0179be3b8e287fb145ff4a81e1884b267",
    "f5c73c894554345596a9140173e87c91a62a29da",
    "a9ba182b6424133a4bf4aa3e8c0dbcd947c32229"
]

# دالة ذكية ومستقرة لجلب قائمة البروكسيات الحية فورياً لتفادي حظر جدار حماية X
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 1. الاتصال المبدئي لجلب توكن الأمان المتغير ct0 عبر الأيبي الحركي للبروكسي
        init_res = session.get(init_url, cookies={'auth_token': token}, headers=headers, proxies=proxies, timeout=12)
        csrf_token = session.cookies.get('ct0', domain='.x.com')
        
        if not csrf_token:
            print(f"[🔄 إعادة محاولة] البروكسي {proxy_ip} لم يستجب للحساب {token[:10]}... جاري التبديل تلقائياً.")
            return

        # 2. توجيه أمر الإطلاق المتزامن المباشر
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
        print(f"[💥 تقرير نجاح القذف] الحساب: {token[:10]}... | البروكسي: {proxy_ip} | كود الاستجابة الفعلي لـ X: {response.status_code}")
        
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
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            order = json.loads(post_data.decode('utf-8'))
            service_type = order.get('service_type', 'comments')
            tweet_id     = order.get('tweet_id', '')
            quantity     = int(order.get('quantity', 1))
            
            print(f"\n📡 [إشارة فورية] تم استقبال أمر تشغيل مباشر من أزرار اللوحة الإلكترونية!")
            print(f"🎯 الخدمة: {service_type} | التغريدة المستهدفة: {tweet_id} | كمية الحسابات: {quantity}")
            
            free_proxies = fetch_free_proxies()
            selected_tokens = AUTH_TOKENS[:quantity]
            for token in selected_tokens:
                assigned_proxy = random.choice(free_proxies) if free_proxies else None
                threading.Thread(target=blast_x_with_proxy, args=(token, tweet_id, service_type, assigned_proxy), daemon=True).start()
                
            self.wfile.write(json.dumps({"status": "launched"}).encode('utf-8'))
        except Exception as e:
            print(f"⚠️ خطأ فني أثناء المعالجة: {e}")

    def do_GET(self):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        
        # المسار السحري والجذري لتشغيل العمليات مباشرة من رابط شريط المتصفح فوراً
        if "/create_order" in self.path:
            try:
                query_components = parse_qs(urlparse(self.path).query)
                
                # التقاط المتغيرات المباشرة من الرابط
                service_type = query_components.get("service_type", ["comments"])[0]
                tweet_id     = query_components.get("tweet_id", [""])[0]
                quantity     = int(query_components.get("quantity", [1])[0])
                
                print(f"\n📡 [إشارة جذريّة] تم لقط أمر تشغيل مباشر وصافي من شريط المتصفح!")
                print(f"🚀 الخدمة المطلوبة: {service_type} | معرف التغريدة: {tweet_id} | عدد الحسابات: {quantity}")
                
                free_proxies = fetch_free_proxies()
                selected_tokens = AUTH_TOKENS[:quantity]
                for token in selected_tokens:
                    assigned_proxy = random.choice(free_proxies) if free_proxies else None
                    threading.Thread(target=blast_x_with_proxy, args=(token, tweet_id, service_type, assigned_proxy), daemon=True).start()
                
                self.wfile.write("✅ تم استقبال أمر القذف المباشر بنجاح! جاري جلب الأيبيات الحركية والتنفيذ السحابي الفوري.".encode("utf-8"))
            except Exception as e:
                self.wfile.write(f"⚠️ خطأ أثناء تفكيك الرابط: {e}".encode("utf-8"))
        else:
            self.wfile.write(b"X-Bot Pro Proxy Rotation Core is Live and Ready!")

def main():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), CloudBotServer)
    print("🛰️ المحرك الجذري انطلق سحابياً بنجاح وهو جاهز للقذف المباشر...")
    server.serve_forever()

if __name__ == "__main__":
    main()
