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


@app.route("/callback", methods=['GET'])
def callback():
    return "OK"

# Webhook 接收端點
@app.route('/webhook/order/<scenario>', methods=['POST'])
def handle_order_webhook(scenario):
    # 取得 HTTP 標頭中的簽名
    try:
        data = request.json  # 解析 JSON 請求
        order_number = data.get('order_number', 'N/A')
        customer_name = data.get('customer', {}).get('name', 'N/A')
        total_price = data.get('prices', {}).get('total_price', 'N/A')
        line_items = data.get('line_items', [])
        for item in line_items:
            title = item.get('title', 'N/A')  # 如果沒有 'title'，預設為 'N/A'
            print(f"商品名稱: {title}")
        output = f"""
        訂單單號：{order_number}
        客戶姓名：{customer_name}
        訂單金額：{total_price}
        購買品項："""
               
        if scenario == "close":
            send_line_notify(output)
    
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'error': 'Server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
