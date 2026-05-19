# -*- coding: utf-8 -*-
"""
数据同步模块
支持与电脑端SQLite数据库的同步
"""

import os
import sqlite3
import json
import datetime
import hashlib
import time


class DataSync:
    """数据同步类"""
    
    def __init__(self, db_manager):
        """初始化同步器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
        self.last_sync_time = None
        self.sync_status = 'idle'  # idle, syncing, success, failed
    
    def get_sync_config(self):
        """获取同步配置"""
        config = self.db.fetch_one("SELECT * FROM settings WHERE key = 'sync_config'")
        if config:
            return json.loads(config['value'])
        return {
            'server_url': '',
            'sync_mode': 'manual',  # manual, auto
            'wifi_only': True,
            'last_sync': None,
        }
    
    def save_sync_config(self, config):
        """保存同步配置"""
        value = json.dumps(config)
        self.db.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES ('sync_config', ?, ?)
        ''', (value, datetime.datetime.now().isoformat()))
    
    def create_sync_package(self):
        """创建同步数据包
        
        生成包含所有本地数据的JSON包
        用于导出到电脑端或从电脑端导入
        """
        package = {
            'version': '1.0',
            'created_at': datetime.datetime.now().isoformat(),
            'device_id': self.get_device_id(),
            'tables': {}
        }
        
        # 同步所有业务表
        sync_tables = [
            'drugs', 'drug_batches', 'suppliers', 'staff',
            'sales_orders', 'sales_items', 'members',
            'settings'
        ]
        
        for table_name in sync_tables:
            rows = self.db.fetch_all(f'SELECT * FROM {table_name}')
            package['tables'][table_name] = [dict(row) for row in rows]
        
        return package
    
    def export_sync_package(self, file_path):
        """导出同步包到文件
        
        Args:
            file_path: 导出文件路径
        """
        package = self.create_sync_package()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(package, f, ensure_ascii=False, indent=2, default=str)
        
        return file_path
    
    def import_sync_package(self, file_path, merge_mode='replace'):
        """从文件导入同步包
        
        Args:
            file_path: 导入文件路径
            merge_mode: 合并模式 ('replace' 替换, 'merge' 合并)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            package = json.load(f)
        
        # 验证包版本
        if package.get('version') != '1.0':
            raise ValueError(f'不支持的同步包版本: {package.get("version")}')
        
        # 导入数据
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('BEGIN TRANSACTION')
            
            for table_name, rows in package['tables'].items():
                if merge_mode == 'replace':
                    # 清空表后重新插入
                    cursor.execute(f'DELETE FROM {table_name}')
                
                for row in rows:
                    # 构建INSERT语句
                    columns = list(row.keys())
                    placeholders = ','.join(['?' for _ in columns])
                    values = [row[col] for col in columns]
                    
                    sql = f'INSERT OR REPLACE INTO {table_name} ({",".join(columns)}) VALUES ({placeholders})'
                    cursor.execute(sql, values)
            
            cursor.execute('COMMIT')
            
            # 更新同步时间
            config = self.get_sync_config()
            config['last_sync'] = datetime.datetime.now().isoformat()
            self.save_sync_config(config)
            
            return True
        
        except Exception as e:
            cursor.execute('ROLLBACK')
            raise e
    
    def sync_with_server(self, server_url):
        """与服务器同步数据
        
        Args:
            server_url: 服务器URL
        
        Returns:
            bool: 同步是否成功
        """
        import requests
        
        self.sync_status = 'syncing'
        
        try:
            # 创建同步包
            package = self.create_sync_package()
            
            # 发送到服务器
            response = requests.post(
                f'{server_url}/api/sync',
                json=package,
                timeout=30
            )
            
            if response.status_code == 200:
                # 处理服务器返回的数据
                server_data = response.json()
                self.apply_server_changes(server_data)
                
                self.sync_status = 'success'
                self.last_sync_time = datetime.datetime.now()
                return True
            else:
                self.sync_status = 'failed'
                return False
        
        except Exception as e:
            self.sync_status = 'failed'
            raise e
    
    def apply_server_changes(self, server_data):
        """应用服务器端的数据变更
        
        Args:
            server_data: 服务器返回的数据
        """
        # 合并服务器数据到本地
        for table_name, rows in server_data.get('tables', {}).items():
            for row in rows:
                self.merge_row(table_name, row)
    
    def merge_row(self, table_name, row):
        """合并单行数据
        
        Args:
            table_name: 表名
            row: 行数据字典
        """
        # 根据更新时间判断是否需要更新
        if 'updated_at' in row:
            local_row = self.db.fetch_one(
                f'SELECT updated_at FROM {table_name} WHERE id = ?',
                (row.get('id'),)
            )
            
            if local_row:
                local_time = local_row['updated_at']
                remote_time = row['updated_at']
                
                # 如果远程更新，更新本地
                if remote_time > local_time:
                    self.update_local_row(table_name, row)
                return
        
        # 默认直接插入或替换
        self.insert_or_replace_row(table_name, row)
    
    def update_local_row(self, table_name, row):
        """更新本地行"""
        self.insert_or_replace_row(table_name, row)
    
    def insert_or_replace_row(self, table_name, row):
        """插入或替换行"""
        columns = list(row.keys())
        placeholders = ','.join(['?' for _ in columns])
        values = [row[col] for col in columns]
        
        sql = f'INSERT OR REPLACE INTO {table_name} ({",".join(columns)}) VALUES ({placeholders})'
        self.db.execute(sql, values)
    
    def get_device_id(self):
        """获取设备ID"""
        config = self.get_sync_config()
        if 'device_id' not in config:
            import uuid
            config['device_id'] = str(uuid.uuid4())
            self.save_sync_config(config)
        return config['device_id']
    
    def get_sync_status(self):
        """获取同步状态"""
        config = self.get_sync_config()
        return {
            'status': self.sync_status,
            'last_sync': config.get('last_sync'),
            'device_id': self.get_device_id(),
        }


