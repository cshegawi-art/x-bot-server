import asyncio
import os
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from playwright.async_api import async_playwright

# مصفوفة التوكنات الخاصة بحساباتك الفعلية المأخوذة من صورتك السابقة
AUTH_TOKENS = [
    "b30b6fc0179be3b8e287fb145ff4a81e1884b267",
    "f5c73c894554345596a9140173e87c91a62a29da",
    "a9ba182b6424133a4bf4aa3e8c0dbcd947c32229"
]

async def execute_x_action(token, tweet_id, service_type):
    async with async_playwright() as p:
        # تشغيل متصفح خفي ذكي وسريع
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # حقن الـ auth_token الخاص بك داخل ملفات تعريف ارتباط المتصفح
        await context.add_cookies([{
            'name': 'auth_token',
            'value': token,
            'domain': '.x.com',
            'path': '/'
        }])
        
        page = await context.new_page()
        try:
            # التوجه مباشرة إلى رابط التغريدة المستهدفة
            await page.goto(f"https://x.com{tweet_id}", timeout=30000)
            await page.wait_for_timeout(3000) # انتظار تحميل واجهة الصفحة
            
            if service_type == "comments":
                # البحث التلقائي عن صندوق كتابة التعليق (الرد)
                comment_box = await page.query_selector('[data-testid="tweetTextarea_0"]')
                if comment_box:
                    await comment_box.click()
                    await comment_box.fill("تعليق تلقائي سريع ومستقر! 🚀")
                    # الضغط على زر إرسال الرد
                    reply_btn = await page.query_selector('[data-testid="tweetButtonInline"]')
                    if reply_btn:
                        await reply_btn.click()
                        print(f"[SUCCESS] الحساب {token[:10]}... أرسل التعليق بنجاح.")
            else:
                # خدمة اللايكات: البحث عن زر الإعجاب والضغط عليه
                like_btn = await page.query_selector('[data-testid="like"]')
                if like_btn:
                    await like_btn.click()
                    print(f"[SUCCESS] الحساب {token[:10]}... وضع إعجاب بنجاح.")
                    
        except Exception as e:
            print(f"[ERROR] فشل التنفيذ للحساب {token[:10]}... بسبب: {e}")
        finally:
            await browser.close()

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
                    delay_time   = int(order.get('delay_time', 5))
                    
                    print(f"\n📡 تم استقبال أمر قذف سحابي متزامن عبر المتصفح الذكي!")
                    print(f"🚀 الخدمة: {service_type} | المعرف: {tweet_id} | العدد: {quantity}")
                    
                    # إطلاق الأتمتة فوراً في الخلفية بالتوازي لكل الحسابات
                    threading.Thread(target=lambda: asyncio.run(run_browser_blast(service_type, tweet_id, quantity, delay_time)), daemon=True).start()
                    
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
            self.wfile.write(b"X-Bot Browser API Server is Active!")

    server = HTTPServer(('0.0.0.0', port), APIServerHandler)
    server.serve_forever()

async def run_browser_blast(service_type, tweet_id, quantity, delay_time):
    selected_tokens = AUTH_TOKENS[:quantity]
    tasks = []
    for token in selected_tokens:
        tasks.append(execute_x_action(token, tweet_id, service_type))
        if delay_time > 0:
            await asyncio.sleep(delay_time)
            
    await asyncio.gather(*tasks)
    print("✨ انتهت دورة القذف المتصفحي بالكامل.")

def main():
    start_api_web_server()

if __name__ == "__main__":
    main()
