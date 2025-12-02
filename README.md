# DaiP智能聊天室

一个基于Flask和Socket.IO的实时智能聊天室，支持多种智能功能和完整的用户管理系统。

## 功能特性

### 基础功能
- ✅ **实时聊天**：基于WebSocket的即时消息传输
- ✅ **用户管理**：完整的用户注册、登录和管理系统
- ✅ **管理员功能**：用户列表查看、状态管理和权限控制
- ✅ **表情支持**：内置表情选择器
- ✅ **响应式设计**：适配不同设备屏幕
- ✅ **历史消息**：自动记录并支持查看历史聊天记录

### 智能功能
- ✅ **AI对话**：集成AI对话功能（@川小农）
- ✅ **视频播放**：支持@电影指令播放网络视频
- ✅ **天气查询**：支持@查天气指令查询城市天气
- ✅ **音乐播放**：支持@听音乐指令搜索并播放音乐
- ✅ **新闻查询**：支持@查新闻指令获取最新热点新闻

## 技术栈

- **后端框架**：Flask (Python)
- **实时通信**：Socket.IO
- **前端技术**：HTML5, CSS3, JavaScript
- **模板引擎**：Jinja2
- **数据库**：SQLite
- **依赖管理**：Python虚拟环境
- **API集成**：天气API、音乐API、新闻API、AI API

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
pip install flask flask-socketio requests
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
- 选择服务器并点击登录按钮进入聊天室

### 3. 发送消息

- 在输入框中输入消息内容
- 点击发送按钮或按Enter键发送消息

### 4. AI对话

- 使用 `@川小农` 指令加上对话内容
- 例如：`@川小农 你好，今天天气怎么样？`
- 系统将返回AI回复

### 5. 播放视频

- 使用 `@电影` 指令加上视频链接
- 例如：`@电影 https://example.com/video.mp4`
- 系统将自动解析并在聊天中嵌入视频播放器

### 6. 天气查询

- 使用 `@查天气` 指令加上城市名称
- 例如：`@查天气 北京`
- 系统将返回该城市的天气信息

### 7. 音乐播放

- 使用 `@听音乐` 指令加上歌曲名称
- 例如：`@听音乐 小幸运`
- 系统将搜索并播放该歌曲

### 8. 新闻查询

- 使用 `@查新闻` 指令
- 例如：`@查新闻`
- 系统将返回最新的热点新闻列表

### 9. 使用表情

- 点击输入框左侧的😊按钮打开表情选择器
- 点击表情即可插入到消息中

### 10. 退出聊天室

- 点击页面右上角的退出按钮
- 或直接关闭浏览器窗口

### 11. 管理员功能

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

### API集成说明

系统集成了多个外部API来实现智能功能：

#### 天气API
- 调用地址：https://v2.xxapi.cn/api/weather
- 功能：根据城市名称查询天气信息
- 使用方式：`@查天气 城市名称`

#### 音乐API
- 调用地址：https://v2.xxapi.cn/api/kugousearch
- 功能：根据歌曲名称搜索并播放音乐
- 使用方式：`@听音乐 歌曲名称`

#### 新闻API
- 调用地址：https://v2.xxapi.cn/api/baiduhot
- 功能：获取最新热点新闻列表
- 使用方式：`@查新闻`

#### AI API
- 调用地址：自定义AI服务接口
- 功能：提供智能对话功能
- 使用方式：`@川小农 对话内容`

### 数据库管理

系统使用SQLite数据库存储用户信息和消息记录，表结构如下：

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    status TEXT DEFAULT 'offline',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_admin INTEGER DEFAULT 0
);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_type TEXT NOT NULL, -- normal, ai, movie, system, weather, music, news
    content TEXT NOT NULL,
    additional_data TEXT, -- 存储AI回复、电影链接、天气数据等额外信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 注意事项

1. 确保已安装Python 3.6或更高版本
2. 视频播放功能依赖外部解析服务，可能会受到网络限制
3. 所有智能功能均依赖外部API，需要确保网络连接正常
4. 首次运行时会自动创建数据库文件和表结构
5. 管理员账户默认用户名：admin，密码：admin123
6. 请勿在生产环境中使用默认的SECRET_KEY和API密钥
7. 部分API可能有调用次数限制，请合理使用

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 联系方式

如有问题或建议，请通过GitHub Issues联系我。