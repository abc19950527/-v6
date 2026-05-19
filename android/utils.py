# -*- coding: utf-8 -*-
"""
工具函数模块
包含通用工具类和函数
"""

import os
import sys
import json
import hashlib
import datetime
import uuid


def get_app_dir():
    """获取应用数据目录"""
    if sys.platform == 'android':
        from android.storage import app_storage_path
        return app_storage_path()
    else:
        return os.path.dirname(os.path.abspath(__file__))


def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)


def get_timestamp():
    """获取当前时间戳"""
    return datetime.datetime.now().timestamp()


def get_datetime_string(fmt='%Y-%m-%d %H:%M:%S'):
    """获取格式化的时间字符串"""
    return datetime.datetime.now().strftime(fmt)


def get_date_string():
    """获取日期字符串"""
    return datetime.datetime.now().strftime('%Y-%m-%d')


def generate_order_no(prefix='XD'):
    """生成订单号
    
    Args:
        prefix: 订单号前缀
    
    Returns:
        str: 订单号
    """
    now = datetime.datetime.now()
    return f"{prefix}{now.strftime('%Y%m%d%H%M%S')}{now.microsecond // 10000:02d}"


def generate_card_no():
    """生成会员卡号"""
    now = datetime.datetime.now()
    return f"VIP{now.strftime('%m%d%H%M%S')}"


def md5_hash(text):
    """MD5哈希
    
    Args:
        text: 要哈希的文本
    
    Returns:
        str: 32位MD5哈希值
    """
    return hashlib.md5(text.encode()).hexdigest()


def sha256_hash(text):
    """SHA256哈希
    
    Args:
        text: 要哈希的文本
    
    Returns:
        str: 64位SHA256哈希值
    """
    return hashlib.sha256(text.encode()).hexdigest()


def validate_phone(phone):
    """验证手机号"""
    if not phone:
        return False
    phone = str(phone).strip()
    return len(phone) == 11 and phone.isdigit()


def validate_email(email):
    """验证邮箱"""
    if not email:
        return False
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_money(amount):
    """格式化金额
    
    Args:
        amount: 金额
    
    Returns:
        str: 格式化的金额字符串
    """
    return f'¥{float(amount):.2f}'


def format_number(num):
    """格式化数字"""
    return f'{float(num):,}'


def parse_money(text):
    """解析金额文本
    
    Args:
        text: 金额文本
    
    Returns:
        float: 金额数值
    """
    if not text:
        return 0.0
    # 移除货币符号和逗号
    text = str(text).replace('¥', '').replace(',', '').strip()
    try:
        return float(text)
    except:
        return 0.0


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _config_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置"""
        app_dir = get_app_dir()
        self._config_file = os.path.join(app_dir, 'config.json')
        
        if os.path.exists(self._config_file):
            with open(self._config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = self._default_config()
    
    def _default_config(self):
        """默认配置"""
        return {
            'store_name': '药品进销存管理系统',
            'printer_type': '58mm',
            'printer_address': '',
            'auto_sync': False,
            'sync_wifi_only': True,
            'expiry_warning_days': 180,
            'low_stock_warning': True,
            'theme': 'light',
            'font_size': 'normal',
        }
    
    def save(self):
        """保存配置"""
        with open(self._config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        """获取配置项"""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self._config[key] = value
        self.save()
    
    def __getitem__(self, key):
        return self._config.get(key)
    
    def __setitem__(self, key, value):
        self._config[key] = value
        self.save()


class Logger:
    """日志记录器"""
    
    _instance = None
    _log_file = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        """初始化"""
        app_dir = get_app_dir()
        ensure_dir(app_dir)
        self._log_file = os.path.join(app_dir, 'app.log')
    
    def _write(self, level, message):
        """写入日志"""
        timestamp = get_datetime_string()
        log_line = f'[{timestamp}] [{level}] {message}\n'
        
        try:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass
    
    def debug(self, message):
        self._write('DEBUG', message)
    
    def info(self, message):
        self._write('INFO', message)
    
    def warning(self, message):
        self._write('WARNING', message)
    
    def error(self, message):
        self._write('ERROR', message)
    
    def critical(self, message):
        self._write('CRITICAL', message)


class DataBackup:
    """数据备份类"""
    
    @staticmethod
    def backup_to_file(db_path, backup_path=None):
        """备份数据库到文件
        
        Args:
            db_path: 原数据库路径
            backup_path: 备份文件路径
        
        Returns:
            str: 备份文件路径
        """
        import shutil
        
        if backup_path is None:
            app_dir = get_app_dir()
            backup_dir = os.path.join(app_dir, 'backup')
            ensure_dir(backup_dir)
            
            timestamp = get_datetime_string('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        shutil.copy2(db_path, backup_path)
        return backup_path
    
    @staticmethod
    def restore_from_backup(backup_path, db_path):
        """从备份恢复数据库
        
        Args:
            backup_path: 备份文件路径
            db_path: 目标数据库路径
        """
        import shutil
        shutil.copy2(backup_path, db_path)
    
    @staticmethod
    def export_to_json(db_path, export_path):
        """导出数据库到JSON
        
        Args:
            db_path: 数据库路径
            export_path: 导出文件路径
        """
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        data = {}
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            data[table_name] = [dict(row) for row in rows]
        
        conn.close()
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        return export_path


# 全局实例
config = None
logger = None


def get_config():
    """获取配置管理器实例"""
    global config
    if config is None:
        config = ConfigManager()
    return config


def get_logger():
    """获取日志记录器实例"""
    global logger
    if logger is None:
        logger = Logger()
    return logger
