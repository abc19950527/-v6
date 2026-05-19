const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 数据库操作
  db: {
    query: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
    get: (sql, params) => ipcRenderer.invoke('db:get', sql, params),
    insert: (sql, params) => ipcRenderer.invoke('db:insert', sql, params),
    backup: () => ipcRenderer.invoke('db:backup'),
    restore: () => ipcRenderer.invoke('db:restore')
  },
  
  // 打印功能
  printer: {
    print: (ticketData) => ipcRenderer.invoke('printer:print', ticketData)
  },
  
  // Excel导出
  excel: {
    export: (data) => ipcRenderer.invoke('excel:export', data)
  },
  
  // 菜单事件
  onMenuBackup: (callback) => ipcRenderer.on('menu-backup', callback),
  onMenuRestore: (callback) => ipcRenderer.on('menu-restore', callback)
})
