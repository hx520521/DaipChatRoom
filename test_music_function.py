import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from app import app, socketio
import threading
import time

# 模拟调用音乐搜索功能
def test_music_search():
    print("开始测试音乐搜索功能...")
    
    # 导入handle_music_request函数
    from app import handle_music_request
    
    try:
        # 调用音乐搜索函数
        handle_music_request(
            nickname="测试用户",
            song_name="小幸运",
            room_name="global",
            original_message="@听音乐 小幸运"
        )
        print("✅ 音乐搜索功能测试成功！")
    except Exception as e:
        print(f"❌ 音乐搜索功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 启动测试
    test_music_search()
