# 二手设备销售管理系统 - 后端

基于 FastAPI + SQLAlchemy + PostgreSQL 的二手设备销售管理系统后端服务。

## 技术栈

- **Python** 3.11+
- **FastAPI** - Web 框架
- **SQLAlchemy** 2.0+ (async) - ORM
- **PostgreSQL** - 数据库
- **Alembic** - 数据库迁移
- **asyncpg** - 异步 PostgreSQL 驱动
- **python-jose** + **bcrypt** - JWT 认证与密码加密

## 前置条件

- Python 3.11+
- PostgreSQL 14+（需运行在 localhost:5432）

## 快速启动

### 1. 创建数据库

```bash
psql -U postgres -c "CREATE DATABASE secondhand_device;"
```

### 2. 安装依赖

```bash
cd backend
pip install -e ".[dev]"
```

> 异步驱动 asyncpg 需单独安装：`pip install asyncpg`

### 3. 配置环境变量

复制示例配置并修改：

```bash
cp .env.example .env
```

`.env` 文件说明：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL 连接串 | `postgresql://postgres:YOUR_PASSWORD@localhost:5432/secondhand_device` |
| SECRET_KEY | JWT 签名密钥 | 生产环境务必修改 |
| ACCESS_TOKEN_EXPIRE | Access Token 有效期（秒） | 3600 |
| REFRESH_TOKEN_EXPIRE | Refresh Token 有效期（秒） | 604800 |
| UPLOAD_DIR | 上传文件存储目录 | uploads |
| MAX_UPLOAD_SIZE | 上传文件大小限制（字节） | 5242880 (5MB) |
| CORS_ORIGINS | 允许的跨域来源 | `["http://localhost:5173"]` |

### 4. 执行数据库迁移

```bash
alembic upgrade head
```

### 5. 初始化种子数据（可选）

```bash
python -m app.seed
```

将创建管理员账号（admin / Admin123456）和 6 个预置分类。

### 6. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

开发模式（自动重载）：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档（Swagger）：http://localhost:8000/docs
- API 文档（ReDoc）：http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── main.py              # 应用入口、CORS、异常处理、路由挂载
│   ├── seed.py              # 种子数据脚本
│   ├── api/v1/              # API 路由层
│   │   ├── auth.py          # 注册/登录/刷新/获取当前用户
│   │   ├── devices.py       # 设备 CRUD + 搜索 + 图片管理
│   │   ├── orders.py        # 订单创建/确认/拒绝/交付/取消
│   │   ├── reviews.py       # 创建评价
│   │   ├── categories.py    # 分类 CRUD
│   │   ├── users.py         # 个人中心 + 评价统计
│   │   └── upload.py        # 通用文件上传
│   ├── core/                # 核心组件
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── security.py      # JWT + bcrypt
│   │   ├── dependencies.py  # 依赖注入（get_current_user, require_admin）
│   │   └── exceptions.py    # 自定义异常
│   ├── models/              # SQLAlchemy 数据模型
│   ├── schemas/             # Pydantic 请求/响应模型
│   ├── services/            # 业务逻辑层
│   └── utils/               # 工具函数
├── alembic/                 # 数据库迁移
├── tests/                   # 测试
│   └── integration/         # 集成测试
├── uploads/                 # 上传文件目录
├── pyproject.toml           # 项目配置
└── .env                     # 环境变量
```

## 运行测试

```bash
pytest tests/ -v
```

## API 概览

| 模块 | 接口 | 方法 | 路径 |
|------|------|------|------|
| 认证 | 注册 | POST | /api/v1/auth/register |
| 认证 | 登录 | POST | /api/v1/auth/login |
| 认证 | 刷新Token | POST | /api/v1/auth/refresh |
| 认证 | 当前用户 | GET | /api/v1/auth/me |
| 设备 | 设备列表 | GET | /api/v1/devices |
| 设备 | 发布设备 | POST | /api/v1/devices |
| 设备 | 设备详情 | GET | /api/v1/devices/{id} |
| 设备 | 更新设备 | PUT | /api/v1/devices/{id} |
| 设备 | 修改价格 | PATCH | /api/v1/devices/{id}/price |
| 设备 | 上下架 | PATCH | /api/v1/devices/{id}/status |
| 设备 | 删除设备 | DELETE | /api/v1/devices/{id} |
| 设备 | 设备评价 | GET | /api/v1/devices/{id}/reviews |
| 订单 | 创建订单 | POST | /api/v1/orders |
| 订单 | 订单列表 | GET | /api/v1/orders |
| 订单 | 订单详情 | GET | /api/v1/orders/{id} |
| 订单 | 确认/拒绝/交付/取消 | PATCH | /api/v1/orders/{id}/* |
| 评价 | 创建评价 | POST | /api/v1/reviews |
| 分类 | 分类列表 | GET | /api/v1/categories |
| 分类 | 分类CRUD | POST/PUT/DELETE | /api/v1/categories/* |
| 用户 | 更新信息 | PUT | /api/v1/users/me |
| 用户 | 修改密码 | PUT | /api/v1/users/me/password |
| 用户 | 我的发布 | GET | /api/v1/users/me/devices |
| 用户 | 评价统计 | GET | /api/v1/users/{id}/review-stats |
| 上传 | 文件上传 | POST | /api/v1/upload |