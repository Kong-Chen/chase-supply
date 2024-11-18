import psycopg2
import requests
import json
import time
import hmac
import hashlib
import base64

# PostgreSQL 連線資訊
connection = psycopg2.connect(
    host="dpg-cpp4jouehbks73brha50-a.oregon-postgres.render.com",
    port="5432",
    database="nobody_y10j",
    user="kong",
    password="yydSDvrjnBhY68izhYu7UhRiiQPdPGth"
)

# API 設定
username = 'apidemo'
secret = b'apidemo'
#username = 'service@chaseshop.com.tw'
#secret = b'urlDkfgyJpKKUhROeyvXvVU-ObLzLmk5XUDbTXZMi-8'
http_method = 'GET'
url_base = 'https://api.cyberbiz.co'
url_path = '/v1/orders'
headers = 'x-date request-line'

# 取得 x-date
x_date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

# 生成 request-line
rline = http_method + ' ' + url_path + ' HTTP/1.1'

# 計算簽名
payload = ''
sig_str = 'x-date: ' + x_date + '\n' + rline
dig = hmac.new(secret, msg=sig_str.encode(), digestmod=hashlib.sha256).digest()
sig = base64.b64encode(dig).decode()
auth = f'hmac username="{username}", algorithm="hmac-sha256", headers="{headers}", signature="{sig}"'

# 發送 API 請求
request_headers = {'X-Date': x_date, 'Authorization': auth}
response = requests.get(url_base + url_path, headers=request_headers)
print(response.status_code)
print(response.text)
data = response.json()

# 連接 PostgreSQL
try:
    cur = connection.cursor()
    if not isinstance(data, list):
        raise ValueError("API response is not a list as expected.")
    # 插入數據
    for order in data:
        date = order.get('created_at', {})
        orderno = order.get('order_number',{})
        customer_name = order.get('customer', {}).get('name', 'N/A')
        prices = order.get('prices', {}).get('total_price', 'N/A')
        line_items = order.get('line_items', [])
         
        print(f"{orderno} - {date} - {customer_name} - {prices}")
        for item in line_items:
            title = item.get('title', 'N/A')
            print(f"  商品名稱: {title}")

    connection.commit()
    cur.close()
    connection.close()
except Exception as e:
    print(f'Error: {e}')
