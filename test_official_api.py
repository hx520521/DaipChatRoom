import requests
import json

# 测试官方酷狗音乐API
api_url = "https://api.kugou.com/search/song"
song_name = "小幸运"

print(f"测试官方酷狗音乐API: {api_url}")
print(f"搜索歌曲: {song_name}")

# 测试官方API参数
params = {
    "keyword": song_name
}

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(api_url, params=params, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 尝试解析JSON
    if response.text:
        data = response.json()
        print(f"JSON解析结果: {data}")
        print(f"状态: {data.get('status')}")
        print(f"数据: {data.get('data')}")
        
        if data.get('status') == 1:
            print("✅ API调用成功！")
        else:
            print("❌ API调用失败！")
    else:
        print("❌ 响应内容为空")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except requests.exceptions.RequestException as e:
    print(f"❌ 请求失败: {str(e)}")
except json.JSONDecodeError:
    print(f"❌ JSON解析失败: {response.text}")

print("\n测试完成！")