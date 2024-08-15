import psycopg2
import requests
import json
import time
import hmac
import hashlib
import base64

# PostgreSQL 連線資訊
db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'C0untry2024',
    'host': '35.236.155.143',
    'port': '5432'
}

# API 設定
username = 'apidemo'
secret = b'apidemo'
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
data = response.json()

# 連接 PostgreSQL
try:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # 插入數據
    for order in data:
        cur.execute('''
        INSERT INTO orders (
            id, order_number, order_name, buyer_email, buyer_mobile, 
            receiver_name, receiver_phone, receiver_address, cvs_store_id, 
            allpay_logistics_id, shipping_type, shipping_name, logistics_id, 
            delivery_date, delivery_time, payment_name, payment_url, merchant_trade_no, 
            total_line_items_price, shipping_rate_price, total_price, 
            total_bonus_redemption_price, note, referral_code, checkout_referral_code, 
            checkout_referral_user_name, register_referral_code, from_device, token, 
            created_at, updated_at, confirmed_at
        ) VALUES (
            %(id)s, %(order_number)s, %(order_name)s, %(buyer_email)s, %(buyer_mobile)s, 
            %(receiver_name)s, %(receiver_phone)s, %(receiver_address)s, %(cvs_store_id)s, 
            %(allpay_logistics_id)s, %(shipping_type)s, %(shipping_name)s, %(logistics_id)s, 
            %(delivery_date)s, %(delivery_time)s, %(payment_name)s, %(payment_url)s, %(merchant_trade_no)s, 
            %(total_line_items_price)s, %(shipping_rate_price)s, %(total_price)s, 
            %(total_bonus_redemption_price)s, %(note)s, %(referral_code)s, %(checkout_referral_code)s, 
            %(checkout_referral_user_name)s, %(register_referral_code)s, %(from_device)s, %(token)s, 
            %(created_at)s, %(updated_at)s, %(confirmed_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            order_number = EXCLUDED.order_number,
            order_name = EXCLUDED.order_name,
            buyer_email = COALESCE(EXCLUDED.buyer_email, orders.buyer_email),
            buyer_mobile = COALESCE(EXCLUDED.buyer_mobile, orders.buyer_mobile),
            receiver_name = COALESCE(EXCLUDED.receiver_name, orders.receiver_name),
            receiver_phone = COALESCE(EXCLUDED.receiver_phone, orders.receiver_phone),
            receiver_address = COALESCE(EXCLUDED.receiver_address, orders.receiver_address),
            cvs_store_id = COALESCE(EXCLUDED.cvs_store_id, orders.cvs_store_id),
            allpay_logistics_id = COALESCE(EXCLUDED.allpay_logistics_id, orders.allpay_logistics_id),
            shipping_type = COALESCE(EXCLUDED.shipping_type, orders.shipping_type),
            shipping_name = COALESCE(EXCLUDED.shipping_name, orders.shipping_name),
            logistics_id = COALESCE(EXCLUDED.logistics_id, orders.logistics_id),
            delivery_date = COALESCE(EXCLUDED.delivery_date, orders.delivery_date),
            delivery_time = COALESCE(EXCLUDED.delivery_time, orders.delivery_time),
            payment_name = COALESCE(EXCLUDED.payment_name, orders.payment_name),
            payment_url = COALESCE(EXCLUDED.payment_url, orders.payment_url),
            merchant_trade_no = COALESCE(EXCLUDED.merchant_trade_no, orders.merchant_trade_no),
            total_line_items_price = COALESCE(EXCLUDED.total_line_items_price, orders.total_line_items_price),
            shipping_rate_price = COALESCE(EXCLUDED.shipping_rate_price, orders.shipping_rate_price),
            total_price = COALESCE(EXCLUDED.total_price, orders.total_price),
            total_bonus_redemption_price = COALESCE(EXCLUDED.total_bonus_redemption_price, orders.total_bonus_redemption_price),
            note = COALESCE(EXCLUDED.note, orders.note),
            referral_code = COALESCE(EXCLUDED.referral_code, orders.referral_code),
            checkout_referral_code = COALESCE(EXCLUDED.checkout_referral_code, orders.checkout_referral_code),
            checkout_referral_user_name = COALESCE(EXCLUDED.checkout_referral_user_name, orders.checkout_referral_user_name),
            register_referral_code = COALESCE(EXCLUDED.register_referral_code, orders.register_referral_code),
            from_device = COALESCE(EXCLUDED.from_device, orders.from_device),
            token = COALESCE(EXCLUDED.token, orders.token),
            created_at = COALESCE(EXCLUDED.created_at, orders.created_at),
            updated_at = COALESCE(EXCLUDED.updated_at, orders.updated_at),
            confirmed_at = COALESCE(EXCLUDED.confirmed_at, orders.confirmed_at)
        ''', {
            'id': order.get('id'),
            'order_number': order.get('order_number'),
            'order_name': order.get('order_name'),
            'buyer_email': order.get('buyer', {}).get('email'),
            'buyer_mobile': order.get('buyer', {}).get('mobile'),
            'receiver_name': order.get('receiver', {}).get('name'),
            'receiver_phone': order.get('receiver', {}).get('phone'),
            'receiver_address': order.get('receiver', {}).get('address'),
            'cvs_store_id': order.get('receiver', {}).get('cvs_store_id'),
            'allpay_logistics_id': order.get('receiver', {}).get('allpay_logistics_id'),
            'shipping_type': order.get('shipping_type'),
            'shipping_name': order.get('shipping_name'),
            'logistics_id': order.get('logistics_id'),
            'delivery_date': order.get('delivery_date'),
            'delivery_time': order.get('delivery_time'),
            'payment_name': order.get('payment_name'),
            'payment_url': order.get('payment_url'),
            'merchant_trade_no': order.get('merchant_trade_no'),
            'total_line_items_price': order.get('prices', {}).get('total_line_items_price'),
            'shipping_rate_price': order.get('prices', {}).get('shipping_rate_price'),
            'total_price': order.get('prices', {}).get('total_price'),
            'total_bonus_redemption_price': order.get('total_bonus_redemption_price'),
            'note': order.get('note'),
            'referral_code': order.get('referral_code'),
            'checkout_referral_code': order.get('checkout_referral_code'),
            'checkout_referral_user_name': order.get('checkout_referral_user_name'),
            'register_referral_code': order.get('register_referral_code'),
            'from_device': order.get('from_device'),
            'token': order.get('token'),
            'created_at': order.get('created_at'),
            'updated_at': order.get('updated_at'),
            'confirmed_at': order.get('confirmed_at')
        })

    conn.commit()
    cur.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
