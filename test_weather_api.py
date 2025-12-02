import requests

# 天气API配置
WEATHER_API_KEY = '7b96a8e86f1307d1'
WEATHER_API_URL = 'https://v2.xxapi.cn/api/weather'

# 测试API调用
def test_weather_api(city_name):
    try:
        params = {
            'key': WEATHER_API_KEY,
            'city': city_name
        }
        
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        
        weather_data = response.json()
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {weather_data}")
        
        # 检查数据结构
        print("\n数据结构分析:")
        if isinstance(weather_data, dict):
            for key, value in weather_data.items():
                print(f"{key}: {type(value).__name__}")
                if key == 'data' and isinstance(value, dict):
                    print("data内容:")
                    for data_key, data_value in value.items():
                        print(f"  {data_key}: {type(data_value).__name__}")
                        if data_key == 'now' and isinstance(data_value, dict):
                            print("  now内容:")
                            for now_key, now_value in data_value.items():
                                print(f"    {now_key}: {now_value}")
                        elif data_key == 'forecast' and isinstance(data_value, list):
                            print("  forecast内容:")
                            for i, forecast_item in enumerate(data_value):
                                print(f"    第{i+1}天:")
                                for forecast_key, forecast_value in forecast_item.items():
                                    print(f"      {forecast_key}: {forecast_value}")
    except Exception as e:
        print(f"API调用错误: {str(e)}")

# 测试几个城市
test_weather_api("北京")
test_weather_api("上海")