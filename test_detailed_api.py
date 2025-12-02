import requests
import json

# 详细测试音乐API
api_url = "https://v2.xxapi.cn/api/kugousearch"
api_key = "9769a9e12ac01f8a"
song_name = "小幸运"

print(f"详细测试音乐API: {api_url}")
print(f"搜索歌曲: {song_name}")
print(f"API密钥: {api_key}")
print("=" * 60)

# 测试所有可能的参数组合
all_params = [
    # 基本参数组合
    {"key": api_key, "name": song_name},
    {"key": api_key, "q": song_name},
    {"key": api_key, "keyword": song_name},
    {"key": api_key, "songname": song_name},
    {"key": api_key, "title": song_name},
    {"key": api_key, "music": song_name},
    
    # 基本参数 + 分页参数
    {"key": api_key, "name": song_name, "page": 1, "limit": 10},
    {"key": api_key, "q": song_name, "page": 1, "limit": 10},
    {"key": api_key, "keyword": song_name, "page": 1, "limit": 10},
    {"key": api_key, "songname": song_name, "page": 1, "limit": 10},
    {"key": api_key, "title": song_name, "page": 1, "limit": 10},
    
    # 不同分页参数值
    {"key": api_key, "name": song_name, "page": 1, "size": 10},
    {"key": api_key, "name": song_name, "offset": 0, "limit": 10},
    {"key": api_key, "name": song_name, "start": 0, "count": 10},
    
    # 仅分页参数
    {"page": 1, "limit": 10},
    {"page": 1, "limit": 10, "name": song_name},
    
    # 尝试不同的密钥参数名
    {"apikey": api_key, "name": song_name},
    {"api_key": api_key, "name": song_name},
    {"appkey": api_key, "name": song_name},
    {"token": api_key, "name": song_name},
    {"auth": api_key, "name": song_name},
    
    # 组合不同的参数名
    {"key": api_key, "name": song_name, "type": "song"},
    {"key": api_key, "name": song_name, "format": "json"},
    {"key": api_key, "name": song_name, "platform": "web"},
    {"key": api_key, "name": song_name, "source": "kugou"},
]

success_count = 0
failure_count = 0
all_responses = []

for i, params in enumerate(all_params):
    print(f"\n[{i+1}/{len(all_params)}] 尝试参数: {params}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        # 尝试解析JSON
        if response.text:
            try:
                data = response.json()
                print(f"JSON解析: {json.dumps(data, ensure_ascii=False, indent=2)}")
                print(f"状态码: {data.get('code')}")
                print(f"消息: {data.get('msg')}")
                print(f"数据: {data.get('data')}")
                
                all_responses.append({
                    "params": params,
                    "status_code": response.status_code,
                    "json_response": data
                })
                
                if data.get('code') == 0:
                    print("✅ 成功！")
                    success_count += 1
                else:
                    print("❌ 失败！")
                    failure_count += 1
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text}")
                failure_count += 1
        else:
            print("❌ 响应内容为空")
            failure_count += 1
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        failure_count += 1
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        failure_count += 1
    
    print("-" * 40)

print("\n" + "=" * 60)
print(f"测试总结: 成功 {success_count} 次, 失败 {failure_count} 次")
print("=" * 60)

# 分析所有响应
print("\n响应分析:")
print("=" * 60)

# 按状态码分组
status_codes = {}
for resp in all_responses:
    code = resp["json_response"].get("code")
    if code not in status_codes:
        status_codes[code] = []
    status_codes[code].append(resp["params"])

for code, params_list in status_codes.items():
    print(f"\n状态码 {code} 的参数组合 ({len(params_list)} 个):")
    for params in params_list:
        print(f"  - {params}")

# 查看所有错误消息
error_messages = set()
for resp in all_responses:
    msg = resp["json_response"].get("msg")
    if msg and resp["json_response"].get("code") != 0:
        error_messages.add(msg)

print("\n所有错误消息:")
for msg in error_messages:
    print(f"  - {msg}")

print("\n测试完成！")