# 舞蹈视频 AI 分析系统

一个基于大模型能力的街舞舞者进步追踪系统，通过 AI 分析舞蹈视频，实现单个人标识和全数据隔离的追踪分析。

## 项目简介

本项目利用先进的大模型技术，对街舞舞者的视频进行智能分析，追踪舞者的动作质量、进步情况和技能发展。系统支持多用户管理，确保每个用户的数据完全隔离，同时为每位舞者提供独立的身份标识和长期的进步追踪。

## 核心功能

- 🎯 **单个人标识**：为每位舞者分配唯一 ID，实现精准的个人数据追踪
- 🔒 **全数据隔离**：多用户系统，确保不同用户的数据完全隔离和安全
- 📹 **视频上传分析**：支持上传舞蹈视频，AI 自动分析动作质量
- 🖼️ **封面预览**：视频列表仅加载封面图，提升页面性能
- 🎬 **弹窗预览**：点击视频即可在弹窗中预览，无需打开新标签页
- 📊 **进步追踪**：可视化展示舞者的进步曲线和技能发展
- 🤖 **AI 智能分析**：集成大模型能力，提供专业的舞蹈动作评估
- 👥 **用户管理**：完整的注册、登录和用户认证系统

## 技术栈

### 前端
- **框架**: Vue 3 (Vite)
- **路由**: Vue Router 5
- **状态管理**: Pinia
- **HTTP 客户端**: Axios
- **构建工具**: Vite
- **Web 服务器**: Nginx (生产环境)

### 后端
- **语言**: Python 3.11
- **Web 框架**: Flask (应用工厂模式)
- **ORM**: SQLAlchemy 2.0
- **数据库迁移**: Flask-Migrate
- **认证**: PyJWT (JWT 令牌)
- **跨域支持**: Flask-CORS
- **AI 集成**: OpenAI SDK, Requests

### 数据库
- **MySQL 8.0** - 关系型数据库

### 容器化与部署
- **Docker** - 容器化
- **Docker Compose** - 多服务编排

### 核心依赖
**后端主要依赖:**
- Flask 3.1.3
- Flask-SQLAlchemy 3.1.1
- Flask-Migrate 4.1.0
- PyMySQL 1.2.0
- SQLAlchemy 2.0.50
- PyJWT 2.9.0
- openai >= 1.0.0
- requests 2.32.3

## 快速开始

### 前置要求

- Docker & Docker Compose
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### 方式一：Docker Compose 启动（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd analyze-dance
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库密码等配置
```

3. 启动所有服务
```bash
docker-compose up -d
```

4. 查看服务状态
```bash
docker-compose ps
```

5. 访问应用
- 前端：http://localhost
- 后端 API：http://localhost:5000
- 数据库：localhost:3306

6. 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

7. 停止服务
```bash
docker-compose down
```

### 方式二：本地开发环境

#### 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/dance_analysis"
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=dance_user
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=dance_analysis

# 运行应用
python app.py
```

后端服务将在 http://localhost:5000 启动

#### 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 项目结构

```
analyze-dance/
├── frontend/                 # Vue 3 前端项目
│   ├── src/
│   │   ├── api/             # API 接口封装
│   │   ├── assets/          # 静态资源（图片、样式等）
│   │   ├── components/      # 可复用组件
│   │   │   ├── ConfirmDialog.vue    # 确认对话框组件
│   │   │   ├── Toast.vue            # 消息提示组件
│   │   │   └── HelloWorld.vue       # 示例组件
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── views/           # 页面组件
│   │   │   ├── LoginView.vue          # 登录页面
│   │   │   ├── RegisterView.vue       # 注册页面
│   │   │   ├── HomeView.vue           # 首页
│   │   │   ├── MyVideosView.vue       # 我的视频页面
│   │   │   ├── DancerListView.vue     # 舞者列表页面
│   │   │   ├── UploadVideoView.vue    # 上传视频页面
│   │   │   ├── AnalysisResultView.vue # 分析结果页面
│   │   │   ├── AnalysisHistoryView.vue# 分析历史页面
│   │   │   ├── ProgressTrackingView.vue # 进步追踪页面
│   │   │   └── UserProfileView.vue    # 用户个人资料页面
│   │   ├── App.vue          # 根组件
│   │   ├── main.js          # 应用入口
│   │   └── style.css        # 全局样式
│   ├── public/              # 公共静态资源
│   ├── Dockerfile           # 前端 Docker 配置
│   ├── nginx.conf           # Nginx 配置文件
│   ├── vite.config.js       # Vite 构建配置
│   ├── package.json         # 前端依赖配置
│   └── README.md            # 前端说明文档
│
├── backend/                  # Python Flask 后端
│   ├── app.py               # Flask 主应用（应用工厂模式）
│   ├── routes/              # 路由模块（按功能拆分）
│   │   ├── __init__.py      # 蓝图注册
│   │   ├── users.py         # 用户认证和管理 API
│   │   ├── videos.py        # 视频管理 API
│   │   ├── analysis.py      # AI 分析 API
│   │   ├── progress.py      # 进步追踪 API
│   │   └── files.py         # 文件服务 API
│   ├── models/              # 数据模型
│   │   └── __init__.py      # 所有数据库模型定义
│   ├── utils/               # 工具函数
│   │   ├── __init__.py      # 工具导出
│   │   ├── auth.py          # JWT 认证工具
│   │   ├── file_utils.py    # 文件上传辅助功能
│   │   └── ai_service.py    # AI 服务封装（OpenAI API）
│   ├── migrations/          # 数据库迁移文件
│   ├── requirements.txt     # Python 依赖
│   ├── Dockerfile           # 后端 Docker 配置
│   └── venv/                # Python 虚拟环境（开发用）
│
├── docker-compose.yml        # Docker Compose 编排配置
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略规则
├── LICENSE                   # 开源许可证
└── README.md                 # 项目说明文档
```

