# 药品进销存管理系统 v6 技术规范

## 一、项目概述
基于Node.js全栈的药品进销存管理系统，支持Windows电脑端和安卓端，数据本地存储，离线可用。

## 二、技术架构

### 电脑端
- 框架: Electron + Vue3 + SQLite
- 后端: Express.js
- 数据库: SQLite3
- UI组件库: Element Plus

### 安卓端
- 框架: Kivy + SQLite
- 打包工具: Buildozer

## 三、数据库设计

### 表结构

#### 1. 药品档案表 (drugs)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| drug_code | TEXT | 药品编码 |
| name | TEXT | 药品名称 |
| generic_name | TEXT | 通用名 |
| specification | TEXT | 规格 |
| dosage_form | TEXT | 剂型 |
| unit | TEXT | 单位 |
| manufacturer | TEXT | 生产厂家 |
| approval_number | TEXT | 批准文号 |
| origin | TEXT | 产地 |
| purchase_price | REAL | 进货价 |
| retail_price | REAL | 零售价 |
| member_price | REAL | 会员价 |
| wholesale_price | REAL | 批发价 |
| category | TEXT | 分类 |
| is_prescription | INTEGER | 是否处方药 0-非处方 1-处方 |
| min_stock | INTEGER | 最低库存 |
| max_stock | INTEGER | 最高库存 |
| status | INTEGER | 状态 0-禁用 1-启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 2. 药品批次表 (drug_batches)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| drug_id | INTEGER | 药品ID |
| batch_number | TEXT | 批号 |
| production_date | DATE | 生产日期 |
| expiry_date | DATE | 有效期 |
| quantity | INTEGER | 库存数量 |
| purchase_price | REAL | 进货价 |
| supplier_id | INTEGER | 供应商ID |
| status | INTEGER | 状态 |
| created_at | DATETIME | 创建时间 |

#### 3. 供应商表 (suppliers)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| code | TEXT | 供应商编码 |
| name | TEXT | 供应商名称 |
| contact | TEXT | 联系人 |
| phone | TEXT | 电话 |
| address | TEXT | 地址 |
| status | INTEGER | 状态 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 4. 员工表 (staff)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| username | TEXT | 用户名 |
| password | TEXT | 密码(加密) |
| name | TEXT | 姓名 |
| role | TEXT | 角色 admin/cashier/warehouse |
| phone | TEXT | 电话 |
| status | INTEGER | 状态 |
| created_at | DATETIME | 创建时间 |

#### 5. 入库单表 (purchase_orders)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| order_no | TEXT | 单据编号 |
| supplier_id | INTEGER | 供应商ID |
| total_amount | REAL | 总金额 |
| operator_id | INTEGER | 操作员ID |
| status | INTEGER | 状态 |
| remark | TEXT | 备注 |
| created_at | DATETIME | 创建时间 |

#### 6. 入库明细表 (purchase_items)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| order_id | INTEGER | 入库单ID |
| drug_id | INTEGER | 药品ID |
| batch_number | TEXT | 批号 |
| quantity | INTEGER | 数量 |
| price | REAL | 单价 |
| amount | REAL | 金额 |
| expiry_date | DATE | 有效期 |
| created_at | DATETIME | 创建时间 |

#### 7. 销售单表 (sales_orders)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| order_no | TEXT | 单据编号 |
| member_id | INTEGER | 会员ID |
| total_amount | REAL | 应收金额 |
| discount_amount | REAL | 优惠金额 |
| actual_amount | REAL | 实收金额 |
| cash_received | REAL | 收款金额 |
| change_amount | REAL | 找零金额 |
| operator_id | INTEGER | 操作员ID |
| payment_method | TEXT | 支付方式 |
| status | INTEGER | 状态 |
| print_status | INTEGER | 打印状态 |
| created_at | DATETIME | 创建时间 |

