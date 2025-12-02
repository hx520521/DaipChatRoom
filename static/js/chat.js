// 连接到WebSocket服务器
const socket = io('http://127.0.0.1:5000');

// DOM元素
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const usersList = document.getElementById('usersList');
const usersCount = document.querySelector('.sidebar-header h3');
const emojiBtn = document.getElementById('emojiBtn');
const emojiPicker = document.getElementById('emojiPicker');
const emojiGrid = document.querySelector('.emoji-grid');

// 常用Emoji列表
const emojis = [
    '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣',
    '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰',
    '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜',
    '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏',
    '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣',
    '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠',
    '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨',
    '😰', '😥', '😓', '🤗', '🤔', '🤭', '🤫', '🤥',
    '😶', '😐', '😑', '😬', '🙄', '😯', '😦', '😧',
    '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐',
    '🥴', '🤢', '🤮', '🤧', '😷', '🤒', '🤕', '🤑',
    '🤠', '😈', '👿', '👹', '👺', '🤡', '💩', '👻',
    '💀', '☠️', '👽', '👾', '🤖', '🎃', '😺', '😸',
    '😹', '😻', '😼', '😽', '🙀', '😿', '😾', '👋',
    '🤚', '🖐️', '✋', '🖖', '👌', '🤌', '🤏', '✌️',
    '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕',
    '👇', '☝️', '👍', '👎', '👊', '✊', '🤛', '🤜',
    '👏', '🙌', '👐', '🤲', '🤝', '🙏', '✍️', '💅',
    '🤳', '💪', '🦾', '🦿', '🦵', '🦶', '👂', '🦻',
    '👃', '🧠', '🦷', '🦴', '👀', '👁️', '👅', '👄'
];

// 初始化Emoji选择器
function initEmojiPicker() {
    emojis.forEach(emoji => {
        const span = document.createElement('span');
        span.textContent = emoji;
        span.addEventListener('click', () => insertEmoji(emoji));
        emojiGrid.appendChild(span);
    });
}

// 发送消息
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        socket.emit('send_message', { message });
        messageInput.value = '';
    }
}

// 接收新消息
socket.on('new_message', (data) => {
    displayMessage(data.nickname, data.message, 'user');
});

// 接收系统消息
socket.on('system_message', (message) => {
    displaySystemMessage(message);
});

// 接收电影消息
socket.on('movie_message', (data) => {
    displayMovieMessage(data.nickname, data.url, data.original_url);
});

// 接收AI消息
socket.on('ai_message', (data) => {
    displayAIMessage(data.nickname, data.message, data.reply, data.is_typing);
});

// 接收天气消息
    socket.on('weather_message', (data) => {
        const { nickname, city, content, is_typing, weather_type } = data;
        displayWeatherMessage(nickname, city, content, is_typing, null, weather_type);
    });
    
    // 接收音乐消息
    socket.on('music_message', function(data) {
        console.log('Received music_message:', data);
        const { nickname, song_name, content, is_typing, music_info } = data;
        displayMusicMessage(nickname, song_name, content, is_typing, music_info);
    });
    
    // 接收新闻消息
    socket.on('news_message', (data) => {
        console.log('Received news_message:', data);
        const { nickname, news_list } = data;
        displayNewsMessage(nickname, news_list);
    });

// 更新在线用户列表
socket.on('update_users', (users) => {
    updateUsersList(users);
});

// 用户加入
socket.on('user_joined', (data) => {
    displaySystemMessage(`${data.nickname} 加入了聊天室`);
});

// 用户离开
socket.on('user_left', (data) => {
    displaySystemMessage(`${data.nickname} 离开了聊天室`);
});

