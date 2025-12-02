import requests
import json

# 音乐API配置
api_url = "https://v2.xxapi.cn/api/kugousearch"
api_key = "9769a9e12ac01f8a"
song_name = "小幸运"

# 尝试不同的参数组合
test_params_list = [
    {"key": api_key, "keyword": song_name, "page": "1", "limit": "1"},  # 主要尝试，添加分页参数
    {"key": api_key, "word": song_name, "page": "1"},      # 备用参数名
    {"key": api_key, "s": song_name, "limit": "1"},         # 常见参数名
    {"key": api_key, "q": song_name},          # 常见参数名
    {"key": api_key, "name": song_name},       # 可能的参数名
    {"key": api_key, "title": song_name},      # 可能的参数名
    {"key": api_key, "music": song_name},      # 可能的参数名
    {api_key: "", "keyword": song_name}        # 尝试不同的密钥格式
]

for i, test_params in enumerate(test_params_list):
    print(f"\n尝试参数组合 {i+1}/{len(test_params_list)}: {test_params}")
    
    try:
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(api_url, params=test_params, headers=headers, timeout=10)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 检查响应是否为空
        if not response.text:
            print("API响应为空")
            continue
        
        # 尝试解析JSON
        try:
            data = response.json()
            print(f"解析后的JSON: {data}")
            
            # 检查API返回的状态码
            if data.get('code') == 0:
                print(f"找到有效响应，使用参数: {test_params}")
                break
            else:
                print(f"API返回错误状态: {data.get('msg', '未知错误')}")
                
        except json.JSONDecodeError:
            print(f"JSON解析失败: {response.text}")
            
    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")