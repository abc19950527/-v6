const { app, BrowserWindow, ipcMain, Menu, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const log = require('electron-log')

// 配置日志
log.transports.file.level = 'info'
log.transports.file.resolvePathFn = () => path.join(app.getPath('userData'), 'logs', 'main.log')

let mainWindow = null
let db = null
let SQL = null

// 初始化sql.js
async function initSqlJs() {
  const initSqlJs = require('sql.js')
  SQL = await initSqlJs()
}

// 数据库路径
function getDbPath() {
  return path.join(app.getPath('userData'), 'pharmacy.db')
}

// 加载数据库
async function loadDatabase() {
  try {
    const dbPath = getDbPath()
    log.info('数据库路径:', dbPath)
    
    if (!SQL) await initSqlJs()
    
    let fileBuffer = null
    if (fs.existsSync(dbPath)) {
      fileBuffer = fs.readFileSync(dbPath)
    }
    
    db = new SQL.Database(fileBuffer)
    createTables()
    saveDatabase()
    log.info('数据库初始化成功')
    return true
  } catch (error) {
    log.error('数据库初始化失败:', error)
    return false
  }
}

// 保存数据库到文件
function saveDatabase() {
  try {
    const data = db.export()
    const buffer = Buffer.from(data)
    fs.writeFileSync(getDbPath(), buffer)
  } catch (error) {
    log.error('保存数据库失败:', error)
  }
}

// 创建数据库表
function createTables() {
  // 药品档案表
  db.run(`
    CREATE TABLE IF NOT EXISTS drugs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      drug_code TEXT UNIQUE NOT NULL,
      drug_name TEXT NOT NULL,
      spec TEXT,
      unit TEXT DEFAULT '盒',
      category TEXT,
      manufacturer TEXT,
      approval_number TEXT,
      price REAL DEFAULT 0,
      cost_price REAL DEFAULT 0,
      min_stock INTEGER DEFAULT 0,
      prescription_type TEXT DEFAULT 'OTC',
      status TEXT DEFAULT '1',
      create_time TEXT DEFAULT CURRENT_TIMESTAMP,
      update_time TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // 批次表
  db.run(`
    CREATE TABLE IF NOT EXISTS drug_batches (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      drug_id INTEGER NOT NULL,
      batch_number TEXT,
      production_date TEXT,
      expiry_date TEXT,
      quantity INTEGER DEFAULT 0,
      cost_price REAL DEFAULT 0,
      supplier_id INTEGER,
      create_time TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (drug_id) REFERENCES drugs(id)
    )
  `)

  // 供应商表
  db.run(`
    CREATE TABLE IF NOT EXISTS suppliers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      supplier_code TEXT UNIQUE NOT NULL,
      supplier_name TEXT NOT NULL,
      contact TEXT,
      phone TEXT,
      address TEXT,
      status TEXT DEFAULT '1',
      create_time TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // 员工表
  db.run(`
    CREATE TABLE IF NOT EXISTS staff (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      staff_code TEXT UNIQUE NOT NULL,
      staff_name TEXT NOT NULL,
      phone TEXT,
      id_card TEXT,
      role TEXT DEFAULT 'staff',
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      status TEXT DEFAULT '1',
      create_time TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // 会员表
  db.run(`
    CREATE TABLE IF NOT EXISTS members (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      member_code TEXT UNIQUE NOT NULL,
      member_name TEXT NOT NULL,
      phone TEXT,
      id_card TEXT,
      points INTEGER DEFAULT 0,
      balance REAL DEFAULT 0,
      grade TEXT DEFAULT '普通会员',
      birthday TEXT,
      status TEXT DEFAULT '1',
      create_time TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // 采购入库单表
  db.run(`
    CREATE TABLE IF NOT EXISTS purchase_orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_no TEXT UNIQUE NOT NULL,
      supplier_id INTEGER,
      total_amount REAL DEFAULT 0,
      payment_status TEXT DEFAULT 'unpaid',
      operator_id INTEGER,
      remark TEXT,
      status TEXT DEFAULT 'pending',
      create_time TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
  `)

  // 采购明细表
  db.run(`
    CREATE TABLE IF NOT EXISTS purchase_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      drug_id INTEGER NOT NULL,
      batch_id INTEGER,
      quantity INTEGER DEFAULT 0,
      price REAL DEFAULT 0,
      amount REAL DEFAULT 0,
      create_time TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (order_id) REFERENCES purchase_orders(id),
      FOREIGN KEY (drug_id) REFERENCES drugs(id)
    )
  `)

  // 销售单表
  db.run(`
    CREATE TABLE IF NOT EXISTS sales_orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_no TEXT UNIQUE NOT NULL,
      member_id INTEGER,
      total_amount REAL DEFAULT 0,
      discount_amount REAL DEFAULT 0,
      actual_amount REAL DEFAULT 0,
      payment_method TEXT DEFAULT 'cash',
      operator_id INTEGER,
      remark TEXT,
      status TEXT DEFAULT 'completed',
      create_time TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (member_id) REFERENCES members(id)
    )
  `)

  // 销售明细表
  db.run(`
    CREATE TABLE IF NOT EXISTS sales_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      drug_id INTEGER NOT NULL,
      batch_id INTEGER,
      quantity INTEGER DEFAULT 0,
      price REAL DEFAULT 0,
      amount REAL DEFAULT 0,
      create_time TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (order_id) REFERENCES sales_orders(id),
      FOREIGN KEY (drug_id) REFERENCES drugs(id)
    )
  `)

  // 操作日志表
  db.run(`
    CREATE TABLE IF NOT EXISTS operation_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      operation TEXT,
      detail TEXT,
      ip_address TEXT,
      create_time TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `)

  // 插入默认管理员账户
  const result = db.exec("SELECT COUNT(*) as count FROM staff WHERE username = 'admin'")
  if (result.length === 0 || result[0].values[0][0] === 0) {
    db.run(`INSERT INTO staff (staff_code, staff_name, role, username, password) VALUES ('A001', '系统管理员', 'admin', 'admin', '123456')`)
  }
}

// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    title: '药品进销存管理系统v6',
    icon: path.join(__dirname, '../public/icon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  // 创建菜单
  const menuTemplate = [
    {
      label: '文件',
      submenu: [
        { label: '备份数据', click: () => mainWindow.webContents.send('menu-backup') },
        { label: '恢复数据', click: () => mainWindow.webContents.send('menu-restore') },
        { type: 'separator' },
        { label: '退出', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: '帮助',
      submenu: [
        { label: '关于', click: () => showAbout() }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(menuTemplate)
  Menu.setApplicationMenu(menu)

  // 加载页面
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 关于对话框
function showAbout() {
  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: '关于',
    message: '药品进销存管理系统v6',
    detail: '版本: 6.0.0\n一款专业的药品进销存管理系统\n\n功能包括:\n- 药品档案管理\n- 采购入库管理\n- 销售出库管理\n- 库存管理\n- 财务统计报表\n- 会员管理\n- 数据备份恢复'
  })
}

// IPC处理器 - 数据库操作
function setupIpcHandlers() {
  // 执行SQL查询
  ipcMain.handle('db:query', async (event, sql, params = []) => {
    try {
      if (sql.trim().toUpperCase().startsWith('SELECT')) {
        const stmt = db.prepare(sql)
        if (params.length > 0) {
          stmt.bind(params)
        }
        const results = []
        while (stmt.step()) {
          results.push(stmt.getAsObject())
        }
        stmt.free()
        return { success: true, data: results }
      } else {
        db.run(sql, params)
        saveDatabase()
        return { success: true, data: { changes: db.getRowsModified() } }
      }
    } catch (error) {
      log.error('数据库查询错误:', error)
      return { success: false, error: error.message }
    }
  })

  // 获取单条记录
  ipcMain.handle('db:get', async (event, sql, params = []) => {
    try {
      const stmt = db.prepare(sql)
      if (params.length > 0) {
        stmt.bind(params)
      }
      let data = null
      if (stmt.step()) {
        data = stmt.getAsObject()
      }
      stmt.free()
      return { success: true, data }
    } catch (error) {
      log.error('数据库查询错误:', error)
      return { success: false, error: error.message }
    }
  })

  // 执行插入并返回ID
  ipcMain.handle('db:insert', async (event, sql, params = []) => {
    try {
      db.run(sql, params)
      const lastId = db.exec('SELECT last_insert_rowid() as id')[0].values[0][0]
      saveDatabase()
      return { success: true, data: { id: lastId, changes: db.getRowsModified() } }
    } catch (error) {
      log.error('数据库插入错误:', error)
      return { success: false, error: error.message }
    }
  })

  // 备份数据库
  ipcMain.handle('db:backup', async () => {
    try {
      const { filePath } = await dialog.showSaveDialog(mainWindow, {
        title: '备份数据库',
        defaultPath: `pharmacy_backup_${new Date().toISOString().slice(0, 10)}.db`,
        filters: [{ name: '数据库文件', extensions: ['db'] }]
      })
      
      if (filePath) {
        const data = db.export()
        const buffer = Buffer.from(data)
        fs.writeFileSync(filePath, buffer)
        return { success: true, path: filePath }
      }
      return { success: false, error: '取消备份' }
    } catch (error) {
      log.error('备份失败:', error)
      return { success: false, error: error.message }
    }
  })

  // 恢复数据库
  ipcMain.handle('db:restore', async () => {
    try {
      const { filePaths } = await dialog.showOpenDialog(mainWindow, {
        title: '恢复数据库',
        filters: [{ name: '数据库文件', extensions: ['db'] }],
        properties: ['openFile']
      })
      
      if (filePaths && filePaths.length > 0) {
        const fileBuffer = fs.readFileSync(filePaths[0])
        db = new SQL.Database(fileBuffer)
        saveDatabase()
        return { success: true }
      }
      return { success: false, error: '取消恢复' }
    } catch (error) {
      log.error('恢复失败:', error)
      return { success: false, error: error.message }
    }
  })

  // 打印小票（模拟）
  ipcMain.handle('printer:print', async (event, ticketData) => {
    try {
      // 在实际环境中，这里会调用打印机
      // 目前模拟打印成功
      log.info('打印小票:', ticketData.content)
      return { success: true }
    } catch (error) {
      log.error('打印失败:', error)
      return { success: false, error: error.message }
    }
  })

  // 导出Excel
  ipcMain.handle('excel:export', async (event, data) => {
    try {
      const XLSX = require('xlsx')
      const { filePath } = await dialog.showSaveDialog(mainWindow, {
        title: '导出Excel',
        defaultPath: `${data.filename || 'export'}_${new Date().toISOString().slice(0, 10)}.xlsx`,
        filters: [{ name: 'Excel文件', extensions: ['xlsx', 'xls'] }]
      })
      
      if (filePath) {
        const ws = XLSX.utils.json_to_sheet(data.data)
        const wb = XLSX.utils.book_new()
        XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
        XLSX.writeFile(wb, filePath)
        return { success: true, path: filePath }
      }
      return { success: false, error: '取消导出' }
    } catch (error) {
      log.error('导出失败:', error)
      return { success: false, error: error.message }
    }
  })
}

// 应用启动
app.whenReady().then(async () => {
  log.info('应用启动')
  await initSqlJs()
  await loadDatabase()
  setupIpcHandlers()
  createWindow()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (db) {
      saveDatabase()
      db.close()
    }
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// 全局异常处理
process.on('uncaughtException', (error) => {
  log.error('未捕获异常:', error)
})

process.on('unhandledRejection', (reason) => {
  log.error('未处理拒绝:', reason)
})
