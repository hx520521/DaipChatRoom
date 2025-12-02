import requests
import json

# 当前app.py中的配置
api_url = "https://v2.xxapi.cn/api/kugousearch"
api_key = "9769a9e12ac01f8a"
song_name = "小幸运"

print(f"测试音乐API: {api_url}")
print(f"搜索歌曲: {song_name}")
print(f"API密钥: {api_key}")

# 测试所有当前使用的参数组合
test_params_list = [
    {"key": api_key, "name": song_name},
    {"key": api_key, "keyword": song_name},
    {"key": api_key, "word": song_name},
    {"key": api_key, "s": song_name},
    {"key": api_key, "q": song_name}
]

for i, params in enumerate(test_params_list):
    print(f"\n尝试参数组合 {i+1}/{len(test_params_list)}: {params}")
    
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
            print(f"状态码: {data.get('code')}")
            print(f"消息: {data.get('msg')}")
            print(f"数据: {data.get('data')}")
            
            if data.get('code') == 1:
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