class ConflictResolver:
    """数据冲突解决器"""
    
    @staticmethod
    def resolve(local_data, remote_data, strategy='remote_wins'):
        """解决数据冲突
        
        Args:
            local_data: 本地数据
            remote_data: 远程数据
            strategy: 解决策略
                - 'remote_wins': 远程优先
                - 'local_wins': 本地优先
                - 'latest_wins': 最新优先
                - 'manual': 手动解决
        
        Returns:
            dict: 解决后的数据
        """
        if strategy == 'remote_wins':
            return remote_data
        
        elif strategy == 'local_wins':
            return local_data
        
        elif strategy == 'latest_wins':
            # 比较更新时间
            local_time = local_data.get('updated_at', '')
            remote_time = remote_data.get('updated_at', '')
            
            if remote_time > local_time:
                return remote_data
            else:
                return local_data
        
        elif strategy == 'manual':
            # 返回None表示需要手动处理
            return None
        
        return remote_data
    
    @staticmethod
    def merge_quantity(local_qty, remote_qty, operation='add'):
        """合并库存数量
        
        Args:
            local_qty: 本地数量
            remote_qty: 远程数量
            operation: 操作类型 ('replace', 'add', 'subtract')
        
        Returns:
            int: 合并后的数量
        """
        if operation == 'replace':
            return remote_qty
        elif operation == 'add':
            # 只保留较大的值
            return max(local_qty, remote_qty)
        elif operation == 'subtract':
            # 取平均
            return (local_qty + remote_qty) // 2
        return remote_qty


class SyncLog:
    """同步日志"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_table()
    
    def _ensure_table(self):
        """确保日志表存在"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT,
                direction TEXT,
                status TEXT,
                records_count INTEGER,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def log(self, sync_type, direction, status, records_count=0, error_message=''):
        """记录同步日志
        
        Args:
            sync_type: 同步类型 (full, incremental, manual)
            direction: 同步方向 (upload, download, bidirectional)
            status: 状态 (success, failed, partial)
            records_count: 记录数
            error_message: 错误信息
        """
        self.db.execute('''
            INSERT INTO sync_logs (sync_type, direction, status, records_count, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (sync_type, direction, status, records_count, error_message))
    
    def get_recent_logs(self, limit=10):
        """获取最近的同步日志"""
        return self.db.fetch_all('''
            SELECT * FROM sync_logs
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))


# 辅助函数
def sync_database_files(source_path, target_path):
    """同步两个数据库文件
    
    直接复制数据库文件，用于离线同步
    
    Args:
        source_path: 源数据库路径
        target_path: 目标数据库路径
    """
    import shutil
    
    # 备份目标文件
    if os.path.exists(target_path):
        backup_path = target_path + '.bak'
        shutil.copy2(target_path, backup_path)
    
    # 复制源文件到目标
    shutil.copy2(source_path, target_path)


def compare_databases(db1_path, db2_path):
    """比较两个数据库的差异
    
    Args:
        db1_path: 数据库1路径
        db2_path: 数据库2路径
    
    Returns:
        dict: 差异报告
    """
    conn1 = sqlite3.connect(db1_path)
    conn2 = sqlite3.connect(db2_path)
    
    conn1.row_factory = sqlite3.Row
    conn2.row_factory = sqlite3.Row
    
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()
    
    # 获取表列表
    cursor1.execute("SELECT name FROM sqlite_master WHERE type='table'")
    cursor2.execute("SELECT name FROM sqlite_master WHERE type='table'")
    
    tables1 = set(row[0] for row in cursor1.fetchall())
    tables2 = set(row[0] for row in cursor2.fetchall())
    
    report = {
        'tables_only_in_db1': list(tables1 - tables2),
        'tables_only_in_db2': list(tables2 - tables1),
        'common_tables': list(tables1 & tables2),
        'differences': {}
    }
    
    # 比较共有表的记录数
    for table in (tables1 & tables2):
        cursor1.execute(f'SELECT COUNT(*) FROM {table}')
        cursor2.execute(f'SELECT COUNT(*) FROM {table}')
        
        count1 = cursor1.fetchone()[0]
        count2 = cursor2.fetchone()[0]
        
        if count1 != count2:
            report['differences'][table] = {
                'db1_count': count1,
                'db2_count': count2,
                'diff': count2 - count1
            }
    
    conn1.close()
    conn2.close()
    
    return report