## API 接口

### 认证相关
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出

### 舞者管理
- `GET /api/dancers` - 获取舞者列表
- `GET /api/dancers/<id>` - 获取舞者详情
- `POST /api/dancers` - 创建舞者
- `PUT /api/dancers/<id>` - 更新舞者信息
- `DELETE /api/dancers/<id>` - 删除舞者

### 视频管理
- `GET /api/videos` - 获取视频列表（仅返回基本信息和封面）
- `GET /api/videos/summary` - 获取视频摘要（性能更优，仅封面和基本信息）
- `POST /api/videos/upload` - 上传视频文件
- `POST /api/videos` - 上传视频（元数据方式）
- `GET /api/videos/<id>` - 获取视频详情（包含分析结果）
- `DELETE /api/videos/<id>` - 删除视频

### AI 分析
- `POST /api/analyze` - 执行 AI 分析
- `GET /api/analysis/<id>` - 获取分析结果

### 进步追踪
- `GET /api/progress/<dancer_id>` - 获取舞者进步记录
- `POST /api/progress` - 创建进步记录

## 数据库设计

### 主要数据表

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| **users** | 用户表（数据隔离基础） | id, username, email, password_hash, avatar_url, is_admin, created_at |
| **dancers** | 舞者表（关联 user_id） | id, user_id, name, description, avatar_url, created_at, updated_at |
| **videos** | 视频表（关联 user_id 和 dancer_id） | id, user_id, dancer_id, title, file_path, thumbnail_url, dance_style, video_type |
| **analyses** | AI 分析结果表（关联 video_id） | id, user_id, video_id, analysis_type, result_data, confidence_score, model_version |
| **progress_records** | 进步记录表（关联 dancer_id） | id, dancer_id, skill_category, score, recorded_at |

### 数据隔离机制

所有业务表都包含 `user_id` 外键，确保：
- 每个用户只能访问自己的数据
- 多租户场景下的数据安全
- 基于用户的权限控制

### 时区处理

所有时间字段使用 **CST (UTC+8)** 时区，统一使用 `get_cst_now()` 函数获取当前时间。

## 环境变量

### Docker Compose 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MYSQL_ROOT_PASSWORD | MySQL root 密码 | rootpassword |
| MYSQL_DATABASE | 数据库名称 | dance_analysis |
| MYSQL_USER | 数据库用户 | dance_user |
| MYSQL_PASSWORD | 数据库密码 | dance_password |
| DATABASE_URL | 数据库连接 URL | 自动生成 (backend 服务) |
| SECRET_KEY | Flask 密钥 | your-secret-key-here |
| FLASK_DEBUG | 是否开启调试模式 | false |
| FLASK_HOST | Flask 监听地址 | 0.0.0.0 |
| FLASK_PORT | Flask 端口 | 5000 |

### 文件上传配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| UPLOAD_FOLDER | 上传文件夹路径 | /app/uploads |
| VIDEO_SUBFOLDER | 视频子文件夹 | videos |
| ALLOWED_EXTENSIONS | 允许的视频格式 | mp4,avi,mov,mkv,webm |
| ALLOWED_IMAGE_EXTENSIONS | 允许的图片格式 | jpg,jpeg,png,gif,bmp,webp |
| MAX_CONTENT_LENGTH | 最大上传大小 (字节) | 524288000 (500MB) |
| MAX_AVATAR_SIZE | 最大头像大小 (字节) | 5242880 (5MB) |

### AI 分析配置

| 变量名 | 说明 | 说明 |
|--------|------|------|
| AI_API_BASE_URL | AI API 基础 URL | 根据使用的 AI 服务配置 |
| AI_API_KEY | AI API 密钥 | 需从服务商获取 |
| AI_MODEL_NAME | AI 模型名称 | 如：gpt-4-vision-preview |

### 配置方式

1. **Docker Compose**: 复制 `.env.example` 为 `.env` 并修改相应配置
2. **本地开发**: 设置环境变量或在代码中配置

## 开发指南

### 添加新功能

