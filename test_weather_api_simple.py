from flask import Flask
from flask_socketio import SocketIO
import requests
import time

# 配置Flask应用
app = Flask(__name__)
socketio = SocketIO(app)

# 天气API配置
WEATHER_API_KEY = '7b96a8e86f1307d1'
WEATHER_API_URL = 'https://v2.xxapi.cn/api/weather'

# 测试天气API的函数
def test_weather_api():
    print("测试天气API...")
    
    # 模拟调用天气API
    city_name = "北京"
    params = {
        'key': WEATHER_API_KEY,
        'city': city_name
    }
    
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        
        weather_data = response.json()
        print(f"API响应: {weather_data}")
        
        # 处理API响应并构建回复
        if weather_data.get('code') == 200:
            data = weather_data.get('data', {})
            city = data.get('city', city_name)
            forecast_list = data.get('data', [])
            
            # 构建天气回复
            weather_reply = f"{city}天气\n"
            
            # 获取今天的天气预报（列表中的第一个元素）
            if forecast_list:
                today = forecast_list[0]
                weather_reply += f"日期: {today.get('date', '')}\n"
                weather_reply += f"天气: {today.get('weather', '')}\n"
                weather_reply += f"温度: {today.get('temperature', '')}\n"
                weather_reply += f"空气质量: {today.get('air_quality', '')}\n"
                weather_reply += f"风向风力: {today.get('wind', '')}\n"
            
            print(f"构建的天气回复: {weather_reply}")
            return True
        else:
            print(f"API调用失败: {weather_data.get('msg', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"API调用异常: {str(e)}")
        return False

if __name__ == '__main__':
    test_weather_api()