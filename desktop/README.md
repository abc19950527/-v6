# 药品进销存管理系统v6 - 桌面端

## 项目简介
基于 Electron + Vue3 + Element Plus + SQLite 开发的药品进销存管理系统桌面应用。

## 功能模块
- 基础信息管理（药品档案、供应商、员工权限）
- 采购入库管理
- 销售出库管理
- 库存管理中心
- 财务统计报表
- 数据安全（备份恢复）
- 会员管理
- 58mm/80mm小票打印
- Excel导出功能

## 技术栈
- Electron 29
- Vue 3.4
- Element Plus 2.6
- Vite 5
- better-sqlite3
- node-thermal-printer
- xlsx

## 开发与构建

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
# 或分开运行
npm run electron:dev
```

### 构建应用
```bash
npm run build
```

### 生产环境运行
```bash
npm run electron:build
```

## 默认账号
- 用户名: admin
- 密码: 123456

## 目录结构
```
desktop/
├── electron/          # Electron主进程
│   ├── main.js         # 主进程入口
│   └── preload.js      # 预加载脚本
├── src/
│   ├── api/           # API接口
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   ├── router/        # 路由配置
│   ├── stores/         # 状态管理
│   ├── utils/         # 工具函数
│   ├── views/         # 页面组件
│   ├── App.vue        # 根组件
│   └── main.js        # 应用入口
├── public/            # 公共资源
├── package.json       # 项目配置
└── vite.config.js     # Vite配置
```

## 注意事项
1. 首次运行需要安装 better-sqlite3 原生模块
2. 打印功能需要连接支持 ESC/POS 协议的小票打印机
3. 数据库文件存储在用户数据目录下
