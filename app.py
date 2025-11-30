from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'daip_chat_room_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

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
    if message.startswith('@川小农'):
        ai_message = message[4:].strip()
        emit('ai_message', {'nickname': nickname, 'message': ai_message, 'reply': '这是AI回复：' + ai_message}, room=room_name)
        return
    
    # 正常消息
    emit('new_message', {'nickname': nickname, 'message': message}, room=room_name)

@socketio.on('get_servers')
def get_servers():
    config = load_config()
    emit('servers_list', config['servers'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)