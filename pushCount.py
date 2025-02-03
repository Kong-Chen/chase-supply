import requests

# 替换为您的 Channel Access Token
CHANNEL_ACCESS_TOKEN = "M85n4nYx5YSQn3po1KMjwNN8Rb5k14gUXtGkrKc6gESU8egXf12wowl5oQALVLv8x/H2rzsuz+J3NjJljB93aXb6CVKGqloUr1Yds0Eg/JsRn0I+MkMSZGlcwne1+LssjXd18zIY/Dm4S7epSFqFhAdB04t89/1O/w1cDnyilFU="

def get_push_message_quota():
    url = "https://api.line.me/v2/bot/message/quota"
    headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_push_message_usage():
    url = "https://api.line.me/v2/bot/message/quota/consumption"
    headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# 主程序
if __name__ == "__main__":
    quota_info = get_push_message_quota()
    usage_info = get_push_message_usage()

    print("全部數量:", quota_info)
    print("已使用數量", usage_info)
