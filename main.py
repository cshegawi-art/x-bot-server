import asyncio
import aiohttp
import mysql.connector
import time
import os

# بيانات الاتصال بقاعدة بيانات InfinityFree
DB_CONFIG = {
    'host': '://infinityfree.com', # ضع الهوست الخاص بك هنا
    'user': 'if0_XXXXXX',             # اسم المستخدم
    'password': 'password_here',       # كلمة المرور
    'database': 'if0_XXXXXX_dbname'    # اسم قاعدة البيانات الكامل
}

sem = asyncio.Semaphore(100)

async def send_x_request(session, db_conn, order_id, token, tweet_id, service_type):
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
            payload = {"variables": {"tweet_text": "تعليق تلقائي سريع وآمن من السيرفر!", "reply": {"in_reply_to_tweet_id": tweet_id}, "dark_request": False, "semantic_annotation_ids": []}, "features": {"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "longform_notetweets_inline_comments_enabled": True, "responsive_web_edit_tweet_api_enabled": True}}
        else:
            payload = {"variables": {"tweet_id": tweet_id}, "features": {"responsive_web_twitter_article_tweet_consumption_enabled": True}}

        status = "failed"
        res_msg = "Unknown Error"

        try:
            async with session.post(url, json=payload, headers=headers, cookies=cookies, timeout=10) as response:
                res_msg = f"HTTP Code: {response.status}"
                if response.status in [200, 201]:
                    status = "success"
                    res_msg = "Executed Successfully"
                elif response.status == 401:
                    res_msg = "فشل: توكن منتهي الصلاحية"
                elif response.status == 403:
                    res_msg = "حظر: حساب مقيد أو محظور"
        except Exception as e:
            res_msg = f"Network Error: {str(e)}"

        try:
            cursor = db_conn.cursor()
            cursor.execute("INSERT INTO order_logs (order_id, token, status, response_message) VALUES (%s, %s, %s, %s)", 
                           (order_id, token[:15] + "...", status, res_msg))
            db_conn.commit()
            cursor.close()
        except:
            pass

async def process_order(db_conn, order):
    order_id, service_type, tweet_id, quantity, delay_time = order
    print(f"🚀 معالجة طلب جديد رقم {order_id} | كمية: {quantity}")
    
    cursor = db_conn.cursor()
    cursor.execute("UPDATE orders SET status = 'processing' WHERE id = %s", (order_id,))
    db_conn.commit()

    # محاكاة توليد توكنات حقيقية من قاعدة البيانات أو كتابتها كمصفوفة برمجية هنا
    # يمكنك وضع توكناتك هنا مباشرة داخل المصفوفة بدلاً من قراءة ملف خارجي
    tokens = ["token_1_here", "token_2_here"] # املأ حساباتك داخل الأقواس
    tokens = tokens[:quantity]

    if not tokens:
        print("❌ لا توجد حسابات مضافة لتنفيذ هذا الطلب.")
        cursor.execute("UPDATE orders SET status = 'failed' WHERE id = %s", (order_id,))
        db_conn.commit()
        cursor.close()
        return

    async with aiohttp.ClientSession() as session:
        tasks = []
        for token in tokens:
            tasks.append(send_x_request(session, db_conn, order_id, token, tweet_id, service_type))
            if delay_time > 0:
                await asyncio.sleep(delay_time / 10)
        
        await asyncio.gather(*tasks)

    cursor.execute("UPDATE orders SET status = 'completed' WHERE id = %s", (order_id,))
    db_conn.commit()
    cursor.close()
    print(f"✅ تم اكتمال الطلب رقم {order_id}")

async def main():
    print("🛰️ السيرفر السحابي يعمل الآن ويراقب قاعدة البيانات باستمرار...")
    while True:
        try:
            db_conn = mysql.connector.connect(**DB_CONFIG)
            cursor = db_conn.cursor()
            cursor.execute("SELECT id, service_type, tweet_id, quantity, delay_time FROM orders WHERE status = 'pending' LIMIT 1")
            order = cursor.fetchone()
            cursor.close()
            
            if order:
                await process_order(db_conn, order)
                
            db_conn.close()
        except Exception as e:
            print(f"⚠️ خطأ قاعدة البيانات: {e}")
            
        await asyncio.sleep(5) # فحص الجداول كل 5 ثوانٍ تلقائياً

if __name__ == "__main__":
    asyncio.run(main())
