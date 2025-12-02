from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import re
import openai
from threading import Thread
import time
import sqlite3
import datetime
import requests
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'daip_chat_room_secret_key'
app.config['DATABASE'] = 'chat.db'
socketio = SocketIO(app, cors_allowed_origins="*")

# 数据库初始化函数
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 删除旧的users表（如果存在）
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        status TEXT DEFAULT 'offline',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # 创建消息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message_type TEXT NOT NULL, -- normal, ai, movie, system
        content TEXT NOT NULL,
        additional_data TEXT, -- 存储AI回复或电影链接等额外数据
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# 获取数据库连接
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# 获取用户ID
def get_user_id(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user['id'] if user else None

# 获取用户信息
def get_user_info(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# 更新用户状态
def update_user_status(username, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET status = ? WHERE username = ?', (status, username))
    conn.commit()
    conn.close()

# 保存消息到数据库
def save_message(username, message_type, content, additional_data=None):
    user_id = get_user_id(username)
    if not user_id:
        return
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO messages (user_id, message_type, content, additional_data) VALUES (?, ?, ?, ?)',
            (user_id, message_type, content, additional_data)
        )
        conn.commit()
    except Exception as e:
        print(f"消息存储失败: {str(e)}")
    finally:
        conn.close()

# 在应用启动时初始化数据库
init_db()

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

# MD5加密函数
def md5_hash(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()

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

# 天气API配置
WEATHER_API_KEY = '7b96a8e86f1307d1'
WEATHER_API_URL = 'https://v2.xxapi.cn/api/weather'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm_password = request.form['confirm_password'].strip()
        
        # 验证输入
        if not username or not password:
            return render_template('register.html', error='用户名和密码不能为空')
        
        if password != confirm_password:
            return render_template('register.html', error='两次输入的密码不一致')
        
        if len(password) < 6:
            return render_template('register.html', error='密码长度不能少于6位')
        
        # 检查用户名是否已存在
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return render_template('register.html', error='用户名已存在')
        
        # 加密密码
        hashed_password = md5_hash(password)
        
        # 插入新用户
        try:
            cursor.execute(
                'INSERT INTO users (username, password, status) VALUES (?, ?, ?)',
                (username, hashed_password, 'offline')
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login', success='注册成功，请登录'))
        except Exception as e:
            conn.close()
            print(f"用户注册失败: {str(e)}")
            return render_template('register.html', error='注册失败，请稍后重试')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    config = load_config()
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        server = request.form['server']
        
        if not username or not password:
            return render_template('login.html', error='请输入用户名和密码', servers=config['servers'])
        
        # 验证用户身份
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return render_template('login.html', error='用户名不存在', servers=config['servers'])
        
        if user['password'] != md5_hash(password):
            return render_template('login.html', error='密码错误', servers=config['servers'])
        
        if username in online_users:
            return render_template('login.html', error='用户已在线', servers=config['servers'])
        
        # 登录成功，更新用户状态
        update_user_status(username, 'online')
        
        session['username'] = username
        session['server'] = server
        session['user_id'] = user['id']
        session['is_admin'] = user['is_admin']
        return redirect(url_for('chat'))
    
    return render_template('login.html', servers=config['servers'], success=request.args.get('success'))

@app.route('/chat')
def chat():
    if 'nickname' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', nickname=session['nickname'])

@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        update_user_status(username, 'offline')
        session.pop('username', None)
        if username in online_users:
            del online_users[username]
            socketio.emit('user_left', {'username': username}, room=room_name)
            socketio.emit('update_users', list(online_users.keys()), room=room_name)
    return redirect(url_for('login'))

# 用户数据管理功能
@app.route('/admin/users', methods=['GET'])
def get_all_users():
    """获取所有用户信息"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    users = db.execute('SELECT id, username, status, is_admin, created_at FROM users').fetchall()
    return render_template('users.html', users=users, current_user=session['username'])

@app.route('/admin/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    """获取单个用户详情"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT id, username, status, is_admin, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return "用户不存在", 404
    
    return render_template('user_details.html', user=user, current_user=session['username'])

@app.route('/admin/users/change_password', methods=['POST'])
def change_password():
    """修改密码"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    # 验证新密码和确认密码
    if new_password != confirm_password:
        return "新密码和确认密码不一致", 400
    
    # 验证原密码
    db = get_db()
    user = db.execute('SELECT password FROM users WHERE username = ?', (username,)).fetchone()
    if not user or user['password'] != md5_hash(old_password):
        return "原密码错误", 400
    
    # 更新密码
    db.execute('UPDATE users SET password = ? WHERE username = ?', (md5_hash(new_password), username))
    db.commit()
    
    return "密码修改成功"

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """删除用户（仅管理员可操作）"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # 检查当前用户是否为管理员
    db = get_db()
    current_user = db.execute('SELECT is_admin FROM users WHERE username = ?', (session['username'],)).fetchone()
    if not current_user or not current_user['is_admin']:
        return "无权限执行此操作", 403
    
    # 不能删除自己
    user_to_delete = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user_to_delete:
        return "用户不存在", 404
    
    if user_to_delete['username'] == session['username']:
        return "不能删除自己", 400
    
    # 删除用户
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    
    return redirect(url_for('get_all_users'))

@socketio.on('connect')
def handle_connect():
    if 'nickname' not in session:
        return False
    
    nickname = session['nickname']
    online_users[nickname] = request.sid
    join_room(room_name)
    
    # 保存用户加入消息
    save_message(nickname, 'system', f'{nickname} 加入了聊天室')
    
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
        
        # 保存用户离开消息
        save_message(nickname, 'system', f'{nickname} 离开了聊天室')
        
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
    
    # 处理@查天气指令
    weather_match = re.search(r'@查天气\s+(.+)', message)
    if weather_match:
        city_name = weather_match.group(1)
        
        # 显示正在查询的状态
        emit('weather_message', {
            'nickname': nickname, 
            'city': city_name, 
            'content': f'正在查询{city_name}的天气...',
            'is_typing': True
        }, room=room_name)
        
        # 启动后台任务处理天气请求
        socketio.start_background_task(handle_weather_request, nickname, city_name, room_name, message)
        return
    
    # 处理@电影指令
    movie_match = re.search(r'@电影\s+(https?://\S+)', message)
    if movie_match:
        movie_url = movie_match.group(1)
        # 对URL进行编码
        import urllib.parse
        encoded_url = urllib.parse.quote(movie_url)
        # 生成解析后的URL
        parsed_url = f'http://jx.playerjy.com/?url={encoded_url}'
        
        # 保存电影消息
        additional_data = json.dumps({'url': parsed_url, 'original_url': movie_url})
        save_message(nickname, 'movie', message, additional_data)
        
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
                # 保存AI消息
                additional_data = json.dumps({'reply': accumulated_response})
                save_message(nickname, 'ai', ai_message, additional_data)
                
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
                error_response = f'抱歉，发生错误：{str(e)}'
                # 保存AI错误消息
                additional_data = json.dumps({'reply': error_response})
                save_message(nickname, 'ai', ai_message, additional_data)
                
                socketio.emit('ai_message', {
                    'nickname': nickname,
                    'message': ai_message,
                    'reply': error_response,
                    'is_typing': False
                }, room=room_name)
        
        # 使用socketio.start_background_task处理AI请求
        socketio.start_background_task(handle_ai_request)
        return
    
    # 处理@听音乐指令
    music_match = re.search(r'@听音乐\s+(.+)', message)
    if music_match:
        song_name = music_match.group(1)
        
        # 显示正在搜索的状态
        emit('music_message', {
            'nickname': nickname, 
            'song_name': song_name, 
            'content': f'正在搜索歌曲：{song_name}...',
            'is_typing': True
        }, room=room_name)
        
        # 启动后台任务处理音乐请求
        socketio.start_background_task(handle_music_request, nickname, song_name, room_name, original_message=message)
        return
    
    # 处理@查新闻指令
    if '@查新闻' in message:
        # 显示正在搜索的状态
        emit('news_message', {
            'nickname': nickname, 
            'news_list': [],
            'is_typing': True
        }, room=room_name)
        
        # 启动后台任务处理新闻请求
        socketio.start_background_task(handle_news_request, nickname, room_name, original_message=message)
        return
    
    # 正常消息
    save_message(nickname, 'normal', message)
    emit('new_message', {'nickname': nickname, 'message': message}, room=room_name)

# 定义处理天气请求的函数
def handle_weather_request(nickname, city_name, room_name, message):
    try:
        # 调用天气API
        params = {
            'key': WEATHER_API_KEY,
            'city': city_name
        }
        
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        
        # 解析API响应
        weather_data = response.json()
        print(f"天气API响应: {weather_data}")
        
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
            
            # 获取天气类型
            weather_type = ""  # 默认空
            if forecast_list:
                today = forecast_list[0]
                weather_type = today.get('weather', '')
            
            # 使用流式方式返回天气结果
            accumulated_reply = ""
            for char in weather_reply:
                accumulated_reply += char
                # 延迟一点时间以模拟流式效果
                time.sleep(0.03)
                # 发送当前累积的响应
                socketio.emit('weather_message', {
                    'nickname': nickname, 
                    'city': city_name, 
                    'content': accumulated_reply,
                    'is_typing': True,
                    'weather_type': weather_type
                }, room=room_name)
        else:
            # API调用失败
            weather_reply = f"查询{city_name}天气失败: {weather_data.get('msg', '未知错误')}"
            weather_type = ""
            
            # 使用流式方式返回错误信息
            accumulated_reply = ""
            for char in weather_reply:
                accumulated_reply += char
                time.sleep(0.03)
                socketio.emit('weather_message', {
                    'nickname': nickname, 
                    'city': city_name, 
                    'content': accumulated_reply,
                    'is_typing': True,
                    'weather_type': weather_type
                }, room=room_name)
        
        # 保存天气消息
        additional_data = json.dumps({'city': city_name, 'content': weather_reply, 'weather_type': weather_type})
        save_message(nickname, 'weather', message, additional_data)
        
        # 发送最终完成的响应
        socketio.emit('weather_message', {
            'nickname': nickname, 
            'city': city_name, 
            'content': accumulated_reply,
            'is_typing': False,
            'weather_type': weather_type
        }, room=room_name)
        
    except Exception as e:
        # 发生错误时发送错误信息
        print(f"天气请求错误: {str(e)}")
        error_response = f'查询{city_name}天气时发生错误: {str(e)}'
        
        # 保存错误消息
        additional_data = json.dumps({'city': city_name, 'error': str(e)})
        save_message(nickname, 'weather', message, additional_data)
        
        socketio.emit('weather_message', {
            'nickname': nickname, 
            'city': city_name, 
            'content': error_response,
            'is_typing': False
        }, room=room_name)
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
                # 保存AI消息
                additional_data = json.dumps({'reply': accumulated_response})
                save_message(nickname, 'ai', ai_message, additional_data)
                
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
                error_response = f'抱歉，发生错误：{str(e)}'
                # 保存AI错误消息
                additional_data = json.dumps({'reply': error_response})
                save_message(nickname, 'ai', ai_message, additional_data)
                
                socketio.emit('ai_message', {
                    'nickname': nickname,
                    'message': ai_message,
                    'reply': error_response,
                    'is_typing': False
                }, room=room_name)
        
        # 使用socketio.start_background_task处理AI请求
        socketio.start_background_task(handle_ai_request)
        return
    
    # 正常消息
    save_message(nickname, 'normal', message)
    emit('new_message', {'nickname': nickname, 'message': message}, room=room_name)

@socketio.on('get_servers')
def get_servers():
    config = load_config()
    emit('servers_list', config['servers'])

# 获取历史消息API
@app.route('/api/history')
def get_history():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询消息及其对应的用户昵称
        cursor.execute('''
        SELECT m.id, u.nickname, m.message_type, m.content, m.additional_data, m.created_at
        FROM messages m
        JOIN users u ON m.user_id = u.id
        ORDER BY m.created_at ASC
        ''')
        
        messages = []
        for row in cursor.fetchall():
            message_data = {
                'id': row['id'],
                'nickname': row['nickname'],
                'message_type': row['message_type'],
                'content': row['content'],
                'created_at': row['created_at']
            }
            
            # 解析额外数据
            if row['additional_data']:
                try:
                    message_data['additional_data'] = json.loads(row['additional_data'])
                except json.JSONDecodeError:
                    message_data['additional_data'] = row['additional_data']
            
            messages.append(message_data)
        
        conn.close()
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 删除历史消息API
@app.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 清空消息表
        cursor.execute('DELETE FROM messages')
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '历史记录已成功删除'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# SocketIO获取历史消息
@socketio.on('get_history')
def handle_get_history():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询消息及其对应的用户昵称
        cursor.execute('''
        SELECT m.id, u.nickname, m.message_type, m.content, m.additional_data, m.created_at
        FROM messages m
        JOIN users u ON m.user_id = u.id
        ORDER BY m.created_at ASC
        ''')
        
        messages = []
        for row in cursor.fetchall():
            message_data = {
                'id': row['id'],
                'nickname': row['nickname'],
                'message_type': row['message_type'],
                'content': row['content'],
                'created_at': row['created_at']
            }
            
            # 解析额外数据
            if row['additional_data']:
                try:
                    message_data['additional_data'] = json.loads(row['additional_data'])
                except json.JSONDecodeError:
                    message_data['additional_data'] = row['additional_data']
            
            messages.append(message_data)
        
        conn.close()
        emit('history_data', {'messages': messages})
    except Exception as e:
        emit('history_error', {'error': str(e)})

# 定义处理音乐请求的函数
def handle_music_request(nickname, song_name, room_name, original_message):
    import requests
    import json
    
    try:
        # 调用音乐搜索API
        api_url = "https://v2.xxapi.cn/api/kugousearch"
        api_key = "9769a9e12ac01f8a"
        
        # 调用音乐搜索API
        # 尝试多种参数名组合
        test_params_list = [
            {"key": api_key, "music": song_name},  # 主要尝试（已验证成功的参数组合）
            {"key": api_key, "name": song_name},      # 备用参数名
            {"key": api_key, "q": song_name},       # 备用参数名
            {"key": api_key, "keyword": song_name},  # 备用参数名
            {"key": api_key, "songname": song_name}  # 备用参数名
        ]
        
        music_data = None
        
        for i, test_params in enumerate(test_params_list):
            print(f"\n尝试参数组合 {i+1}/{len(test_params_list)}: {test_params}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            try:
                response = requests.get(api_url, params=test_params, headers=headers, timeout=10)
                print(f"响应状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
                # 检查响应是否为空
                if not response.text:
                    print("API响应为空")
                    continue
                
                # 尝试解析JSON
                data = response.json()
                print(f"解析后的JSON: {data}")
                
                # 检查API返回的状态码
                if data.get('code') == 200:  # API返回200表示成功
                    music_data = data
                    print(f"找到有效响应，使用参数: {test_params}")
                    break
                else:
                    print(f"API返回错误状态: {data.get('msg', '未知错误')}")
                    
            except requests.exceptions.Timeout:
                print("请求超时")
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {str(e)}")
            except json.JSONDecodeError:
                print(f"JSON解析失败: {response.text}")
        
        # 如果所有参数组合都失败
        if music_data is None:
            raise ValueError("所有API参数组合都失败")
        print(f"音乐API响应: {music_data}")
        
        # 处理搜索结果
        print(f"音乐API响应状态码: {music_data.get('code')}")
        print(f"音乐API响应数据: {music_data}")
        
        # 检查API响应状态
        if music_data.get('code') == 200:
            # 获取音乐数据
            music_info = music_data.get('data', {})
            
            # 发送流式响应
            accumulated_response = ""
            for char in f'搜索到歌曲：{song_name}':
                accumulated_response += char
                socketio.emit('music_message', {
                    'nickname': nickname, 
                    'song_name': song_name, 
                    'content': accumulated_response,
                    'is_typing': True,
                    'music_info': None
                }, room=room_name)
                time.sleep(0.03)
            
            # 发送最终结果 - 使用列表中的第一首歌曲
            first_song = music_info[0] if isinstance(music_info, list) and len(music_info) > 0 else music_info
            socketio.emit('music_message', {
                'nickname': nickname, 
                'song_name': song_name, 
                'content': f'搜索到歌曲：{song_name}',
                'is_typing': False,
                'music_info': first_song
            }, room=room_name)
            
            # 保存音乐消息
            additional_data = json.dumps({
                'song_name': song_name,
                'music_info': first_song
            })
            save_message(nickname, 'music', original_message, additional_data)
        else:
            # 搜索失败
            error_message = music_data.get('msg', '搜索失败')
            socketio.emit('music_message', {
                'nickname': nickname, 
                'song_name': song_name, 
                'content': f'搜索歌曲失败：{error_message}',
                'is_typing': False,
                'music_info': None
            }, room=room_name)
            
            # 保存错误消息
            additional_data = json.dumps({
                'song_name': song_name,
                'error': error_message
            })
            save_message(nickname, 'music', original_message, additional_data)
            
    except Exception as e:
        print(f"音乐请求错误: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细的错误栈
        
        # 发送错误信息
        socketio.emit('music_message', {
            'nickname': nickname, 
            'song_name': song_name, 
            'content': f'搜索歌曲失败：{str(e)}',
            'is_typing': False,
            'music_info': None
        }, room=room_name)
        
        # 保存错误消息
        additional_data = json.dumps({
            'song_name': song_name,
            'error': str(e)
        })
        save_message(nickname, 'music', original_message, additional_data)

# 定义处理新闻请求的函数
def handle_news_request(nickname, room_name, original_message):
    import requests
    import json
    import time
    
    try:
        # 调用百度热点新闻API
        api_url = "https://v2.xxapi.cn/api/baiduhot"
        api_key = "9769a9e12ac01f8a"
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 调用新闻API
        response = requests.get(api_url, params={'key': api_key}, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析API响应
        news_data = response.json()
        print(f"新闻API响应: {news_data}")
        
        # 检查API返回的状态码
        if news_data.get('code') == 200:
            # 获取前10条热点新闻
            news_list = news_data.get('data', [])[:10]
            
            # 使用SSE协议发送新闻数据
            accumulated_response = ""
            for char in "正在获取新闻...":
                accumulated_response += char
                socketio.emit('news_message', {
                    'nickname': nickname, 
                    'news_list': [],
                    'is_typing': True
                }, room=room_name)
                time.sleep(0.03)
            
            # 发送最终结果
            socketio.emit('news_message', {
                'nickname': nickname, 
                'news_list': news_list,
                'is_typing': False
            }, room=room_name)
            
            # 保存新闻消息
            additional_data = json.dumps({'news_list': news_list})
            save_message(nickname, 'news', original_message, additional_data)
        else:
            # API返回错误
            error_message = f"新闻API返回错误: {news_data.get('msg', '未知错误')}"
            print(error_message)
            socketio.emit('news_message', {
                'nickname': nickname, 
                'news_list': [],
                'is_typing': False
            }, room=room_name)
            socketio.emit('system_message', f"{nickname} 新闻查询失败: {error_message}", room=room_name)
            
    except Exception as e:
        # 发生错误时发送错误信息
        print(f"新闻请求错误: {str(e)}")
        socketio.emit('news_message', {
            'nickname': nickname, 
            'news_list': [],
            'is_typing': False
        }, room=room_name)
        socketio.emit('system_message', f"{nickname} 新闻查询失败: {str(e)}", room=room_name)



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)