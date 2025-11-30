// 连接到WebSocket服务器
const socket = io();

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
    displayAIMessage(data.nickname, data.message, data.reply);
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

// 显示AI消息
function displayAIMessage(nickname, message, reply) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', 'ai');
    
    const now = new Date();
    const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-nickname">${nickname} [AI对话]</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content">
            <strong>问:</strong> ${escapeHtml(message)}<br>
            <strong>答:</strong> ${escapeHtml(reply)}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

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

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 自动获取焦点
    messageInput.focus();
    
    // 初始化Emoji选择器
    initEmojiPicker();
});