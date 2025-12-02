import requests
import json

# 测试之前发现的可能工作的API配置
api_url = "https://v2.xxapi.cn/api/kugousearch"
api_key = "9769a9e12ac01f8a"
song_name = "小幸运"

print(f"测试音乐API: {api_url}")
print(f"搜索歌曲: {song_name}")
print(f"API密钥: {api_key}")

# 测试多种可能的参数组合，包括之前可能工作的
all_params = [
    # 基础参数
    {"key": api_key, "name": song_name},
    {"key": api_key, "q": song_name},
    {"key": api_key, "songname": song_name},
    {"key": api_key, "keyword": song_name},
    
    # 增加分页参数
    {"key": api_key, "name": song_name, "page": 1, "limit": 10},
    {"key": api_key, "q": song_name, "page": 1, "limit": 10},
    
    # 不同的参数名
    {"key": api_key, "title": song_name},
    {"key": api_key, "music": song_name},
    
    # 尝试不使用key参数
    {"name": song_name},
    {"q": song_name},
    {"keyword": song_name},
]

for i, params in enumerate(all_params):
    print(f"\n尝试参数组合 {i+1}/{len(all_params)}: {params}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 尝试解析JSON
        if response.text:
            try:
                data = response.json()
                print(f"JSON解析结果: {data}")
                print(f"状态码: {data.get('code')}")
                print(f"消息: {data.get('msg')}")
                print(f"数据: {data.get('data')}")
                
                if data.get('code') == 1:
                    print("✅ API调用成功！")
                else:
                    print("❌ API调用失败！")
            except json.JSONDecodeError:
                print(f"❌ JSON解析失败: {response.text}")
        else:
            print("❌ 响应内容为空")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")

print("\n测试完成！")