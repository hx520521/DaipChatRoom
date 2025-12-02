import requests
import json

# 测试API返回的音乐数据结构
api_url = 'https://v2.xxapi.cn/api/kugousearch'
params = {'key': '9769a9e12ac01f8a', 'music': '小幸运'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print('正在调用音乐API...')
response = requests.get(api_url, params=params, headers=headers)
print('API响应状态:', response.status_code)

if response.status_code == 200:
    try:
        data = response.json()
        print('\nAPI返回数据结构:')
        print(f'- 状态码: {data.get("code")}')
        print(f'- 消息: {data.get("msg")}')
        print(f'- 数据类型: {type(data.get("data"))}')
        
        # 显示第一首歌曲
        if isinstance(data.get("data"), list) and len(data.get("data")) > 0:
            first_song = data.get("data")[0]
            print('\n第一首歌曲详情:')
            print(f'- 歌曲名: {first_song.get("song")}')
            print(f'- 歌手: {first_song.get("singer")}')
            print(f'- 音频URL: {first_song.get("url")}')
            print(f'- 专辑封面: {first_song.get("image")}')
            
            # 验证URL是否有效
            url = first_song.get("url")
            if url:
                try:
                    print('\n正在验证音频URL...')
                    audio_response = requests.head(url, timeout=5)
                    print(f'音频URL有效性: {audio_response.status_code == 200}')
                    print(f'状态码: {audio_response.status_code}')
                    print(f'Content-Type: {audio_response.headers.get("Content-Type")}')
                    print(f'Content-Length: {audio_response.headers.get("Content-Length")}')
                except Exception as e:
                    print(f'音频URL测试失败: {e}')
    except json.JSONDecodeError as e:
        print(f'JSON解析失败: {e}')
        print(f'响应内容: {response.text}')
else:
    print(f'API请求失败: {response.status_code}')
    print(f'响应内容: {response.text}')