// 显示消息
function displayMessage(nickname, message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', type);
    
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">${nickname}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 显示系统消息
function displaySystemMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'system');
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 显示电影消息
function displayMovieMessage(nickname, url, original_url) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'movie');
    
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">${nickname} [电影分享]</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">
            <a href="${original_url}" target="_blank" style="word-break: break-all; font-size: 12px; display: block; margin-bottom: 10px;">${original_url}</a>
            <iframe src="${url}" width="400" height="400" frameborder="0" allowfullscreen sandbox="allow-same-origin allow-scripts allow-popups allow-forms"></iframe>
            <div class="movie-error" style="display: none; color: red; font-size: 12px; margin-top: 5px;">
                视频加载失败，请尝试点击原始链接观看
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // 添加iframe加载错误处理
    const iframe = messageDiv.querySelector('iframe');
    const errorDiv = messageDiv.querySelector('.movie-error');
    
    // 添加调试信息
    console.log('尝试加载视频:', { url, original_url });
    
    iframe.addEventListener('error', (e) => {
        console.error('视频加载错误:', e);
        errorDiv.style.display = 'block';
    });
    
    iframe.addEventListener('load', () => {
        console.log('视频加载成功');
    });
}

// 根据天气类型设置聊天背景颜色
function setChatBackground(weatherType) {
    const chatContainer = document.querySelector('.chat-container');
    if (!chatContainer) return;
    
    // 移除所有可能的天气类
    chatContainer.classList.remove('weather-sunny', 'weather-cloudy', 'weather-rainy', 'weather-snowy', 'weather-windy', 'weather-foggy');
    
    // 根据天气类型添加对应的类
    if (weatherType.includes('晴') || weatherType.includes('多云')) {
        chatContainer.classList.add('weather-sunny');
    } else if (weatherType.includes('阴')) {
        chatContainer.classList.add('weather-cloudy');
    } else if (weatherType.includes('雨') || weatherType.includes('雷')) {
        chatContainer.classList.add('weather-rainy');
    } else if (weatherType.includes('雪')) {
        chatContainer.classList.add('weather-snowy');
    } else if (weatherType.includes('风')) {
        chatContainer.classList.add('weather-windy');
    } else if (weatherType.includes('雾') || weatherType.includes('霾')) {
        chatContainer.classList.add('weather-foggy');
    }
}

// 获取当前时间的辅助函数
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// 显示音乐消息
function displayMusicMessage(nickname, song_name, content, is_typing = false, music_info = null) {
    console.log('displayMusicMessage called with:', { nickname, song_name, content, is_typing, music_info });
    
    // 检查输入参数是否有效
    if (!nickname || !song_name) {
        console.error('Invalid music message parameters:', { nickname, song_name, content });
        return;
    }
    
    // 查找是否已存在此消息的容器
    let messageDiv = null;
    const messageId = `music-${nickname}-${song_name}`;
    
    // 如果是打字状态更新，找到对应消息
    if (is_typing) {
        messageDiv = document.getElementById(messageId);
    }
    
    // 如果不存在，创建新的消息容器
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = 'message music';
        
        // 消息头部
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        
        const nicknameSpan = document.createElement('span');
        nicknameSpan.className = 'message-nickname';
        nicknameSpan.textContent = nickname;
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = getCurrentTime();
        
        headerDiv.appendChild(nicknameSpan);
        headerDiv.appendChild(timeSpan);
        
        // 消息内容
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        
        // 添加到聊天区域
        document.getElementById('chatMessages').appendChild(messageDiv);
    }
    
    // 更新消息内容
    const contentDiv = messageDiv.querySelector('.message-content');
    if (is_typing) {
        // 显示搜索状态
        contentDiv.innerHTML = `<p>${content}</p>`;
    } else if (music_info) {
        // 显示音乐卡片
        contentDiv.innerHTML = `
            <div class="music-card">
                <img src="${music_info.image ? music_info.image : '/static/img/music-placeholder.svg'}" alt="专辑封面" class="music-cover" onerror="this.src='/static/img/music-placeholder.svg'">
                <div class="music-info">
                    <h4 class="music-title">${music_info.title || music_info.song || song_name || '未知歌曲'}</h4>
                    <p class="music-artist">${music_info.artist || music_info.singer || '未知歌手'}</p>
                    <p class="music-album">${music_info.album || music_info.song || '未知专辑'}</p>
                </div>
                <div class="music-player">
                    <audio id="audio-${messageId}" src="${music_info.url}" controls></audio>
                </div>
                <div class="music-controls">
                    <button class="play-btn" onclick="togglePlay('${messageId}')">▶️</button>
                    <button class="pause-btn" onclick="pauseAudio('${messageId}')">⏸️</button>
                    <button class="stop-btn" onclick="stopAudio('${messageId}')">⏹️</button>
                </div>
            </div>
        `;
    } else {
        // 显示错误信息
        contentDiv.innerHTML = `<p>${content}</p>`;
    }
    
    // 滚动到底部
    scrollToBottom();
}

