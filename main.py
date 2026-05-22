import asyncio
import aiohttp
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# رابط ملف طابور الطلبات النصي الموجود على موقعك بـ InfinityFree
# استبدل masb.kesug.com برابط موقعك الفعلي إذا كان مختلفاً
QUEUE_URL = "http://kesug.com"

# دالة فتح منفذ اتصال وهمي لإرضاء سيرفر Render وتفعيل الخطة المجانية للأبد
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"X-Bot Server is Live and Running!")
        def log_message(self, format, *args):
            return # كتم سجلات السيرفر الوهمي لعدم ملء الشاشة
    
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

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
            payload = {"variables": {"tweet_text": "تعليق تلقائي سريع وموحد!", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}

        try:
            async with session.post(url, json=payload, headers=headers, cookies=cookies, timeout=10) as response:
                print(f"[REPORT] Token: {token[:10]}... | Service: {service_type} | HTTP Code: {response.status}")
        except Exception as e:
            print(f"[ERROR] Connection Failed for token {token[:10]}... : {e}")

async def process_orders_from_web():
    # قائمة التوكنات والحسابات الخاصة بك (ضع توكناتك الحقيقية هنا داخل المصفوفة مباشرة)
    AUTH_TOKENS = [
        "token_1_here",
        "token_2_here",
        "token_3_here"
    ]

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # قراءة ملف الطلبات النصي المرفوع على استضافة InfinityFree عن بعد
                async with session.get(QUEUE_URL) as response:
                    if response.status == 200:
                        content = await response.text()
                        lines = content.splitlines()
                        
                        if lines:
                            print(f"\n📡 تم رصد الطلبات غير المنفذة في السيرفر...")
                            # قراءة أول طلب في الطابور
                            first_line = lines[0]
                            parts = first_line.split('|')
                            
                            if len(parts) >= 7 and parts[0] == "PENDING":
                                _, service_type, sub_type, gender, delay_time, tweet_id, quantity = parts
                                quantity = int(quantity)
                                delay_time = int(delay_time)
                                
                                print(f"🚀 بدء معالجة سحابية فورا | خدمة: {service_type} | تغريدة: {tweet_id} | كمية: {quantity}")
                                
                                # تصفية الحسابات بناء على العدد المطلوبة
                                selected_tokens = AUTH_TOKENS[:quantity]
                                
                                tasks = []
                                for token in selected_tokens:
                                    tasks.append(send_x_request(session, token, tweet_id, service_type))
                                    if delay_time > 0:
                                        await asyncio.sleep(delay_time / 10)
                                
                                # إطلاق قذف العمليات في أجزاء من الثانية
                                await asyncio.gather(*tasks)
                                print("✨ تم الانتهاء من تنفيذ الدفعة الحالية بنجاح كامل.")
                                
                                # ملاحظة: في النسخة المتقدمة يتم تصفير الملف النصي من السيرفر لمنع التكرار
                                
            except Exception as e:
                print(f"⏳ بانتظار اتصال مستقر مع الاستضافة المجانية... {e}")
                
            await asyncio.sleep(5) # الفحص الدوري كل 5 ثواني

async def main():
    print("🛰️ السيرفر السحابي المستقل انطلق الآن ويراقب اللوحة الإلكترونية بانتظام...")
    # تشغيل المنفذ الوهمي في خيط منفصل لتنشيط الخدمة في منصة Render المجانية
    threading.Thread(target=run_dummy_server, daemon=True).start()
    # بدء مراقبة ومعالجة الطلبات
    await process_orders_from_web()

if __name__ == "__main__":
    asyncio.run(main())
