import requests
import json
import os

# 配置
TEST_MUSIC = '小幸运'

# 直接调用音乐搜索API
def test_music_api():
    """直接测试音乐搜索API并验证专辑封面"""
    print(f"\n🔍 直接测试音乐搜索API: {TEST_MUSIC}")
    
    # 调用音乐搜索API
    api_url = "https://v2.xxapi.cn/api/kugousearch"
    api_key = "9769a9e12ac01f8a"
    
    try:
        response = requests.get(
            api_url,
            params={"key": api_key, "music": TEST_MUSIC},
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            return False
        
        result = response.json()
        print(f"✅ API请求成功，状态码: {response.status_code}")
        
        # 检查API响应
        if result.get('code') != 200:
            print(f"❌ API返回错误: {result.get('msg', '未知错误')}")
            return False
        
        music_data = result.get('data', [])
        if not music_data:
            print("❌ 没有找到音乐数据")
            return False
        
        # 获取第一首歌曲
        first_song = music_data[0] if isinstance(music_data, list) else music_data
        
        print(f"\n🎵 音乐信息:")
        print(f"   歌曲名: {first_song.get('song', '未知歌曲')}")
        print(f"   歌手: {first_song.get('singer', '未知歌手')}")
        print(f"   URL: {first_song.get('url', '未知URL')}")
        print(f"   专辑封面: {first_song.get('image', '没有封面图片')}")
        
        # 验证专辑封面
        if 'image' in first_song and first_song['image']:
            print(f"\n📸 专辑封面URL: {first_song['image']}")
            
            # 检查封面URL是否有效
            try:
                cover_response = requests.head(first_song['image'], allow_redirects=True, timeout=5)
                if cover_response.status_code == 200:
                    print(f"✅ 专辑封面URL有效，状态码: {cover_response.status_code}")
                    print(f"   内容类型: {cover_response.headers.get('Content-Type', '未知')}")
                else:
                    print(f"⚠️  专辑封面URL可能无效，状态码: {cover_response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ 专辑封面URL请求失败: {e}")
        else:
            print(f"\n⚠️  没有专辑封面信息，将使用默认占位图")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except json.JSONDecodeError:
        print("❌ JSON解析失败")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_placeholder_image():
    """测试默认占位图是否存在"""
    print(f"\n🖼️  测试默认占位图:")
    placeholder_path = 'd:/Users/Git/DaipChatRoom/static/img/music-placeholder.svg'
    
    if os.path.exists(placeholder_path):
        print(f"✅ 默认占位图存在: {placeholder_path}")
        
        # 检查文件大小
        file_size = os.path.getsize(placeholder_path)
        print(f"   文件大小: {file_size} 字节")
        return True
    else:
        print(f"❌ 默认占位图不存在: {placeholder_path}")
        return False

def main():
    """主测试函数"""
    print("=== 音乐专辑封面显示测试 ===")
    
    success = True
    
    # 测试音乐搜索API
    if not test_music_api():
        success = False
    
    # 测试默认占位图
    if not test_placeholder_image():
        success = False
    
    print("\n" + "="*40)
    if success:
        print("🎉 所有测试通过！专辑封面显示功能正常工作。")
    else:
        print("❌ 部分测试失败，请检查问题。")

if __name__ == "__main__":
    main()