// 音乐播放控制
function togglePlay(messageId) {
    const audio = document.getElementById(`audio-${messageId}`);
    if (audio.paused) {
        audio.play();
    } else {
        audio.pause();
    }
}

function pauseAudio(messageId) {
    const audio = document.getElementById(`audio-${messageId}`);
    audio.pause();
}

function stopAudio(messageId) {
    const audio = document.getElementById(`audio-${messageId}`);
    audio.pause();
    audio.currentTime = 0;
}

// 显示天气消息
function displayWeatherMessage(nickname, city, content, is_typing = false, time = null, weather_type = '') {
    // 添加调试日志
    console.log('displayWeatherMessage called with:', { nickname, city, content, is_typing, time, weather_type });
    
    // 检查输入参数是否有效
    if (!nickname || !city) {
        console.error('Invalid weather message parameters:', { nickname, city, content });
        return;
    }
    
    // 如果天气类型有效且不是打字状态，则设置背景
    if (weather_type && !is_typing) {
        setChatBackground(weather_type);
    }
    
    // 查找是否已存在此消息的容器
    let messageDiv = null;
    const existingMessages = document.querySelectorAll('.message.weather');
    
    // 尝试找到相同用户和城市的消息
    for (let msg of existingMessages) {
        const contentDiv = msg.querySelector('.message-content');
        if (contentDiv) {
            const cityIndicator = contentDiv.querySelector('.weather-city');
            if (cityIndicator && cityIndicator.textContent.includes(city)) {
                messageDiv = msg;
                console.log('Found existing weather message:', messageDiv);
                break;
            }
        }
    }
    
    // 如果不存在，则创建新的消息容器
    if (!messageDiv) {
        console.log('Creating new weather message container');
        messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'weather');
        
        // 使用传入的时间或当前时间
        if (!time) {
            const now = new Date();
            time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-nickname">${nickname} [天气查询]</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">
                <div class="weather-city">${city}</div>
                <div class="weather-content">${escapeHtml(content)}</div>
                <div class="weather-typing" style="display: none;">...</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        console.log('Added new weather message to chatMessages');
    } else {
        // 更新现有消息的内容
        const weatherContentElement = messageDiv.querySelector('.weather-content');
        if (weatherContentElement) {
            weatherContentElement.textContent = content;
            console.log('Updated existing weather message content:', content);
        } else {
            console.error('Could not find weather-content element in existing message');
        }
        
        // 更新时间如果提供了
        if (time) {
            const timeElement = messageDiv.querySelector('.message-time');
            if (timeElement) {
                timeElement.textContent = time;
            }
        }
    }
    
    // 处理打字状态
    const typingIndicator = messageDiv.querySelector('.weather-typing');
    if (typingIndicator) {
        if (is_typing) {
            typingIndicator.style.display = 'inline';
            console.log('Set weather typing indicator to visible');
        } else {
            typingIndicator.style.display = 'none';
            console.log('Set weather typing indicator to hidden');
        }
    } else {
        console.error('Could not find weather-typing element');
    }
    
    scrollToBottom();
    console.log('displayWeatherMessage completed');
}