#### 后端 API 开发流程

1. **创建路由模块**：在 `backend/routes/` 下创建新的路由文件
2. **定义数据模型**：在 `backend/models/__init__.py` 中添加新模型类
3. **编写业务逻辑**：在 `backend/utils/` 下添加工具函数或服务类
4. **注册蓝图**：在 `backend/app.py` 中注册新的蓝图
5. **配置数据库迁移**：使用 Flask-Migrate 进行数据库变更管理

示例 - 添加新的 API 端点:
```python
# backend/routes/example.py
from flask import Blueprint, request, jsonify
from utils.auth import token_required
from models import db

example_bp = Blueprint('example', __name__)

@example_bp.route('/api/example', methods=['GET'])
@token_required
def get_example(current_user):
    return jsonify({'message': 'Hello from example API'})
```

#### 前端页面开发流程

1. **创建视图组件**：在 `frontend/src/views/` 下创建新的页面组件
2. **创建可复用组件**：在 `frontend/src/components/` 下创建通用组件
3. **配置路由**：在 `frontend/src/router/` 中添加路由配置
4. **状态管理**：在 `frontend/src/stores/` 中创建 Pinia store
5. **API 调用**：在 `frontend/src/api/` 中添加 API 接口函数

示例 - 创建新页面:
```vue
<!-- frontend/src/views/ExampleView.vue -->
<template>
  <div class="example-view">
    <h1>示例页面</h1>
  </div>
</template>

<script setup>
import { ref } from 'vue'
</script>
```

### 数据库迁移

项目使用 **Flask-Migrate** 进行数据库版本管理：

```bash
# 进入后端目录
cd backend

# 初始化迁移（仅首次）
flask db init

# 创建迁移脚本
flask db migrate -m "描述更改内容"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

### 代码规范

- **Python**: 遵循 PEP 8 编码规范
- **Vue**: 使用 Composition API (setup 语法糖)
- **命名**: 
  - Python 文件使用 snake_case
  - Vue 组件使用 PascalCase
  - API 端点使用 RESTful 风格

## 常见问题

### 数据库连接失败

- 检查 MySQL 服务是否正常运行：`docker-compose ps db`
- 验证环境变量配置是否正确（特别是密码和用户名）
- 确保网络连接正常，Docker 容器间可以通信
- 查看数据库日志：`docker-compose logs db`

### 前端无法连接后端

- 检查后端服务是否启动：`docker-compose ps backend`
- 确认 CORS 配置是否正确（已在 `backend/app.py` 中配置）
- 验证 API 基础 URL 配置（前端应指向正确的后端地址）
- 查看后端日志：`docker-compose logs backend`

### Docker 构建失败

- 清理 Docker 缓存：`docker system prune -a`
- 检查 Docker 版本是否兼容（建议 20.10+）
- 确保网络畅通可以拉取镜像
- 删除并重建容器：`docker-compose down && docker-compose up --build`

### 视频列表加载慢

- ✅ 已优化：视频列表仅加载封面图和基本信息
- 使用 `/api/videos/summary` 接口可获得更优的性能
- 如需获取完整视频信息，调用 `/api/videos/<id>` 接口
- 确保 CDN 或静态文件服务配置正确

### 上传失败

- 检查文件大小是否超过限制（默认 500MB）
- 确认文件格式是否在允许列表中（mp4, avi, mov, mkv, webm）
- 检查磁盘空间是否充足
- 查看上传目录权限：`ls -la backend/uploads/`

### AI 分析功能异常

- 确认 AI_API_KEY 已正确配置
- 检查网络连接是否可以访问 AI 服务提供商
- 查看 AI 服务配额是否充足
- 检查 `backend/utils/ai_service.py` 中的错误日志

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 联系方式

如有问题或建议，请：
- 提交 Issue
- 联系项目维护者

## 后续计划

### 已完成 ✅

- [x] 视频列表仅加载封面（性能优化）
- [x] 视频预览弹窗功能
- [x] 后端代码模块化拆分（Blueprints）
- [x] JWT 令牌认证系统
- [x] 用户头像上传功能
- [x] Flask-Migrate 数据库迁移支持
- [x] AI 服务封装（OpenAI SDK 集成）
- [x] 完整的用户管理系统（注册、登录、资料管理）

### 进行中 🚧

- [ ] 集成真实的大模型 API 进行动作分析
- [ ] 完善视频文件上传和存储功能
- [ ] 添加数据可视化图表（ECharts/D3.js）

### 计划中 📋

- [ ] 批量视频处理功能
- [ ] 支持多种舞蹈风格分析（breaking, popping, locking, choreography, heels 等）
- [ ] 移动端适配（响应式设计）
- [ ] WebSocket 实时分析进度推送
- [ ] 视频对比功能（同一舞者不同时期的视频对比）
- [ ] 社交分享功能
- [ ] 多语言支持（i18n）
- [ ] 性能监控和日志系统
- [ ] 单元测试和集成测试覆盖