from flask import Flask, request, abort, jsonify
import hmac
import hashlib
import requests
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage
import os

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

# 設置你的 Webhook 密鑰 (從 Cyberbiz 後台取得)
WEBHOOK_SECRET = b'urlDkfgyJpKKUhROeyvXvVU-ObLzLmk5XUDbTXZMi-8'

def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    #token = 'KaRNNWyrwulLuZ0ioKvDOXGo7ybGRjsZa9Nql2rHTug'   #個人
    token ='Y15svh94pm2DGvMvdK1NWgMJDHQwOxrxx6SGEgGcFlB' #電商
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


@app.route("/callback", methods=['GET','POST'])
def callback():
    if request.method == 'GET':
        return "OK"
    elif request.method == 'POST':
        # group_id = 'C8ecab467e269cb16f4b9734fad9aa03f' 
        # output = TextSendMessage(text="PUSH成功")  # 要发送的纯文字消息
        # try:
        #    line_bot_api.push_message(group_id, output)
        # except Exception as e:
        #     print(f"发送失败: {e}")
        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    group_id = event.source.group_id
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=group_id)
    )
    print(user_message)



# Webhook 接收端點
@app.route('/webhook/order/<scenario>', methods=['POST'])
def handle_order_webhook(scenario):
    # 取得 HTTP 標頭中的簽名
    try:
        data = request.json  # 解析 JSON 請求
        order_name = data.get('order_name', 'N/A')
        customer_name = data.get('customer', {}).get('name', 'N/A')
        total_price = data.get('prices', {}).get('total_price', 'N/A')
        line_items = data.get('line_items', [])
        shipping_name = data.get('shipping_name', 'N/A')
        
        output = f"""\n訂單單號：{order_name}\n客戶姓名：{customer_name}\n出貨方式：{shipping_name}\n訂單金額：{total_price}\n購買品項："""
        
        for idx, item in enumerate(line_items, start=1):
            title = item.get('title', 'N/A')  # 如果沒有 'title'，預設為 'N/A'
            quantity = item.get('quantity', 'N/A')
            output += f"\n{idx}.{title} *{quantity}件"
        
        if scenario == "create":
           output = f"\n訂單狀態：新增" + output 
        
        if scenario == "close":
           output = f"\n訂單狀態：結案" + output 

        send_line_notify(output)
        

        group_id = 'C8ecab467e269cb16f4b9734fad9aa03f' 
        try:
            output_new = TextSendMessage(text=output)
            line_bot_api.push_message(group_id, output_new)
        except Exception as e:
            print(f"发送失败: {e}")
        
        
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'error': 'Server error'}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