// 显示AI消息
function displayAIMessage(nickname, message, reply, is_typing = false) {
    // 添加调试日志
    console.log('displayAIMessage called with:', { nickname, message, reply, is_typing });
    
    // 检查输入参数是否有效
    if (!nickname || !message) {
        console.error('Invalid AI message parameters:', { nickname, message, reply });
        return;
    }
    
    // 查找是否已存在此消息的容器
    let messageDiv = null;
    const existingMessages = document.querySelectorAll('.message.ai');
    
    // 尝试找到相同用户和问题的消息
    for (let msg of existingMessages) {
        const content = msg.querySelector('.message-content');
        if (content) {
            const questionContainer = content.querySelector('.ai-question');
            if (questionContainer) {
                const questionText = questionContainer.textContent.replace('问:', '').trim();
                const escapedMessage = escapeHtml(message);
                if (questionText.includes(escapedMessage) || questionContainer.innerHTML.includes(escapedMessage)) {
                    messageDiv = msg;
                    console.log('Found existing message:', messageDiv);
                    break;
                }
            }
        }
    }
    
    // 如果不存在，则创建新的消息容器
    if (!messageDiv) {
        console.log('Creating new message container');
        messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'ai');
        
        const now = new Date();
        const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-nickname">${nickname} [AI对话]</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">
                <div class="ai-question">
                    <strong>问:</strong> ${escapeHtml(message)}
                </div>
                <div class="ai-answer">
                    <strong>答:</strong> <span class="ai-reply">${escapeHtml(reply)}</span>
                    <span class="typing-indicator" style="display: none;">...</span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        console.log('Added new message to chatMessages');
    } else {
        // 更新现有消息的回复内容
        const aiReplyElement = messageDiv.querySelector('.ai-reply');
        if (aiReplyElement) {
            aiReplyElement.textContent = reply;
            console.log('Updated existing message reply:', reply);
        } else {
            console.error('Could not find ai-reply element in existing message');
        }
    }
    
    // 处理打字状态
    const typingIndicator = messageDiv.querySelector('.typing-indicator');
    if (typingIndicator) {
        if (is_typing) {
            typingIndicator.style.display = 'inline';
            console.log('Set typing indicator to visible');
        } else {
            typingIndicator.style.display = 'none';
            console.log('Set typing indicator to hidden');
        }
    } else {
        console.error('Could not find typing-indicator element');
    }
    
    scrollToBottom();
    console.log('displayAIMessage completed');
}

// 获取历史记录按钮和删除历史记录按钮
const historyBtn = document.getElementById('historyBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

// 历史记录按钮点击事件
historyBtn.addEventListener('click', () => {
    // 滚动到聊天记录顶部
    chatMessages.scrollTop = 0;
});

// 删除历史记录按钮点击事件
clearHistoryBtn.addEventListener('click', () => {
    // 确认删除操作
    if (confirm('确定要删除所有历史记录吗？此操作不可恢复。')) {
        // 发送删除历史记录的请求
        fetch('/api/history/clear', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 清空聊天消息区域
                chatMessages.innerHTML = '';
                // 显示系统消息
                displaySystemMessage('历史记录已成功删除');
            } else {
                // 显示错误信息
                displaySystemMessage('删除历史记录失败：' + data.error);
            }
        })
        .catch(error => {
            console.error('删除历史记录请求失败:', error);
            displaySystemMessage('删除历史记录失败：网络错误');
        });
    }
});

// 更新用户列表
function updateUsersList(users) {
    usersList.innerHTML = '';
    usersCount.textContent = `在线用户 (${users.length})`;
    
    users.forEach(user => {
        const li = document.createElement('li');
        li.textContent = user;
        usersList.appendChild(li);
    });
}

// 滚动到底部
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 插入Emoji到输入框
function insertEmoji(emoji) {
    const input = messageInput;
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const value = input.value;
    
    // 在光标位置插入emoji
    input.value = value.substring(0, start) + emoji + value.substring(end);
    
    // 重新设置光标位置
    const newPosition = start + emoji.length;
    input.selectionStart = newPosition;
    input.selectionEnd = newPosition;
    
    // 聚焦输入框
    input.focus();
    
    // 关闭emoji选择器
    emojiPicker.classList.remove('show');
}

