import requests
import json

# 测试音乐API
api_url = "https://v2.xxapi.cn/api/kugousearch"
api_key = "9769a9e12ac01f8a"
song_name = "小幸运"

print(f"测试音乐API: {api_url}")
print(f"搜索歌曲: {song_name}")
print(f"API密钥: {api_key}")
print("=" * 60)

# 只测试成功的参数组合
params = {"key": api_key, "music": song_name}

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(api_url, params=params, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"完整响应内容: {response.text}")
    
    # 解析JSON
    if response.text:
        try:
            data = response.json()
            print(f"\nJSON解析 (格式化):")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            print(f"\n状态码: {data.get('code')}")
            print(f"消息: {data.get('msg')}")
            print(f"\n数据结构:")
            print(f"  - 数据类型: {type(data.get('data'))}")
            print(f"  - 数据内容: {data.get('data')}")
            
            # 如果是列表，打印第一个元素的结构
            if isinstance(data.get('data'), list) and len(data.get('data')) > 0:
                print(f"\n第一个元素结构:")
                print(json.dumps(data.get('data')[0], ensure_ascii=False, indent=2))
            elif isinstance(data.get('data'), dict):
                print(f"\n字典结构:")
                for key, value in data.get('data').items():
                    print(f"    - {key}: {type(value).__name__} = {value}")
                    
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON解析失败: {e}")
    else:
        print("\n❌ 响应内容为空")
    
except requests.exceptions.Timeout:
    print(f"\n❌ 请求超时")
except requests.exceptions.RequestException as e:
    print(f"\n❌ 请求失败: {str(e)}")