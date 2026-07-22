# 二手设备销售管理系统 - 前端

基于 Vue 3 + TypeScript + Element Plus 的二手设备销售管理系统前端应用。

## 技术栈

- **Vue 3** - 组合式 API + `<script setup>`
- **TypeScript** - 类型安全
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 客户端
- **Vite** - 构建工具

## 前置条件

- Node.js 18+
- 后端服务运行在 http://localhost:8000

## 快速启动

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用启动后访问：http://localhost:5173

> 开发模式下，`/api` 请求自动代理到后端 `http://localhost:8000`（通过 Vite proxy 配置）。

### 3. 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录。

### 4. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── api/                 # API 接口封装
│   │   ├── auth.ts          # 认证接口
│   │   ├── device.ts        # 设备接口
│   │   ├── order.ts         # 订单接口
│   │   ├── review.ts        # 评价接口
│   │   ├── category.ts      # 分类接口
│   │   └── user.ts          # 用户接口
│   ├── components/          # 通用组件
│   │   ├── DeviceCard.vue   # 设备卡片
│   │   ├── SearchBar.vue    # 搜索栏
│   │   ├── ImageUpload.vue  # 图片上传
│   │   └── StatusTag.vue    # 状态标签
│   ├── layouts/
│   │   └── MainLayout.vue   # 主布局（导航栏+内容区）
│   ├── router/
│   │   └── index.ts         # 路由配置+守卫
│   ├── stores/              # Pinia 状态管理
│   │   ├── auth.ts          # 认证状态
│   │   └── device.ts        # 设备列表状态
│   ├── utils/
│   │   ├── request.ts       # Axios 封装（Token 拦截+401 刷新）
│   │   └── format.ts        # 格式化工具
│   ├── views/               # 页面组件
│   │   ├── auth/            # 登录、注册
│   │   ├── device/          # 设备列表、详情、发布
│   │   ├── order/           # 订单列表、详情
│   │   ├── review/          # 评价弹窗
│   │   ├── profile/         # 个人中心
│   │   ├── my/              # 我的发布
│   │   └── admin/           # 分类管理
│   ├── App.vue
│   └── main.ts
├── vite.config.ts           # Vite 配置（含 API 代理）
├── tsconfig.json
└── package.json
```

## 页面路由

| 路由 | 页面 | 权限 |
|------|------|------|
| `/` | 首页/设备列表 | 无 |
| `/login` | 登录 | 未登录 |
| `/register` | 注册 | 未登录 |
| `/devices/:id` | 设备详情 | 无 |
| `/devices/publish` | 发布设备 | 登录 |
| `/orders` | 订单列表 | 登录 |
| `/orders/:id` | 订单详情 | 登录 |
| `/profile` | 个人中心 | 登录 |
| `/my/devices` | 我的发布 | 登录 |
| `/admin/categories` | 分类管理 | 管理员 |

## 设计规范

| Token | 值 | 用途 |
|-------|-----|------|
| accent | #0052FF | 主操作色 |
| accent-secondary | #4D7CFF | 渐变终点色 |
| background | #FAFAFA | 页面背景 |
| card | #FFFFFF | 卡片背景 |
| border | #E2E8F0 | 边框 |
| success | #22C55E | 成功/在售 |
| warning | #F59E0B | 警告/待确认 |
| danger | #EF4444 | 危险/已取消 |