// 事件监听
sendBtn.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Emoji按钮点击事件
emojiBtn.addEventListener('click', () => {
    emojiPicker.classList.toggle('show');
});

// 点击外部区域关闭Emoji选择器
document.addEventListener('click', (e) => {
    if (!emojiPicker.contains(e.target) && e.target !== emojiBtn) {
        emojiPicker.classList.remove('show');
    }
});

// 自动调整输入框大小
function adjustTextareaHeight() {
    // 设置最小高度
    messageInput.style.height = 'auto';
    
    // 计算所需高度
    const textHeight = messageInput.scrollHeight;
    const minHeight = parseInt(window.getComputedStyle(messageInput).minHeight);
    const maxHeight = parseInt(window.getComputedStyle(messageInput).maxHeight);
    
    // 设置合适的高度
    messageInput.style.height = Math.min(Math.max(textHeight, minHeight), maxHeight) + 'px';
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 自动获取焦点
    messageInput.focus();
    
    // 初始化Emoji选择器
    initEmojiPicker();
    
    // 添加输入框事件监听
    messageInput.addEventListener('input', adjustTextareaHeight);
    messageInput.addEventListener('paste', adjustTextareaHeight);
    messageInput.addEventListener('change', adjustTextareaHeight);
    
    // 添加功能按钮事件监听
    const aiBtn = document.getElementById('aiBtn');
    const movieBtn = document.getElementById('movieBtn');
    const historyBtn = document.getElementById('historyBtn');
    
    aiBtn.addEventListener('click', () => {
        messageInput.value = '@川小农 ';
        messageInput.focus();
        adjustTextareaHeight();
    });
    
    movieBtn.addEventListener('click', () => {
        messageInput.value = '@电影 ';
        messageInput.focus();
        adjustTextareaHeight();
    });
    
    // 天气按钮点击事件
    const weatherBtn = document.getElementById('weatherBtn');
    if (weatherBtn) {
        weatherBtn.addEventListener('click', () => {
            messageInput.value = '@查天气 ';
            messageInput.focus();
            adjustTextareaHeight();
        });
    }
    
    // 音乐按钮点击事件
    const musicBtn = document.getElementById('musicBtn');
    if (musicBtn) {
        musicBtn.addEventListener('click', () => {
            messageInput.value = '@听音乐 ';
            messageInput.focus();
            adjustTextareaHeight();
        });
    }
    
    // 新闻按钮点击事件
    const newsBtn = document.getElementById('newsBtn');
    if (newsBtn) {
        newsBtn.addEventListener('click', () => {
            messageInput.value = '@查新闻';
            messageInput.focus();
            adjustTextareaHeight();
        });
    }
    
    // 历史记录按钮事件
    historyBtn.addEventListener('click', () => {
        loadHistoryMessages();
        historyBtn.textContent = '刷新历史';
        historyBtn.style.backgroundColor = '#4CAF50';
        setTimeout(() => {
            historyBtn.textContent = '历史记录';
            historyBtn.style.backgroundColor = '#2196F3';
        }, 1500);
    });
    
    // 页面加载时自动加载历史记录
    loadHistoryMessages();
});

// 加载历史消息
function loadHistoryMessages() {
    // 清空当前消息
    chatMessages.innerHTML = '';
    
    // 显示加载状态
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'system');
    loadingDiv.innerHTML = '<div class="message-content">正在加载历史记录...</div>';
    chatMessages.appendChild(loadingDiv);
    
    // 使用SocketIO获取历史消息
    socket.emit('get_history');
}

