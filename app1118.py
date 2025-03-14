from flask import Flask, request, jsonify
import hmac
import hashlib
import requests
import json

app = Flask(__name__)

# 設置你的 Webhook 密鑰 (從 Cyberbiz 後台取得)
WEBHOOK_SECRET = b'urlDkfgyJpKKUhROeyvXvVU-ObLzLmk5XUDbTXZMi-8'

def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    token = 'KaRNNWyrwulLuZ0ioKvDOXGo7ybGRjsZa9Nql2rHTug'   #個人
    headers = {
        'Authorization': 'Bearer ' + token
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    return response
 

# 驗證簽名的函數 
def verify_signature(secret, payload, signature):
    computed_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_signature, signature)


# Webhook 接收端點
@app.route('/webhook/order', methods=['POST'])
def handle_order_webhook():
    # 取得 HTTP 標頭中的簽名
    data = request.json  # 解析 JSON 請求
    order_number = data.get('order_number', 'N/A')
    customer_name = data.get('customer', {}).get('name', 'N/A')
    total_price = data.get('prices', {}).get('total_price', 'N/A')
    line_items = data.get('line_items', [])
    summary = f"收到資料:\n{order_number}-{customer_name}-{total_price}"
    send_line_notify(summary)  # 只傳前 1000 個字避免超長
    #response_message = f"接收到"
    #response = send_line_notify(response_message)
    
    
    signature = request.headers.get('X-Cyberbiz-Signature')
    # 確保簽名存在
    if not signature:
        return jsonify({'error': 'Missing signature'}), 400

    # 獲取請求的原始資料
    payload = request.get_data()

    # 驗證簽名
    if not verify_signature(WEBHOOK_SECRET, payload, signature):
        return jsonify({'error': 'Invalid signature'}), 403

    # 處理 Webhook 資料
    try:
        data = request.json  # 解析 JSON 請求
        order_number = data.get('order_number', 'N/A')
        customer_name = data.get('customer', {}).get('name', 'N/A')
        total_price = data.get('prices', {}).get('total_price', 'N/A')
        line_items = data.get('line_items', [])

        #print(f"收到新訂單：{order_number}")
        #print(f"客戶名稱：{customer_name}")
        #print(f"總金額：{total_price}")
        for item in line_items:
            #print(f"  商品名稱: {item.get('title', 'N/A')}，數量: {item.get('quantity', 0)}")
            response_message = f"123"
            response = send_line_notify(response_message)

        # 回應成功
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
