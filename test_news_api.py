import requests
import json

# 新闻API配置
NEWS_API_KEY = '9769a9e12ac01f8a'
NEWS_API_URL = 'https://v2.xxapi.cn/api/baiduhot'

# 测试API调用
print('正在调用新闻API...')
response = requests.get(NEWS_API_URL, params={'key': NEWS_API_KEY})
print(f'API响应状态码: {response.status_code}')

if response.status_code == 200:
    try:
        news_data = response.json()
        print(f'\nAPI返回数据结构:')
        print(f'- 状态码: {news_data.get("code")}')
        print(f'- 消息: {news_data.get("msg")}')
        
        # 查看新闻列表
        news_list = news_data.get('data', [])
        print(f'\n新闻总数: {len(news_list)}')
        
        # 检查所有新闻是否有重复的1
        print(f'\n检查所有新闻的重复数字1:')
        for i, news in enumerate(news_list):
            title_str = news.get('title', '')
            desc_str = news.get('desc', '')
            
            # 检查是否包含重复的1
            has_repeated_ones = '111' in title_str or '111' in desc_str
            if has_repeated_ones:
                print(f'\n第{i+1}条新闻包含重复的1:')
                print(f'- 原始标题: {repr(title_str)}')
                print(f'- 原始描述: {repr(desc_str)}')
        
        # 如果没有找到重复的1，显示前5条新闻的详细内容
        if not any('111' in news.get('title', '') or '111' in news.get('desc', '') for news in news_list):
            print(f'\n未发现重复的1，显示前5条新闻详情:')
            for i, news in enumerate(news_list[:5]):
                print(f'\n第{i+1}条新闻:')
                print(f'- 原始标题: {repr(news.get("title"))}')
                print(f'- 原始描述: {repr(news.get("desc"))}')
                print(f'- URL: {news.get("url")}')
                print(f'- 热度: {news.get("hot")}')
                print(f'- 索引: {news.get("index")}')
            
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {e}')
        print(f'原始响应内容: {response.text}')
    except Exception as e:
        print(f'其他错误: {e}')
else:
    print(f'API调用失败: {response.status_code}')
    print(f'响应内容: {response.text}')