// 接收历史消息数据
socket.on('history_data', (data) => {
    // 清空当前消息
    chatMessages.innerHTML = '';
    
    if (data.messages && data.messages.length > 0) {
        data.messages.forEach(message => {
            displayHistoryMessage(message);
        });
        
        // 显示加载完成提示
        const loadCompleteDiv = document.createElement('div');
        loadCompleteDiv.classList.add('message', 'system');
        loadCompleteDiv.innerHTML = `<div class="message-content">已加载 ${data.messages.length} 条历史记录</div>`;
        chatMessages.appendChild(loadCompleteDiv);
    } else {
        // 显示无历史记录提示
        const noHistoryDiv = document.createElement('div');
        noHistoryDiv.classList.add('message', 'system');
        noHistoryDiv.innerHTML = '<div class="message-content">暂无历史记录</div>';
        chatMessages.appendChild(noHistoryDiv);
    }
    
    scrollToBottom();
});

// 处理历史消息显示错误
socket.on('history_error', (data) => {
    // 清空当前消息
    chatMessages.innerHTML = '';
    
    // 显示错误提示
    const errorDiv = document.createElement('div');
    errorDiv.classList.add('message', 'system');
    errorDiv.innerHTML = `<div class="message-content" style="color: red;">加载历史记录失败: ${data.error}</div>`;
    chatMessages.appendChild(errorDiv);
});

// 显示历史消息
function displayHistoryMessage(message) {
    const { nickname, message_type, content, additional_data, created_at } = message;
    
    // 解析创建时间
    const messageDate = new Date(created_at);
    const time = messageDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const date = messageDate.toLocaleDateString();
    const displayTime = `${date} ${time}`;
    
    switch (message_type) {
        case 'user_message':
            displayMessage(nickname, content, 'user', displayTime);
            break;
        case 'system_message':
            displaySystemMessage(content, displayTime);
            break;
        case 'movie_message':
            if (additional_data && additional_data.original_url) {
                displayMovieMessage(nickname, content, additional_data.original_url, displayTime);
            }
            break;
        case 'ai_message':
            if (additional_data && additional_data.question) {
                displayAIMessage(nickname, additional_data.question, content, false, displayTime);
            }
            break;
        case 'weather_message':
            if (additional_data && additional_data.city) {
                displayWeatherMessage(nickname, additional_data.city, content, false, displayTime);
            }
            break;
        case 'join_message':
            displaySystemMessage(`${nickname} 加入了聊天室`, displayTime);
            break;
        case 'leave_message':
            displaySystemMessage(`${nickname} 离开了聊天室`, displayTime);
            break;
        default:
            // 未知消息类型，作为普通消息显示
            displayMessage(nickname, content, 'user', displayTime);
            break;
    }
}

