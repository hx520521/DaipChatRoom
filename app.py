from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import re
import openai
from threading import Thread
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'daip_chat_room_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 配置OpenAI客户端
openai.api_key = "sk-qnefgnmlhjscyqapfjqklknpjiftbsuljfrjprckddthlzes"
openai.api_base = "https://api.siliconflow.cn/v1"
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

# 测试API连接的函数
def test_api_connection():
    try:
        print("测试API连接...")
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "你好"}
            ],
            max_tokens=10,
            temperature=0.7
        )
        print(f"API连接成功! 响应: {response}")
        return True
    except Exception as e:
        print(f"API连接失败: {str(e)}")
        return False

# 在应用启动时直接测试API连接
print("启动应用，准备测试API连接...")
test_api_connection()

# 加载配置文件
CONFIG_FILE = 'config.json'
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"servers": []}

# 全局变量
online_users = {}
room_name = 'general'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    config = load_config()
    if request.method == 'POST':
        nickname = request.form['nickname'].strip()
        server = request.form['server']
        
        if not nickname:
            return render_template('login.html', error='请输入昵称', servers=config['servers'])
        
        if nickname in online_users:
            return render_template('login.html', error='昵称已存在', servers=config['servers'])
        
        session['nickname'] = nickname
        session['server'] = server
        return redirect(url_for('chat'))
    
    return render_template('login.html', servers=config['servers'])

@app.route('/chat')
def chat():
    if 'nickname' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', nickname=session['nickname'])

@app.route('/logout')
def logout():
    nickname = session.pop('nickname', None)
    if nickname in online_users:
        del online_users[nickname]
        socketio.emit('user_left', {'nickname': nickname}, room=room_name)
        socketio.emit('update_users', list(online_users.keys()), room=room_name)
    return redirect(url_for('login'))

@socketio.on('connect')
def handle_connect():
    if 'nickname' not in session:
        return False
    
    nickname = session['nickname']
    online_users[nickname] = request.sid
    join_room(room_name)
    
    emit('user_joined', {'nickname': nickname}, room=room_name)
    emit('update_users', list(online_users.keys()), room=room_name)

@socketio.on('disconnect')
def handle_disconnect():
    nickname = None
    for user, sid in online_users.items():
        if sid == request.sid:
            nickname = user
            break
    
    if nickname:
        del online_users[nickname]
        leave_room(room_name)
        emit('user_left', {'nickname': nickname}, room=room_name)
        emit('update_users', list(online_users.keys()), room=room_name)
        emit('system_message', f'{nickname} 离开了聊天室')

@socketio.on('send_message')
def handle_message(data):
    if 'nickname' not in session:
        return
    
    message = data['message'].strip()
    if not message:
        return
    
    nickname = session['nickname']
    
    # 处理@电影指令
    movie_match = re.search(r'@电影\s+(https?://\S+)', message)
    if movie_match:
        movie_url = movie_match.group(1)
        # 对URL进行编码
        import urllib.parse
        encoded_url = urllib.parse.quote(movie_url)
        # 生成解析后的URL
        parsed_url = f'http://jx.playerjy.com/?url={encoded_url}'
        emit('movie_message', {'nickname': nickname, 'url': parsed_url, 'original_url': movie_url}, room=room_name)
        return
    
    # 处理@川小农指令
    if '@川小农' in message:
        # 提取@川小农后面的内容
        ai_message = message.split('@川小农')[1].strip()
        if not ai_message:
            ai_message = "你好，有什么可以帮你的吗？"
            # 发送提示消息
            emit('ai_message', {
                'nickname': nickname, 
                'message': "你好", 
                'reply': "你好，有什么可以帮你的吗？",
                'is_typing': False
            }, room=room_name)
            return
            
        # 显示正在思考的状态
        emit('ai_message', {
            'nickname': nickname, 
            'message': ai_message, 
            'reply': '',
            'is_typing': True
        }, room=room_name)
        
        # 启动异步任务处理AI请求
        def handle_ai_request():
            try:
                print(f"AI请求开始: {ai_message}")
                # 使用OpenAI API进行流式调用
                response = openai.ChatCompletion.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "你是一个智能聊天机器人，名叫川小农，帮助用户解答问题。"},
                        {"role": "user", "content": ai_message}
                    ],
                    stream=True,
                    max_tokens=1024,
                    temperature=0.7
                )
                
                print(f"AI响应开始")
                # 处理流式响应
                accumulated_response = ""
                for chunk in response:
                    print(f"收到AI响应块: {chunk}")
                    if chunk.choices[0].delta.content is not None:
                        accumulated_response += chunk.choices[0].delta.content
                        print(f"累积响应: {accumulated_response}")
                        # 发送当前累积的响应
                        socketio.emit('ai_message', {
                            'nickname': nickname, 
                            'message': ai_message, 
                            'reply': accumulated_response,
                            'is_typing': True
                        }, room=room_name)
                        # 模拟打字速度
                        time.sleep(0.05)
                
                print(f"AI响应完成")
                # 发送最终完成的响应
                socketio.emit('ai_message', {
                    'nickname': nickname, 
                    'message': ai_message, 
                    'reply': accumulated_response,
                    'is_typing': False
                }, room=room_name)
                
            except Exception as e:
                # 发生错误时发送错误信息
                print(f"AI请求错误: {str(e)}")
                socketio.emit('ai_message', {
                    'nickname': nickname,
                    'message': ai_message,
                    'reply': f'抱歉，发生错误：{str(e)}',
                    'is_typing': False
                }, room=room_name)
        
        # 使用socketio.start_background_task处理AI请求
        socketio.start_background_task(handle_ai_request)
        return
    
    # 正常消息
    emit('new_message', {'nickname': nickname, 'message': message}, room=room_name)

@socketio.on('get_servers')
def get_servers():
    config = load_config()
    emit('servers_list', config['servers'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)