# 药品进销存管理系统 v6

基于 Node.js 全栈开发的药品进销存管理系统，支持 Windows 电脑端和安卓端，数据本地存储，离线可用。

## 技术架构

### 电脑端
- **框架**: Electron + Vue3 + Element Plus
- **数据库**: sql.js (SQLite in-memory)
- **打包**: electron-builder

### 安卓端
- **框架**: Kivy + SQLite
- **打包**: Buildozer

## 项目结构

```
d:/药品进销存管理系统v6/
├── desktop/                 # 电脑端 (Electron)
│   ├── electron/           # Electron主进程
│   ├── src/                # Vue源码
│   │   ├── api/            # API接口
│   │   ├── components/     # 组件
│   │   ├── router/         # 路由
│   │   ├── stores/         # 状态管理
│   │   ├── utils/          # 工具函数
│   │   └── views/           # 页面
│   ├── package.json
│   └── release/            # 打包输出
│
├── android/                 # 安卓端 (Kivy)
│   ├── main.py             # 主程序
│   ├── buildozer.spec      # 打包配置
│   └── bin/                # APK输出
│
├── .github/workflows/       # GitHub Actions
│   └── build.yml           # 自动构建配置
│
└── docs/                   # 文档
```

## 核心功能

### 模块1：基础信息管理
- [x] 药品档案管理（增删改查、分类管理）
- [x] 供应商管理（CRUD）
- [x] 员工权限管理（管理员/收银员/库管员）

### 模块2：采购入库管理
- [x] 手动录入入库单
- [x] 批量入库
- [x] 入库单据查询/修改/删除
- [x] 库存自动累加
- [x] 入库流水台账

### 模块3：销售出库管理
- [x] 快速开单（扫码/手动输入）
- [x] 自动计算金额
- [x] 库存扣减
- [x] 小票打印（58mm/80mm）
- [x] 销售单据管理

### 模块4：库存管理中心
- [x] 实时库存查询
- [x] 库存盘点
- [x] 效期预警（180天提醒）
- [x] 库存上下限预警

### 模块5：财务统计报表
- [x] 销售统计（日/月）
- [x] 销量排行
- [x] 毛利核算
- [x] 库存价值统计
- [x] Excel导出

### 模块6：数据安全
- [x] 手动/定时备份
- [x] 数据恢复
- [x] 操作日志

### 模块7：增值功能
- [x] 会员管理（积分/充值/折扣）
- [x] 拆零销售
- [x] 近效期促销
- [x] 流水日记账

## 快速开始

### 电脑端

```bash
# 进入目录
cd desktop

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建Windows安装包
npm run build
```

### 安卓端

#### 方式一：Windows本地打包（需要WSL）
```bash
# 在WSL中执行
cd android
pip install buildozer
buildozer android debug
```

#### 方式二：GitHub Actions自动打包
1. 将代码推送到GitHub仓库
2. 在Actions页面查看自动构建结果
3. 下载生成的APK

#### 方式三：本地调试
```bash
cd android
pip install kivy
python main.py
```

## 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 123456 |
| 收银员 | cashier | 123456 |
| 库管员 | warehouse | 123456 |

## 界面预览

### 电脑端
- 主色调：医疗蓝(#1890ff) + 简约白
- 布局：左侧导航 + 中间操作区
- 大按钮大字设计

### 安卓端
- 竖向极简布局
- 一键直达常用功能
- 触摸友好的大按钮

## 数据存储

- 所有数据存储在本地SQLite数据库
- 电脑端数据文件：`%APPDATA%/pharmacy-management-desktop/pharmacy.db`
- 安卓端数据文件：`/data/data/com.pharmacy.drugpos/files/drugpos.db`

## 备份与恢复

### 电脑端
1. 点击菜单「文件」→「备份数据」
2. 选择保存位置
3. 恢复时选择「文件」→「恢复数据」

### 安卓端
1. 进入「数据同步」界面
2. 导出数据备份包
3. 恢复时导入备份包

## 许可证

本软件为开源项目，可免费使用于个人和商业用途。

## 联系方式

如有问题或建议，请提交Issue。
