import os
import json
import threading
import requests
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

# قائمة التوكنات الحقيقية والنشطة الخاصة بحساباتك الثلاثة
AUTH_TOKENS = [
    "e4d6598cdb8da596f6287e7684d848b2673cce69",
    "b30bfc0179be3b8e287fb145ff4a81e1884b267",
    "5c73e094554345596a9140173e87c91a62a2958a"
]

# دالة ذكية تفحص البروكسي قبل استخدامه للتأكد من أنه شغال 100% ومضمون
def is_proxy_working(proxy_ip):
    proxies = {"http": f"http://{proxy_ip}", "https": f"http://{proxy_ip}"}
    try:
        # اختبار البروكسي على خادم خفيف، إذا استجاب في أقل من 3 ثوانٍ يعتبر ناجحاً
        response = requests.get("https://ipify.org", proxies=proxies, timeout=3)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

# دالة سحب وتصفية البروكسيات الحية فقط واستبعاد الميتة
def fetch_validated_proxies(needed_count):
    url = "https://proxyscrape.com"
    working_proxies = []
    try:
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            raw_list = response.text.strip().split("\n")
            clean_list = [p.strip() for p in raw_list if p.strip()]
            random.shuffle(clean_list) # عشوائية الاختيار لتفادي التكرار
            
            print(f"🔍 تم جلب {len(clean_list)} بروكسي خام، جاري الفحص السريع للحصول على {needed_count} بروكسي مضمون...")
            
            # فحص البروكسيات بالتوالي حتى نجمع العدد المطلوب للحسابات
            for proxy in clean_list:
                if is_proxy_working(proxy):
                    working_proxies.append(proxy)
                    print(f"✅ بروكسي فعال ومضمون: {proxy}")
                    if len(working_proxies) >= needed_count:
                        break
    except Exception as e:
        print(f"⚠️ خطأ أثناء جلب البروكسيات: {e}")
    return working_proxies

def blast_x_action(token, tweet_id, service_type, proxy_ip):
    session = requests.Session()
    proxies = {"http": f"http://{proxy_ip}", "https": f"http://{proxy_ip}"} if proxy_ip else None
    init_url = "https://x.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 1. الاتصال المبدئي الموثوق عبر الأيبي السكني للبروكسي المجاني الفعال لتهيئة الـ ct0
        init_res = session.get(init_url, cookies={'auth_token': token}, headers=headers, proxies=proxies, timeout=12)
        csrf_token = session.cookies.get('ct0', domain='.x.com')
        
        if not csrf_token:
            print(f"[❌ فشل أمني] الحساب {token[:10]}... تعذر استخراج الـ ct0 عبر البروكسي {proxy_ip}")
            return

        # 2. قذف العملية فوراً لخوادم موقع X
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
            payload = {"variables": {"tweet_text": "تم التنفيذ والظهور الواقعي بنجاح سحابي! 🚀", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}

        response = session.post(url, json=payload, headers=api_headers, cookies={'auth_token': token}, proxies=proxies, timeout=12)
        print(f"[💥 تقرير نجاح القذف] الحساب: {token[:10]}... | الكود: {response.status_code} | البروكسي: {proxy_ip}")
        
    except Exception as e:
        print(f"[⚠️ خطأ شبكة] تعذر القذف للحساب {token[:10]}... عبر الأيبي {proxy_ip} : {e}")

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
            
            print(f"\n📡 [إشارة حية] استقبال طلب قذف فوري مباشر من اللوحة الإلكترونية!")
            print(f"🎯 الخدمة: {service_type} | التغريدة: {tweet_id} | كمية الحسابات: {quantity}")
            
            selected_tokens = AUTH_TOKENS[:quantity]
            
            # جلب عدد بروكسيات فعال ومضمون مطابق تماماً لعدد الحسابات المطلوبة للطلب
            validated_proxies = fetch_validated_proxies(len(selected_tokens))
            
            for index, token in enumerate(selected_tokens):
                # تعيين البروكسي المضمون والناجح في الفحص لكل حساب بالتوازي
                assigned_proxy = validated_proxies[index] if index < len(validated_proxies) else None
                threading.Thread(target=blast_x_with_proxy, args=(token, tweet_id, service_type, assigned_proxy), daemon=True).start()
                
            self.wfile.write(json.dumps({"status": "launched"}).encode('utf-8'))
        except Exception as e:
            print(f"⚠️ خطأ فني أثناء المعالجة الحية: {e}")

    def do_GET(self):
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"X-Bot Pro Validated Proxy Core is Live!")

def main():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), CloudBotServer)
    print("🛰️ المحرك الجذري بالبروكسيات المضمونة انطلق سحابياً وهو جاهز للقذف المباشر...")
    server.serve_forever()

if __name__ == "__main__":
    main()
