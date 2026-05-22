import asyncio
import aiohttp
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# رابط ملف الطلبات النصي الموجود على موقعك بـ InfinityFree
QUEUE_URL = "http://kesug.com"

# دالة تشغيل منفذ اتصال حقيقي لإرضاء خوادم Render وتنشيط السيرفر فوراً
def start_dummy_web_server():
    port = int(os.environ.get("PORT", 10000))
    class SimpleWebServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("X-Bot System is active and checking orders!".encode("utf-8"))
        def log_message(self, format, *args):
            return  # كتم سجلات الطلبات الوهمية لإبقاء الشاشة نظيفة

    try:
        server = HTTPServer(('0.0.0.0', port), SimpleWebServer)
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ تنبيه السيرفر الوهمي: {e}")

sem = asyncio.Semaphore(100)

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
            payload = {"variables": {"tweet_text": "تعليق تلقائي سريع!", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}

        try:
            async with session.post(url, json=payload, headers=headers, cookies=cookies, timeout=10) as response:
                print(f"[REPORT] Token: {token[:10]}... | HTTP Code: {response.status}")
        except Exception as e:
            print(f"[ERROR] Connection Failed for token {token[:10]}... : {e}")

async def monitor_queue():
    # املأ مصفوفة التوكنات الخاصة بك هنا بشكل برميجي مباشر
    AUTH_TOKENS = [
        "token_1_here",
        "token_2_here",
        "token_3_here"
    ]

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(QUEUE_URL) as response:
                    if response.status == 200:
                        content = await response.text()
                        lines = content.splitlines()
                        
                        if lines:
                            first_line = lines[0]
                            parts = first_line.split('|')
                            
                            if len(parts) >= 7 and parts[0] == "PENDING":
                                _, service_type, sub_type, gender, delay_time, tweet_id, quantity = parts
                                quantity = int(quantity)
                                delay_time = int(delay_time)
                                
                                print(f"\n📡 تم رصد طلب جديد | خدمة: {service_type} | كمية: {quantity}")
                                selected_tokens = AUTH_TOKENS[:quantity]
                                
                                tasks = []
                                for token in selected_tokens:
                                    tasks.append(send_x_request(session, token, tweet_id, service_type))
                                    if delay_time > 0:
                                        await asyncio.sleep(delay_time / 10)
                                
                                await asyncio.gather(*tasks)
                                print("✨ تم الانتهاء من المعالجة السحابية الحالية بنجاح.")
            except Exception as e:
                pass
                
            await asyncio.sleep(6) # فحص الملف كل 6 ثوانٍ بانتظام

async def main():
    print("🛰️ السيرفر السحابي المستقل انطلق الآن ويراقب اللوحة بانتظام...")
    # تشغيل منفذ الويب في الخلفية بشكل آمن لتنشيط المنصة
    threading.Thread(target=start_dummy_web_server, daemon=True).start()
    # تشغيل محرك الأتمتة الرئيسي
    await monitor_queue()

if __name__ == "__main__":
    asyncio.run(main())