// 修改显示消息函数以支持自定义时间
function displayMessage(nickname, message, type, time = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', type);
    
    if (!time) {
        const now = new Date();
        time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">${nickname}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 修改显示系统消息函数以支持自定义时间
function displaySystemMessage(message, time = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'system');
    
    if (!time) {
        const now = new Date();
        time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">系统</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 显示新闻消息函数
function displayNewsMessage(nickname, news_list, time = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'news');
    
    // 只保留前10条新闻
    const top10News = news_list.slice(0, 10);
    
    let newsContent = '<ul class="news-list">';
    top10News.forEach((news, index) => {
        console.log(`处理第${index + 1}条新闻:`, news);
        
        // 全面清理所有可能包含重复1的字段
        const cleanTitle = news.title ? news.title.replace(/1+/g, '').trim() : '';
        const cleanDesc = news.desc ? news.desc.replace(/1+/g, '').trim() : '';
        const cleanHot = news.hot ? news.hot.replace(/1+/g, '').trim() : '';
        
        // 调试信息
        console.log(`清理后 - 标题: "${cleanTitle}", 描述: "${cleanDesc}", 热度: "${cleanHot}"`);
        
        newsContent += `
            <li class="news-item">
                <div class="news-index">${index + 1}</div>
                <div class="news-info">
                    <div class="news-title">
                        <a href="${news.url}" target="_blank" rel="noopener noreferrer">${cleanTitle}</a>
                    </div>
                    ${cleanDesc ? `<div class="news-desc">${cleanDesc}</div>` : ''}
                    <div class="news-hot">热度: ${cleanHot}</div>
                </div>
                ${news.img ? `<img src="${news.img}" alt="${cleanTitle}" class="news-img" />` : ''}
            </li>
        `;
    });
    newsContent += '</ul>';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">${nickname}</span>
        </div>
        <div class="message-content">
            ${newsContent}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 修改显示电影消息函数以支持自定义时间
function displayMovieMessage(nickname, url, original_url, time = null) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'movie');
    
    if (!time) {
        const now = new Date();
        time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">${nickname} [电影分享]</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">
            <a href="${original_url}" target="_blank" style="word-break: break-all; font-size: 12px; display: block; margin-bottom: 10px;">${original_url}</a>
            <iframe src="${url}" width="400" height="400" frameborder="0" allowfullscreen sandbox="allow-same-origin allow-scripts allow-popups allow-forms"></iframe>
            <div class="movie-error" style="display: none; color: red; font-size: 12px; margin-top: 5px;">
                视频加载失败，请尝试点击原始链接观看
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // 添加iframe加载错误处理
    const iframe = messageDiv.querySelector('iframe');
    const errorDiv = messageDiv.querySelector('.movie-error');
    
    // 添加调试信息
    console.log('尝试加载视频:', { url, original_url });
    
    iframe.addEventListener('error', (e) => {
        console.error('视频加载错误:', e);
        errorDiv.style.display = 'block';
    });
    
    iframe.addEventListener('load', () => {
        console.log('视频加载成功');
    });
}

// 修改显示AI消息函数以支持自定义时间
function displayAIMessage(nickname, message, reply, is_typing = false, time = null) {
    // 添加调试日志
    console.log('displayAIMessage called with:', { nickname, message, reply, is_typing, time });
    
    // 检查输入参数是否有效
    if (!nickname || !message) {
        console.error('Invalid AI message parameters:', { nickname, message, reply });
        return;
    }
    
    // 查找是否已存在此消息的容器
    let messageDiv = null;
    const existingMessages = document.querySelectorAll('.message.ai');
    
    // 尝试找到相同用户和问题的消息
    for (let msg of existingMessages) {
        const content = msg.querySelector('.message-content');
        if (content) {
            const questionContainer = content.querySelector('.ai-question');
            if (questionContainer) {
                const questionText = questionContainer.textContent.replace('问:', '').trim();
                const escapedMessage = escapeHtml(message);
                if (questionText.includes(escapedMessage) || questionContainer.innerHTML.includes(escapedMessage)) {
                    messageDiv = msg;
                    console.log('Found existing message:', messageDiv);
                    break;
                }
            }
        }
    }
    
    // 如果不存在，则创建新的消息容器
    if (!messageDiv) {
        console.log('Creating new message container');
        messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'ai');
        
        if (!time) {
            const now = new Date();
            time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-nickname">${nickname} [AI对话]</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">
                <div class="ai-question">
                    <strong>问:</strong> ${escapeHtml(message)}
                </div>
                <div class="ai-answer">
                    <strong>答:</strong> <span class="ai-reply">${escapeHtml(reply)}</span>
                    <span class="typing-indicator" style="display: none;">...</span>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        console.log('Added new message to chatMessages');
    } else {
        // 更新现有消息的回复内容
        const aiReplyElement = messageDiv.querySelector('.ai-reply');
        if (aiReplyElement) {
            aiReplyElement.textContent = reply;
            console.log('Updated existing message reply:', reply);
        } else {
            console.error('Could not find ai-reply element in existing message');
        }
    }
    
    // 处理打字状态
    const typingIndicator = messageDiv.querySelector('.typing-indicator');
    if (typingIndicator) {
        if (is_typing) {
            typingIndicator.style.display = 'inline';
            console.log('Set typing indicator to visible');
        } else {
            typingIndicator.style.display = 'none';
            console.log('Set typing indicator to hidden');
        }
    } else {
        console.error('Could not find typing-indicator element');
    }
    
    scrollToBottom();
    console.log('displayAIMessage completed');
}