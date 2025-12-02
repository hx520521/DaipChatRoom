# DaiP智能聊天室

一个基于Flask和Socket.IO的实时智能聊天室，支持视频播放、AI对话和用户管理功能。

## 功能特性

- ✅ **实时聊天**：基于WebSocket的即时消息传输
- ✅ **用户管理**：完整的用户注册、登录和管理系统
- ✅ **管理员功能**：用户列表查看、状态管理和权限控制
- ✅ **视频播放**：支持@电影指令播放网络视频
- ✅ **AI对话**：集成AI对话功能（@川小农）
- ✅ **表情支持**：内置表情选择器
- ✅ **响应式设计**：适配不同设备屏幕

## 技术栈

- **后端框架**：Flask (Python)
- **实时通信**：Socket.IO
- **前端技术**：HTML5, CSS3, JavaScript
- **模板引擎**：Jinja2
- **数据库**：SQLite
- **依赖管理**：Python虚拟环境

## 安装与运行

### 1. 克隆仓库

```bash
git clone https://github.com/hx520521/DaipChatRoom.git
cd DaipChatRoom
```

### 2. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install flask flask-socketio
```

### 3. 运行应用

```bash
python app.py
```

应用将在 http://localhost:5000 启动

## 使用说明

### 1. 用户注册

- 访问 http://localhost:5000/register
- 输入用户名、密码和确认密码
- 点击注册按钮完成注册

### 2. 用户登录

- 访问 http://localhost:5000/login
- 输入用户名和密码
- 点击登录按钮进入聊天室

### 3. 发送消息

- 在输入框中输入消息内容
- 点击发送按钮或按Enter键发送消息

### 4. 播放视频

- 使用 `@电影` 指令加上视频链接
- 例如：`@电影 https://example.com/video.mp4`
- 系统将自动解析并在聊天中嵌入视频播放器

### 5. AI对话

- 使用 `@川小农` 指令加上对话内容
- 例如：`@川小农 你好，今天天气怎么样？`
- 系统将返回AI回复

### 6. 使用表情

- 点击输入框左侧的😊按钮打开表情选择器
- 点击表情即可插入到消息中

### 7. 退出聊天室

- 点击页面右上角的退出按钮
- 或直接关闭浏览器窗口

### 8. 管理员功能

- 登录管理员账户（用户名：admin，默认密码：admin123）
- 点击用户列表按钮查看所有注册用户
- 可查看用户详情、修改用户状态和删除用户

## 项目结构

```
DaipChatRoom/
├── app.py                 # 主应用程序
├── config.json            # 配置文件
├── chat.db                # SQLite数据库文件
├── templates/
│   ├── login.html        # 登录页面模板
│   ├── register.html     # 注册页面模板
│   ├── chat.html         # 聊天页面模板
│   ├── users.html        # 用户列表页面模板
│   └── user_details.html # 用户详情页面模板
├── static/
│   ├── css/
│   │   └── style.css    # 样式文件
│   ├── js/
│   │   └── chat.js       # 前端脚本文件
│   └── img/              # 图片资源目录
├── venv/                 # Python虚拟环境（忽略）
└── .gitignore            # Git忽略文件
```

## 配置文件说明

`config.json` 用于配置可用的服务器列表：

```json
{
  "servers": [
    "主服务器",
    "备用服务器1",
    "备用服务器2"
  ]
}
```

## 开发与扩展

### 添加新功能

1. **后端**：在 `app.py` 中添加新的路由或Socket.IO事件处理函数
2. **前端**：在 `static/js/chat.js` 中添加对应的客户端逻辑
3. **样式**：在 `static/css/style.css` 中添加新的样式
4. **模板**：根据需要修改 `templates/` 目录下的HTML模板

### 视频播放解析

当前使用的视频解析服务：
```python
parsed_url = f'http://jx.playerjy.com/?url={encoded_url}'
```

可以根据需要修改为其他视频解析服务。

### 数据库管理

系统使用SQLite数据库存储用户信息，表结构如下：

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nickname TEXT,
    status TEXT DEFAULT 'offline',
    is_admin INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 注意事项

1. 确保已安装Python 3.6或更高版本
2. 视频播放功能依赖外部解析服务，可能会受到网络限制
3. AI对话功能需要确保相关服务可用
4. 首次运行时会自动创建数据库文件和表结构
5. 管理员账户默认用户名：admin，密码：admin123
6. 请勿在生产环境中使用默认的SECRET_KEY

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 联系方式

如有问题或建议，请通过GitHub Issues联系我。