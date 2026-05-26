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
- Vue 3 (Vite)
- Vue Router 5
- Pinia 状态管理
- Axios HTTP 客户端

### 后端
- Python 3.11
- Flask Web 框架
- SQLAlchemy ORM
- PyMySQL 数据库驱动
- Flask-CORS 跨域支持

### 数据库
- MySQL 8.0

### 容器化
- Docker
- Docker Compose

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
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── views/           # 页面组件
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── HomeView.vue
│   │   │   ├── MyVideosView.vue        # 我的视频页面（新增）
│   │   │   ├── DancerListView.vue
│   │   │   ├── DancerDetailView.vue
│   │   │   ├── UploadVideoView.vue
│   │   │   ├── AnalysisResultView.vue
│   │   │   └── ProgressTrackingView.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── backend/                  # Python Flask 后端
│   ├── app.py               # Flask 主应用
│   ├── routes/              # 路由模块（按功能拆分）
│   │   ├── __init__.py
│   │   ├── users.py         # 用户认证和管理 API
│   │   ├── videos.py        # 视频管理 API
│   │   ├── analysis.py      # AI 分析 API
│   │   ├── progress.py      # 进步追踪 API
│   │   └── files.py         # 文件服务 API
│   ├── models/              # 数据模型
│   │   └── __init__.py      # 所有数据库模型
│   ├── utils/               # 工具函数
│   │   ├── __init__.py
│   │   ├── auth.py          # JWT 认证工具
│   │   └── file_utils.py    # 文件上传辅助功能
│   ├── requirements.txt     # Python 依赖
│   ├── Dockerfile           # Docker 配置
│   └── venv/                # Python 虚拟环境
│
├── docker-compose.yml        # Docker Compose 配置
├── .env.example              # 环境变量示例
├── .gitignore
├── LICENSE
└── README.md
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

- **users** - 用户表（数据隔离基础）
- **dancers** - 舞者表（关联 user_id）
- **videos** - 视频表（关联 user_id 和 dancer_id）
- **analysis** - 分析结果表（关联 video_id）
- **progress_records** - 进步记录表（关联 dancer_id）

所有业务表都包含 `user_id` 外键，确保数据完全隔离。

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MYSQL_ROOT_PASSWORD | MySQL root 密码 | rootpassword |
| MYSQL_DATABASE | 数据库名称 | dance_analysis |
| MYSQL_USER | 数据库用户 | dance_user |
| MYSQL_PASSWORD | 数据库密码 | dance_password |
| DATABASE_URL | 数据库连接 URL | 自动生成 |
| FLASK_SECRET_KEY | Flask 密钥 | 需设置 |

## 开发指南

### 添加新功能

1. 后端：在对应的路由模块中添加新的 API 端点
2. 前端：在 `frontend/src/views/` 中创建新页面组件
3. API：在 `frontend/src/api/` 中添加新的 API 调用函数
4. 路由：在 `frontend/src/router/` 中配置新路由

### 数据库迁移

目前使用 SQLAlchemy 自动创建表结构。生产环境建议使用 Flask-Migrate 进行数据库版本管理。

## 常见问题

### 数据库连接失败
- 检查 MySQL 服务是否正常运行
- 验证环境变量配置是否正确
- 确保网络连接正常

### 前端无法连接后端
- 检查后端服务是否启动
- 确认 CORS 配置是否正确
- 验证 API 基础 URL 配置

### Docker 构建失败
- 清理 Docker 缓存：`docker system prune`
- 检查 Docker 版本是否兼容
- 确保网络畅通可以拉取镜像

### 视频列表加载慢
- 现在视频列表仅加载封面图和基本信息，不加载视频内容
- 如需获取完整视频信息，请调用 `/api/videos/<id>` 接口
- 使用 `/api/videos/summary` 接口可获得更优的性能

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

- [ ] 集成真实的大模型 API 进行动作分析
- [ ] 完善视频文件上传和存储功能
- [ ] 添加数据可视化图表（ECharts/D3.js）
- [ ] 实现 JWT 令牌认证
- [ ] 添加批量视频处理功能
- [ ] 支持多种舞蹈风格分析
- [ ] 移动端适配
- [x] 视频列表仅加载封面（已完成）
- [x] 视频预览弹窗（已完成）
- [x] 后端代码模块化拆分（已完成）