#### 8. 销售明细表 (sales_items)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| order_id | INTEGER | 销售单ID |
| drug_id | INTEGER | 药品ID |
| batch_id | INTEGER | 批次ID |
| quantity | INTEGER | 数量(拆零数量) |
| pack_quantity | INTEGER | 整包数量 |
| unit_price | REAL | 单价 |
| amount | REAL | 金额 |
| created_at | DATETIME | 创建时间 |

#### 9. 会员表 (members)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| card_no | TEXT | 卡号 |
| name | TEXT | 姓名 |
| phone | TEXT | 电话 |
| points | INTEGER | 积分 |
| balance | REAL | 余额 |
| discount_rate | REAL | 折扣率 |
| status | INTEGER | 状态 |
| created_at | DATETIME | 创建时间 |

#### 10. 库存调整表 (stock_adjustments)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| drug_id | INTEGER | 药品ID |
| batch_id | INTEGER | 批次ID |
| before_quantity | INTEGER | 调整前数量 |
| after_quantity | INTEGER | 调整后数量 |
| reason | TEXT | 调整原因 |
| operator_id | INTEGER | 操作员ID |
| created_at | DATETIME | 创建时间 |

#### 11. 操作日志表 (operation_logs)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| operator_id | INTEGER | 操作员ID |
| action | TEXT | 操作类型 |
| table_name | TEXT | 操作表名 |
| record_id | INTEGER | 记录ID |
| detail | TEXT | 详细信息 |
| created_at | DATETIME | 创建时间 |

#### 12. 系统设置表 (settings)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| key | TEXT | 键名 |
| value | TEXT | 键值 |
| updated_at | DATETIME | 更新时间 |

## 四、核心功能模块

### 模块1：基础信息管理
1. 药品档案管理（增删改查、分类管理）
2. 供应商管理（CRUD）
3. 员工权限管理（角色：管理员/收银员/库管员）

### 模块2：采购入库管理
1. 手动录入入库单
2. 批量入库
3. 入库单据查询/修改/删除
4. 库存自动累加
5. 入库流水台账
6. 筛选查询（时间/供应商/药品）

### 模块3：销售出库管理
1. 快速开单（扫码/手动输入）
2. 自动计算金额
3. 库存扣减
4. 小票打印（58mm/80mm）
5. 销售单据管理
6. 当日销售汇总

### 模块4：库存管理中心
1. 实时库存查询
2. 库存盘点
3. 效期预警（180天提醒）
4. 库存上下限预警

### 模块5：财务统计报表
1. 销售统计（日/月）
2. 销量排行
3. 毛利核算
4. 库存价值统计
5. Excel导出

### 模块6：数据安全
1. 手动/定时备份
2. 数据恢复
3. 操作日志

### 模块7：增值功能
1. 会员管理
2. 拆零销售
3. 近效期促销
4. 流水日记账

## 五、界面设计

### 电脑端
- 主色调：#1890ff（医疗蓝）+ #ffffff（简约白）
- 布局：左侧导航 + 中间主操作区 + 右侧数据预览
- 大按钮、大字体设计

### 安卓端
- 竖向极简布局
- 一键直达常用功能
- 触摸友好的大按钮

## 六、项目结构

```
d:/药品进销存管理系统v6/
├── desktop/                 # 电脑端
│   ├── main.js             # Electron主进程
│   ├── preload.js          # 预加载脚本
│   ├── package.json
│   ├── src/
│   │   ├── main.js         # Vue入口
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── views/          # 页面
│   │   ├── components/      # 组件
│   │   ├── store/          # 状态管理
│   │   ├── api/            # API接口
│   │   ├── utils/          # 工具函数
│   │   └── styles/         # 样式
│   └── dist/               # 打包输出
│
├── android/                 # 安卓端
│   ├── main.py             # Kivy主程序
│   ├── buildozer.spec
│   └── screens/            # 界面
│
├── database/               # 数据库文件
│   └── backup/             # 备份目录
│
└── docs/                   # 文档
    └── manual.pdf          # 操作手册
```

## 七、部署方式

### 电脑端
- 打包为Windows exe免安装程序
- 使用electron-builder

### 安卓端
- 使用buildozer打包为APK
- 支持安卓5.0+
