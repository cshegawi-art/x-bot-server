import os
import json
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# مصفوفة الحسابات والبروكسيات المخصصة لها (الهيكل الاحترافي للـ 1000 حساب)
# يجب وضع البروكسي الخاص بكل حساب أمامه لضمان عدم الحظر نهائياً
ACCOUNTS_DATA = [
    {
        "token": "b30b6fc0179be3b8e287fb145ff4a81e1884b267",
        "proxy": "http://user:pass@proxy_ip:port" # ضع البروكسي الخاص بالحساب الأول هنا
    },
    {
        "token": "f5c73c894554345596a9140173e87c91a62a29da",
        "proxy": "http://user:pass@proxy_ip:port" # ضع البروكسي الخاص بالحساب الثاني هنا
    },
    {
        "token": "a9ba182b6424133a4bf4aa3e8c0dbcd947c32229",
        "proxy": "http://user:pass@proxy_ip:port" # ضع البروكسي الخاص بالحساب الثالث هنا
    }
]

def blast_x_action(account, tweet_id, service_type):
    token = account["token"]
    proxy_url = account["proxy"]
    
    session = requests.Session()
    
    # ربط البروكسي السكني بالجلسة الحالية للحساب لتخطي حظر موقع X
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    } if proxy_url and "user" not in proxy_url else None

    init_url = "https://x.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 1. الاتصال المبدئي عبر البروكسي لجلب توكن الأمان الإجباري ct0
        init_res = session.get(init_url, cookies={'auth_token': token}, headers=headers, proxies=proxies, timeout=15)
        csrf_token = session.cookies.get('ct0', domain='.x.com')
        
        if not csrf_token:
            print(f"[❌ خطأ أمني] الحساب {token[:10]}... فشل في استخراج ct0. التوكن فاسد أو البروكسي بطيء.")
            return

        # 2. توجيه طلب القذف المباشر لخوادم الـ GraphQL الخاصة بـ X
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
            payload = {"variables": {"tweet_text": "تم التنفيذ التلقائي بدقة وسرعة! 🚀", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}

        # إطلاق قذف العملية الفوري
        response = session.post(url, json=payload, headers=api_headers, cookies={'auth_token': token}, proxies=proxies, timeout=15)
        print(f"[💥 تقرير السيرفر] الحساب: {token[:10]}... | الكود: {response.status_code} | الاستجابة: {response.text[:50]}")
        
    except Exception as e:
        print(f"[⚠️ خطأ اتصال] الحساب {token[:10]}... تعذر القذف بسبب: {e}")

# مستقبل الـ API السحابي المباشر
class CloudBotServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            order = json.loads(post_data.decode('utf-8'))
            service_type = order.get('service_type', 'comments')
            tweet_id     = order.get('tweet_id', '')
            quantity     = int(order.get('quantity', 1))
            
            print(f"\n📡 [إشارة حية] استقبال أمر تشغيل فوري من موقعك الإلكتروني.")
            print(f"🎯 الخدمة: {service_type} | التغريدة المستهدفة: {tweet_id} | العدد المطلوب: {quantity}")
            
            # تشغيل جميع الحسابات المطلوبة معاً في نفس الميلي ثانية بالتوازي عبر الـ Threads
            selected_accounts = ACCOUNTS_DATA[:quantity]
            for account in selected_accounts:
                threading.Thread(target=blast_x_action, args=(account, tweet_id, service_type), daemon=True).start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "launched"}).encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"X-Bot Turbo Core is Live and Ready!")

def main():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), CloudBotServer)
    print("🛰️ المحرك الجذري انطلق سحابياً وهو جاهز لاستقبال الأوامر الحية...")
    server.serve_forever()

if __name__ == "__main__":
    main()
