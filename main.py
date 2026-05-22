import asyncio
import aiohttp
import os
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

sem = asyncio.Semaphore(100)

# مصفوفة التوكنات والحسابات الخاصة بك (ضع توكناتك الحقيقية هنا داخل الأقواس)
AUTH_TOKENS = [
    "b30bfc0179be3b8e207fb145ff4a01e1084b6267",
    "t5c73e094554345596a9140173e87c91a62a2958a",
    "a96a102b6424133e4ef843e3c808cd942c32229c"
]

async def send_x_request(session, token, tweet_id, service_type):
    async with sem:
        url = "https://x.com" if service_type == "comments" else "https://x.com"
        cookies = {'auth_token': token}
        headers = {
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {}
        if service_type == "comments":
            payload = {"variables": {"tweet_text": "تعليق فوري وسريع!", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}

        try:
            async with session.post(url, json=payload, headers=headers, cookies=cookies, timeout=10) as response:
                print(f"[REPORT] الحساب: {token[:10]}... | الخدمة: {service_type} | كود الاستجابة: {response.status}")
        except Exception as e:
            print(f"[ERROR] خطأ اتصال بالحساب {token[:10]}... : {e}")

# دالة استقبال ومعالجة الطلبات الفورية القادمة من موقعك مباشرة
def start_api_web_server():
    port = int(os.environ.get("PORT", 10000))
    class APIServerHandler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            # تخطي حماية المتصفحات (CORS) للسماح للموقع بالإرسال المباشر
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
                    print(f"\n📡 تم استقبال طلب فوري مباشر وموثوق من اللوحة الإلكترونية!")
                    
                    service_type = order.get('service_type', 'comments')
                    tweet_id     = order.get('tweet_id', '')
                    quantity     = int(order.get('quantity', 1))
                    delay_time   = int(order.get('delay_time', 5))
                    
                    print(f"🚀 بدء القذف السحابي المتزامن | الخدمة: {service_type} | التغريدة: {tweet_id} | كمية الحسابات: {quantity}")
                    
                    # تشغيل محرك الأتمتة السريع في خيط مستقيل لعدم حظر السيرفر
                    threading.Thread(target=lambda: asyncio.run(execute_fast_blast(service_type, tweet_id, quantity, delay_time)), daemon=True).start()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "processing"}).encode('utf-8'))
                except Exception as e:
                    self.send_response(400)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"X-Bot API Server is Active and Waiting for Immediate Requests!")

    server = HTTPServer(('0.0.0.0', port), APIServerHandler)
    server.serve_forever()

async def execute_fast_blast(service_type, tweet_id, quantity, delay_time):
    selected_tokens = AUTH_TOKENS[:quantity]
    async with aiohttp.ClientSession() as session:
        tasks = []
        for token in selected_tokens:
            tasks.append(send_x_request(session, token, tweet_id, service_type))
            if delay_time > 0:
                await asyncio.sleep(delay_time / 10)
        
        await asyncio.gather(*tasks)
        print("✨ تم اكتمال قذف الدفعة الحالية بالكامل وتحديث تقارير الاستجابة بالأعلى.")

def main():
    print("🛰️ السيرفر السحابي المطور انطلق بنظام الـ API الفوري المباشر بانتظار قذف الطلبات...")
    start_api_web_server()

if __name__ == "__main__":
    main()
