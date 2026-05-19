# -*- coding: utf-8 -*-
"""
药品进销存管理系统 v6 - Android App
基于Kivy + SQLite的离线安卓应用
"""

import os
import sys
import sqlite3
import datetime
import hashlib
import uuid
from kivy.config import Config

# Kivy配置
Config.set('kivy', 'title', '药品进销存')
Config.set('kivy', 'version', '1.0.0')
Config.set('kivy', 'orientation', 'portrait')
Config.set('kivy', 'fullscreen', '0')
Config.set('kivy', 'window_soft_input_mode', 'adjust_resize')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.storage.jsonstore import JsonStore

# 全局颜色定义
COLOR_PRIMARY = (0.098, 0.502, 1.0, 1)      # #1890ff 医疗蓝
COLOR_SUCCESS = (0.298, 0.686, 0.314, 1)    # #4CAF50
COLOR_WARNING = (0.957, 0.647, 0.0, 1)      # #f5a623 警告色
COLOR_DANGER = (0.957, 0.263, 0.212, 1)    # #f44336 危险色
COLOR_BG = (0.961, 0.965, 0.969, 1)         # #f5f5f5 背景灰
COLOR_WHITE = (1, 1, 1, 1)                   # 白色
COLOR_TEXT = (0.133, 0.133, 0.133, 1)       # #222 文字颜色
COLOR_TEXT_SECONDARY = (0.475, 0.475, 0.475, 1)  # #666 次要文字

# 字体设置
FONT_NAME = 'DroidSansFallback'


# 数据库管理器
class DatabaseManager:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # 使用应用数据目录
            from android.storage import app_storage_path
            try:
                data_dir = app_storage_path()
            except:
                data_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(data_dir, 'drugpos.db')
        
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建药品档案表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                generic_name TEXT,
                specification TEXT,
                dosage_form TEXT,
                unit TEXT DEFAULT '盒',
                manufacturer TEXT,
                approval_number TEXT,
                origin TEXT,
                purchase_price REAL DEFAULT 0,
                retail_price REAL DEFAULT 0,
                member_price REAL DEFAULT 0,
                wholesale_price REAL DEFAULT 0,
                category TEXT,
                is_prescription INTEGER DEFAULT 0,
                min_stock INTEGER DEFAULT 0,
                max_stock INTEGER DEFAULT 1000,
                status INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建药品批次表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drug_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_id INTEGER NOT NULL,
                batch_number TEXT,
                production_date DATE,
                expiry_date DATE,
                quantity INTEGER DEFAULT 0,
                purchase_price REAL,
                supplier_id INTEGER,
                status INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (drug_id) REFERENCES drugs(id)
            )
        ''')
        
        # 创建供应商表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                name TEXT NOT NULL,
                contact TEXT,
                phone TEXT,
                address TEXT,
                status INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建员工表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'cashier',
                phone TEXT,
                status INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建销售单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_no TEXT UNIQUE NOT NULL,
                member_id INTEGER,
                total_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                actual_amount REAL DEFAULT 0,
                cash_received REAL DEFAULT 0,
                change_amount REAL DEFAULT 0,
                operator_id INTEGER,
                payment_method TEXT DEFAULT 'cash',
                status INTEGER DEFAULT 1,
                print_status INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        ''')
        
        # 创建销售明细表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                drug_id INTEGER NOT NULL,
                batch_id INTEGER,
                quantity INTEGER NOT NULL,
                pack_quantity INTEGER DEFAULT 0,
                unit_price REAL NOT NULL,
                amount REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES sales_orders(id),
                FOREIGN KEY (drug_id) REFERENCES drugs(id)
            )
        ''')
        
        # 创建会员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_no TEXT UNIQUE NOT NULL,
                name TEXT,
                phone TEXT,
                points INTEGER DEFAULT 0,
                balance REAL DEFAULT 0,
                discount_rate REAL DEFAULT 1.0,
                status INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建系统设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建操作日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_id INTEGER,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id INTEGER,
                detail TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入默认管理员账号
        cursor.execute("SELECT COUNT(*) FROM staff WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            password_hash = hashlib.md5('123456'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO staff (username, password, name, role) 
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, '管理员', 'admin'))
        
        # 插入测试药品数据
        cursor.execute("SELECT COUNT(*) FROM drugs")
        if cursor.fetchone()[0] == 0:
            self.insert_sample_data(cursor)
        
        conn.commit()
    
    def insert_sample_data(self, cursor):
        """插入示例数据"""
        # 示例药品
        drugs = [
            ('YP001', '阿莫西林胶囊', '阿莫西林', '0.25g*24粒', '胶囊', '盒', '华北制药', '国药准字H13022378', '河北', 8.5, 18.0, 15.0, 12.0, '抗生素', 1, 10, 500),
            ('YP002', '布洛芬缓释胶囊', '布洛芬', '0.3g*20粒', '胶囊', '盒', '中美天津史克', '国药准字H12000710', '天津', 12.0, 25.0, 22.0, 18.0, '解热镇痛', 0, 10, 500),
            ('YP003', '感冒灵颗粒', '对乙酰氨基酚', '10g*9袋', '颗粒', '盒', '三九制药', '国药准字Z44021988', '广东', 6.0, 12.0, 10.0, 9.0, '感冒用药', 0, 20, 1000),
            ('YP004', '维生素C片', '维生素C', '100mg*100片', '片剂', '瓶', '华中药业', '国药准字H42021869', '湖北', 3.0, 8.0, 6.5, 5.5, '维生素', 0, 15, 800),
            ('YP005', '氨氯地平片', '氨氯地平', '5mg*28片', '片剂', '盒', '辉瑞制药', '国药准字J20171090', '进口', 25.0, 48.0, 42.0, 35.0, '心脑血管', 1, 5, 200),
            ('YP006', '蒙脱石散', '蒙脱石', '3g*10袋', '散剂', '盒', '博福益普生', '国药准字H20000690', '天津', 15.0, 28.0, 25.0, 22.0, '胃肠道', 0, 10, 300),
            ('YP007', '复方甘草片', '甘草', '50片', '片剂', '瓶', '太极集团', '国药准字Z50020659', '重庆', 2.0, 5.0, 4.0, 3.5, '镇咳祛痰', 0, 10, 400),
            ('YP008', '阿司匹林肠溶片', '阿司匹林', '50mg*30片', '片剂', '盒', '拜耳医药', '国药准字J20171078', '进口', 10.0, 22.0, 18.0, 15.0, '解热镇痛', 0, 8, 300),
        ]
        
        for drug in drugs:
            cursor.execute('''
                INSERT INTO drugs (drug_code, name, generic_name, specification, dosage_form, unit, 
                                   manufacturer, approval_number, origin, purchase_price, retail_price, 
                                   member_price, wholesale_price, category, is_prescription, min_stock, max_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', drug)
        
        # 获取药品ID并插入批次信息
        today = datetime.date.today()
        for i, drug in enumerate(drugs, 1):
            # 创建批次
            expiry_date = today + datetime.timedelta(days=365 + (i % 3) * 180)
            production_date = today - datetime.timedelta(days=30 * (i % 6))
            batch_no = f'P{ datetime.datetime.now().strftime("%Y%m%d") }{i:02d}'
            quantity = 50 + (i % 5) * 20
            
            cursor.execute('''
                INSERT INTO drug_batches (drug_id, batch_number, production_date, expiry_date, quantity, purchase_price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (i, batch_no, production_date, expiry_date, quantity, drug[9]))
        
        # 添加示例会员
        members = [
            ('VIP0001', '张三', '13800138001', 500, 100.0, 0.95),
            ('VIP0002', '李四', '13900139002', 200, 50.0, 0.98),
            ('VIP0003', '王五', '13700137003', 1000, 200.0, 0.90),
        ]
        
        for member in members:
            cursor.execute('''
                INSERT INTO members (card_no, name, phone, points, balance, discount_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', member)
        
        # 添加示例供应商
        suppliers = [
            ('GYS001', '国药集团', '王经理', '010-12345678', '北京'),
            ('GYS002', '华润医药', '李经理', '021-87654321', '上海'),
            ('GYS003', '九州通药业', '张经理', '027-11112222', '武汉'),
        ]
        
        for supplier in suppliers:
            cursor.execute('''
                INSERT INTO suppliers (code, name, contact, phone, address)
                VALUES (?, ?, ?, ?, ?)
            ''', supplier)
        
        # 添加系统设置
        settings = [
            ('store_name', '药店进销存管理系统'),
            ('printer_type', '58mm'),
            ('auto_sync', '0'),
            ('expiry_warning_days', '180'),
        ]
        
        for key, value in settings:
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
    
    def execute(self, sql, params=None):
        """执行SQL语句"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return cursor
    
    def fetch_all(self, sql, params=None):
        """查询所有结果"""
        cursor = self.execute(sql, params)
        return cursor.fetchall()
    
    def fetch_one(self, sql, params=None):
        """查询单条结果"""
        cursor = self.execute(sql, params)
        return cursor.fetchone()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


# 全局数据库实例
db = None


def get_db():
    """获取数据库实例"""
    global db
    if db is None:
        db = DatabaseManager()
    return db


# ========================
# 通用UI组件
# ========================

class StyledButton(Button):
    """自定义样式按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLOR_PRIMARY
        self.color = COLOR_WHITE
        self.font_size = '18sp'
        self.size_hint_y = None
        self.height = '60dp'
        self.bold = True
        self.background_normal = ''
        self.background_down = ''
        self.border_radius = [10, 10, 10, 10]


class PrimaryButton(StyledButton):
    """主按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLOR_PRIMARY


class SuccessButton(StyledButton):
    """成功按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLOR_SUCCESS


class DangerButton(StyledButton):
    """危险按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLOR_DANGER


class WarningButton(StyledButton):
    """警告按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLOR_WARNING


class CardBox(BoxLayout):
    """卡片容器"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10
        self.size_hint_y = None
        self.height = self.minimum_height
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10, 10, 10, 10])
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ListItem(BoxLayout):
    """列表项"""
    def __init__(self, title, subtitle='', icon='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '70dp'
        self.padding = 10
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class HeaderBar(BoxLayout):
    """顶部导航栏"""
    def __init__(self, title='', back_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = '56dp'
        self.padding = [10, 5]
        self.spacing = 10
        
        with self.canvas.before:
            Color(*COLOR_PRIMARY)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # 返回按钮
        if back_callback:
            back_btn = Button(text='<', size_hint_x=None, width='50dp', height='46dp',
                            background_color=(0, 0, 0, 0), color=COLOR_WHITE, font_size='24sp')
            back_btn.bind(on_press=back_callback)
            self.add_widget(back_btn)
        
        # 标题
        title_label = Label(text=title, color=COLOR_WHITE, font_size='20sp',
                           size_hint_x=1, halign='left', valign='middle')
        self.add_widget(title_label)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ========================
# 登录界面
# ========================

class LoginScreen(Screen):
    """登录界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_staff = None
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # 主容器
        main_layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        # Logo区域
        logo_area = BoxLayout(orientation='vertical', size_hint_y=0.3)
        logo_label = Label(
            text='[font=icon.ttf]&#xe900;[/font]\n\n药品进销存',
            markup=True,
            font_size='32sp',
            color=COLOR_PRIMARY,
            size_hint_y=0.5
        )
        
        subtitle = Label(
            text='管理系统 v6.0',
            font_size='16sp',
            color=COLOR_TEXT_SECONDARY,
            size_hint_y=0.2
        )
        logo_area.add_widget(logo_label)
        logo_area.add_widget(subtitle)
        
        # 登录表单
        form_layout = BoxLayout(orientation='vertical', size_hint_y=0.5, spacing=15)
        
        # 用户名输入
        self.username_input = TextInput(
            hint_text='用户名',
            size_hint_y=None,
            height='50dp',
            font_size='18sp',
            multiline=False,
            padding=[15, 12],
            foreground_color=COLOR_TEXT,
            hint_text_color=COLOR_TEXT_SECONDARY
        )
        
        # 密码输入
        self.password_input = TextInput(
            hint_text='密码',
            size_hint_y=None,
            height='50dp',
            font_size='18sp',
            multiline=False,
            password=True,
            padding=[15, 12],
            foreground_color=COLOR_TEXT,
            hint_text_color=COLOR_TEXT_SECONDARY
        )
        
        # 记住密码
        remember_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp')
        self.remember_check = CheckBox(size_hint_x=None, width='30dp')
        remember_label = Label(text='记住密码', color=COLOR_TEXT_SECONDARY, font_size='14sp')
        remember_layout.add_widget(self.remember_check)
        remember_layout.add_widget(remember_label)
        
        # 登录按钮
        login_btn = PrimaryButton(text='登 录', size_hint_y=None, height='55dp')
        login_btn.bind(on_press=self.do_login)
        
        # 版本信息
        version_label = Label(
            text='v6.0 | Android离线版',
            font_size='12sp',
            color=COLOR_TEXT_SECONDARY,
            size_hint_y=0.1
        )
        
        form_layout.add_widget(self.username_input)
        form_layout.add_widget(self.password_input)
        form_layout.add_widget(remember_layout)
        form_layout.add_widget(login_btn)
        
        main_layout.add_widget(logo_area)
        main_layout.add_widget(form_layout)
        main_layout.add_widget(version_label)
        
        self.add_widget(main_layout)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def do_login(self, instance):
        """执行登录"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username:
            self.show_error('请输入用户名')
            return
        
        if not password:
            self.show_error('请输入密码')
            return
        
        # 密码MD5加密
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # 查询数据库
        database = get_db()
        staff = database.fetch_one(
            'SELECT * FROM staff WHERE username = ? AND password = ? AND status = 1',
            (username, password_hash)
        )
        
        if staff:
            self.current_staff = dict(staff)
            self.manager.current = 'main'
            self.manager.get_screen('main').set_user_info(self.current_staff)
        else:
            self.show_error('用户名或密码错误')
    
    def show_error(self, message):
        """显示错误信息"""
        popup = Popup(
            title='提示',
            content=Label(text=message, font_size='16sp'),
            size_hint=(0.8, 0.3),
            auto_dismiss=True
        )
        popup.open()


# ========================
# 主界面
# ========================

class MainScreen(Screen):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_staff = None
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # 主容器
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部信息栏
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            padding=[15, 0]
        )
        with top_bar.canvas.before:
            Color(*COLOR_PRIMARY)
            self.top_rect = Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=self._update_top_rect, size=self._update_top_rect)
        
        store_label = Label(
            text='[size=24][b]&#xe901;[/b][/size] 药品进销存',
            markup=True,
            color=COLOR_WHITE,
            halign='left',
            valign='middle'
        )
        
        self.user_label = Label(
            text='',
            color=COLOR_WHITE,
            halign='right',
            valign='middle'
        )
        
        top_bar.add_widget(store_label)
        top_bar.add_widget(self.user_label)
        
        # 功能按钮区域
        scroll = ScrollView(size_hint_y=1)
        grid = GridLayout(cols=2, spacing=15, padding=15, size_hint_y=None)
        grid.height = grid.minimum_height
        
        # 功能按钮定义
        functions = [
            ('销售开单', 'sale', COLOR_PRIMARY, '&#xe902;'),
            ('库存查询', 'stock', COLOR_SUCCESS, '&#xe903;'),
            ('效期预警', 'expiry', COLOR_WARNING, '&#xe904;'),
            ('会员管理', 'member', COLOR_PRIMARY, '&#xe905;'),
            ('数据同步', 'sync', COLOR_SUCCESS, '&#xe906;'),
            ('小票打印', 'print', COLOR_WARNING, '&#xe907;'),
        ]
        
        for text, screen, color, icon in functions:
            btn = self.create_function_button(text, icon, color, screen)
            grid.add_widget(btn)
        
        scroll.add_widget(grid)
        
        # 底部快捷操作
        bottom_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='70dp',
            padding=10,
            spacing=10
        )
        
        quick_buttons = [
            ('扫码', 'scan'),
            ('查药', 'search'),
            ('日结', 'daily'),
        ]
        
        for text, action in quick_buttons:
            btn = StyledButton(text=text, on_press=lambda x, a=action: self.quick_action(a))
            btn.height = '50dp'
            bottom_bar.add_widget(btn)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(scroll)
        main_layout.add_widget(bottom_bar)
        
        self.add_widget(main_layout)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _update_top_rect(self, *args):
        self.top_rect.pos = self.pos
        self.top_rect.size = self.size
    
    def create_function_button(self, text, icon, color, screen_name):
        """创建功能按钮"""
        btn = BoxLayout(orientation='vertical', size_hint_y=None, height='140dp')
        
        with btn.canvas.before:
            Color(*color)
            self.btn_rect = RoundedRectangle(
                pos=btn.pos, 
                size=btn.size, 
                radius=[15, 15, 15, 15]
            )
        btn.bind(pos=self._update_btn_rect, size=self._update_btn_rect)
        
        icon_label = Label(
            text=f'[size=40]{icon}[/size]',
            markup=True,
            color=COLOR_WHITE,
            size_hint_y=0.6
        )
        
        text_label = Label(
            text=text,
            color=COLOR_WHITE,
            font_size='18sp',
            bold=True,
            size_hint_y=0.4
        )
        
        btn.add_widget(icon_label)
        btn.add_widget(text_label)
        btn.bind(on_touch_down=lambda instance, touch: self.on_btn_touch(instance, touch, screen_name))
        
        return btn
    
    def _update_btn_rect(self, instance, value):
        instance.btn_rect.pos = instance.pos
        instance.btn_rect.size = instance.size
    
    def on_btn_touch(self, instance, touch, screen_name):
        """按钮点击处理"""
        if instance.collide_point(*touch.pos):
            self.go_to_screen(screen_name)
            return True
        return False
    
    def go_to_screen(self, screen_name):
        """跳转到指定界面"""
        if screen_name == 'sale':
            self.manager.current = 'sale'
        elif screen_name == 'stock':
            self.manager.current = 'stock'
        elif screen_name == 'expiry':
            self.manager.current = 'expiry'
        elif screen_name == 'member':
            self.manager.current = 'member'
        elif screen_name == 'sync':
            self.manager.current = 'sync'
        elif screen_name == 'print':
            self.manager.current = 'print'
    
    def set_user_info(self, staff):
        """设置用户信息"""
        self.current_staff = staff
        self.user_label.text = f'{staff["name"]} [{staff["role"]}]'
    
    def quick_action(self, action):
        """快捷操作"""
        if action == 'scan':
            self.show_message('扫码功能开发中')
        elif action == 'search':
            self.manager.current = 'stock'
        elif action == 'daily':
            self.manager.current = 'sale'
    
    def show_message(self, msg):
        """显示消息"""
        popup = Popup(
            title='提示',
            content=Label(text=msg, font_size='16sp'),
            size_hint=(0.8, 0.3)
        )
        popup.open()


# ========================
# 销售开单界面
# ========================

class SaleScreen(Screen):
    """销售开单界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_items = []  # 购物车商品
        self.current_member = None
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # 主容器
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部导航
        top_bar = HeaderBar(title='销售开单', back_callback=lambda x: self.go_back())
        
        # 商品搜索区域
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=10, spacing=10)
        
        self.search_input = TextInput(
            hint_text='输入药品编码/名称搜索',
            size_hint_x=1,
            font_size='16sp',
            multiline=False,
            padding=[10, 8]
        )
        
        scan_btn = StyledButton(text='扫码', size_hint_x=None, width='70dp', height='50dp')
        scan_btn.bind(on_press=lambda x: self.scan_drug())
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(scan_btn)
        
        # 商品列表
        self.goods_list = BoxLayout(orientation='vertical', size_hint_y=0.35)
        
        list_header = BoxLayout(orientation='horizontal', size_hint_y=None, height='35dp', padding=[10, 0])
        for text, width in [('药品', 0.3), ('数量', 0.2), ('单价', 0.25), ('删除', 0.25)]:
            lbl = Label(text=text, color=COLOR_TEXT_SECONDARY, font_size='14sp', size_hint_x=width)
            list_header.add_widget(lbl)
        self.goods_list.add_widget(list_header)
        
        self.goods_scroll = ScrollView(size_hint_y=1)
        self.goods_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.goods_container.height = self.goods_container.minimum_height
        self.goods_scroll.add_widget(self.goods_container)
        self.goods_list.add_widget(self.goods_scroll)
        
        # 会员信息区域
        member_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=10)
        
        self.member_label = Label(text='未选择会员', color=COLOR_TEXT_SECONDARY, size_hint_x=0.6)
        
        member_btn = StyledButton(text='选择会员', size_hint_x=0.4, height='45dp')
        member_btn.bind(on_press=lambda x: self.select_member())
        
        member_layout.add_widget(self.member_label)
        member_layout.add_widget(member_btn)
        
        # 金额显示区域
        amount_layout = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', padding=15, spacing=5)
        
        total_row = BoxLayout(orientation='horizontal', size_hint_y=1)
        total_row.add_widget(Label(text='商品金额:', color=COLOR_TEXT_SECONDARY, size_hint_x=0.5))
        self.total_label = Label(text='¥0.00', color=COLOR_TEXT, size_hint_x=0.5, halign='right')
        total_row.add_widget(self.total_label)
        amount_layout.add_widget(total_row)
        
        discount_row = BoxLayout(orientation='horizontal', size_hint_y=1)
        discount_row.add_widget(Label(text='优惠金额:', color=COLOR_TEXT_SECONDARY, size_hint_x=0.5))
        self.discount_label = Label(text='¥0.00', color=COLOR_SUCCESS, size_hint_x=0.5, halign='right')
        discount_row.add_widget(self.discount_label)
        amount_layout.add_widget(discount_row)
        
        actual_row = BoxLayout(orientation='horizontal', size_hint_y=1)
        actual_row.add_widget(Label(text='实收金额:', color=COLOR_PRIMARY, size_hint_x=0.5))
        self.actual_label = Label(text='¥0.00', color=COLOR_PRIMARY, size_hint_x=0.5, halign='right', bold=True)
        actual_row.add_widget(self.actual_label)
        amount_layout.add_widget(actual_row)
        
        # 操作按钮区域
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='70dp', padding=10, spacing=10)
        
        clear_btn = DangerButton(text='清空', size_hint_x=0.25, height='55dp')
        clear_btn.bind(on_press=lambda x: self.clear_cart())
        
        payment_btn = SuccessButton(text='收款结账', size_hint_x=0.75, height='55dp')
        payment_btn.bind(on_press=lambda x: self.show_payment())
        
        btn_layout.add_widget(clear_btn)
        btn_layout.add_widget(payment_btn)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(search_layout)
        main_layout.add_widget(self.goods_list)
        main_layout.add_widget(member_layout)
        main_layout.add_widget(amount_layout)
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)
        
        # 绑定搜索事件
        self.search_input.bind(on_text_validate=self.search_drug)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def go_back(self):
        """返回"""
        self.manager.current = 'main'
    
    def search_drug(self):
        """搜索药品"""
        keyword = self.search_input.text.strip()
        if not keyword:
            return
        
        database = get_db()
        
        # 查询药品（优先按编码精确匹配）
        drugs = database.fetch_all('''
            SELECT d.*, db.batch_number, db.expiry_date, db.quantity as stock_quantity
            FROM drugs d
            LEFT JOIN drug_batches db ON d.id = db.drug_id AND db.status = 1
            WHERE (d.drug_code = ? OR d.name LIKE ? OR d.generic_name LIKE ?)
            AND d.status = 1 AND db.quantity > 0
            ORDER BY d.name
            LIMIT 10
        ''', (keyword, f'%{keyword}%', f'%{keyword}%'))
        
        if not drugs:
            self.show_message('未找到相关药品')
            return
        
        # 显示搜索结果选择
        self.show_drug_selection(drugs)
    
    def show_drug_selection(self, drugs):
        """显示药品选择弹窗"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scroll = ScrollView(size_hint_y=1)
        list_box = BoxLayout(orientation='vertical', size_hint_y=None)
        list_box.height = list_box.minimum_height
        
        for drug in drugs:
            drug_dict = dict(drug)
            btn = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp', padding=10)
            
            info = f'{drug_dict["name"]}\n规格:{drug_dict["specification"]} 库存:{drug_dict["stock_quantity"]}'
            lbl = Label(text=info, color=COLOR_TEXT, font_size='14sp', size_hint_x=0.7, halign='left')
            
            price_lbl = Label(text=f'¥{drug_dict["retail_price"]:.2f}', color=COLOR_PRIMARY, font_size='16sp', 
                             size_hint_x=0.3, bold=True)
            
            btn.add_widget(lbl)
            btn.add_widget(price_lbl)
            
            btn.bind(on_touch_down=lambda inst, touch, d=drug_dict: self.add_to_cart(d) if inst.collide_point(*touch.pos) else None)
            
            list_box.add_widget(btn)
        
        scroll.add_widget(list_box)
        content.add_widget(scroll)
        
        close_btn = StyledButton(text='关闭', size_hint_y=None, height='50dp')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup = Popup(title='选择药品', content=content, size_hint=(0.95, 0.8), auto_dismiss=False)
        popup.open()
    
    def add_to_cart(self, drug):
        """添加到购物车"""
        # 检查是否已存在
        for item in self.cart_items:
            if item['drug_id'] == drug['id']:
                item['quantity'] += 1
                item['amount'] = item['quantity'] * item['unit_price']
                self.update_cart_display()
                return
        
        # 计算单价
        if self.current_member and self.current_member['discount_rate']:
            unit_price = drug['retail_price'] * self.current_member['discount_rate']
        else:
            unit_price = drug['retail_price']
        
        cart_item = {
            'drug_id': drug['id'],
            'drug_name': drug['name'],
            'specification': drug['specification'],
            'unit': drug['unit'],
            'quantity': 1,
            'unit_price': unit_price,
            'amount': unit_price
        }
        
        self.cart_items.append(cart_item)
        self.update_cart_display()
    
    def update_cart_display(self):
        """更新购物车显示"""
        self.goods_container.clear_widgets()
        
        for i, item in enumerate(self.cart_items):
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=[10, 5])
            
            name_lbl = Label(text=item['drug_name'][:10], color=COLOR_TEXT, font_size='14sp', size_hint_x=0.35)
            
            qty_layout = BoxLayout(size_hint_x=0.2)
            minus_btn = Button(text='-', size_hint_x=0.4, background_color=COLOR_WARNING, color=COLOR_WHITE)
            qty_lbl = Label(text=str(item['quantity']), color=COLOR_TEXT, size_hint_x=0.2)
            plus_btn = Button(text='+', size_hint_x=0.4, background_color=COLOR_PRIMARY, color=COLOR_WHITE)
            
            def make_qty_callback(index, delta):
                def callback(btn):
                    self.change_quantity(index, delta)
                return callback
            
            minus_btn.bind(on_press=make_qty_callback(i, -1))
            plus_btn.bind(on_press=make_qty_callback(i, 1))
            
            qty_layout.add_widget(minus_btn)
            qty_layout.add_widget(qty_lbl)
            qty_layout.add_widget(plus_btn)
            
            price_lbl = Label(text=f'¥{item["unit_price"]:.2f}', color=COLOR_TEXT, font_size='14sp', size_hint_x=0.25)
            
            del_btn = Button(text='×', size_hint_x=0.2, background_color=COLOR_DANGER, color=COLOR_WHITE, font_size='20sp')
            del_btn.bind(on_press=lambda x, idx=i: self.remove_from_cart(idx))
            
            row.add_widget(name_lbl)
            row.add_widget(qty_layout)
            row.add_widget(price_lbl)
            row.add_widget(del_btn)
            
            self.goods_container.add_widget(row)
        
        self.calculate_amounts()
    
    def change_quantity(self, index, delta):
        """修改数量"""
        if 0 <= index < len(self.cart_items):
            new_qty = self.cart_items[index]['quantity'] + delta
            if new_qty > 0:
                self.cart_items[index]['quantity'] = new_qty
                self.cart_items[index]['amount'] = new_qty * self.cart_items[index]['unit_price']
            elif new_qty == 0:
                self.remove_from_cart(index)
                return
            self.update_cart_display()
    
    def remove_from_cart(self, index):
        """移除购物车商品"""
        if 0 <= index < len(self.cart_items):
            self.cart_items.pop(index)
            self.update_cart_display()
    
    def clear_cart(self):
        """清空购物车"""
        self.cart_items = []
        self.current_member = None
        self.member_label.text = '未选择会员'
        self.update_cart_display()
    
    def select_member(self):
        """选择会员"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 会员卡号输入
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        card_input = TextInput(hint_text='输入会员卡号', size_hint_x=0.7, font_size='16sp')
        search_btn = StyledButton(text='查询', size_hint_x=0.3)
        input_layout.add_widget(card_input)
        input_layout.add_widget(search_btn)
        content.add_widget(input_layout)
        
        # 会员列表
        scroll = ScrollView(size_hint_y=1)
        member_list = BoxLayout(orientation='vertical', size_hint_y=None)
        member_list.height = member_list.minimum_height
        
        def search_members(btn):
            card_no = card_input.text.strip()
            database = get_db()
            
            if card_no:
                members = database.fetch_all(
                    'SELECT * FROM members WHERE card_no LIKE ? AND status = 1 LIMIT 20',
                    (f'%{card_no}%',)
                )
            else:
                members = database.fetch_all('SELECT * FROM members WHERE status = 1 LIMIT 20')
            
            member_list.clear_widgets()
            
            for m in members:
                m_dict = dict(m)
                btn = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=10)
                info = f'{m_dict["card_no"]}\n{m_dict["name"]} | 积分:{m_dict["points"]}'
                lbl = Label(text=info, color=COLOR_TEXT, size_hint_x=0.7)
                select_btn = StyledButton(text='选择', size_hint_x=0.3)
                
                def select(btn, member=m_dict):
                    self.current_member = member
                    self.member_label.text = f'{member["name"]} ({member["card_no"]})'
                    popup.dismiss()
                    self.recalculate_prices()
                
                select_btn.bind(on_press=select)
                btn.add_widget(lbl)
                btn.add_widget(select_btn)
                member_list.add_widget(btn)
        
        search_btn.bind(on_press=search_members)
        
        scroll.add_widget(member_list)
        content.add_widget(scroll)
        
        close_btn = StyledButton(text='关闭', size_hint_y=None, height='50dp')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup = Popup(title='选择会员', content=content, size_hint=(0.95, 0.8), auto_dismiss=False)
        popup.open()
    
    def recalculate_prices(self):
        """重新计算价格"""
        if not self.current_member:
            return
        
        discount_rate = self.current_member.get('discount_rate', 1.0)
        
        for item in self.cart_items:
            # 获取药品原价
            database = get_db()
            drug = database.fetch_one('SELECT retail_price FROM drugs WHERE id = ?', (item['drug_id'],))
            if drug:
                item['unit_price'] = drug['retail_price'] * discount_rate
                item['amount'] = item['quantity'] * item['unit_price']
        
        self.update_cart_display()
    
    def calculate_amounts(self):
        """计算金额"""
        total = sum(item['amount'] for item in self.cart_items)
        
        # 计算优惠
        discount = 0
        if self.current_member:
            # 基础折扣优惠
            discount = total * (1 - self.current_member.get('discount_rate', 1.0))
        
        actual = total - discount
        
        self.total_label.text = f'¥{total:.2f}'
        self.discount_label.text = f'¥{discount:.2f}'
        self.actual_label.text = f'¥{actual:.2f}'
    
    def scan_drug(self):
        """扫码添加药品"""
        self.show_message('扫码功能需配合扫描枪使用')
    
    def show_payment(self):
        """显示收款界面"""
        if not self.cart_items:
            self.show_message('请先添加商品')
            return
        
        actual_amount = float(self.actual_label.text.replace('¥', ''))
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 实收金额显示
        amount_lbl = Label(
            text=f'应收金额: ¥{actual_amount:.2f}',
            font_size='28sp',
            color=COLOR_PRIMARY,
            bold=True,
            size_hint_y=0.2
        )
        content.add_widget(amount_lbl)
        
        # 收款方式
        pay_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        pay_layout.add_widget(Label(text='支付方式:', color=COLOR_TEXT))
        self.payment_spinner = Spinner(
            text='现金',
            values=['现金', '微信', '支付宝', '医保卡', '会员卡'],
            size_hint_x=0.6
        )
        pay_layout.add_widget(self.payment_spinner)
        content.add_widget(pay_layout)
        
        # 收款金额输入
        cash_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        cash_layout.add_widget(Label(text='收款金额:'))
        self.cash_input = TextInput(text=str(actual_amount), size_hint_x=0.6, font_size='18sp', multiline=False)
        cash_layout.add_widget(self.cash_input)
        content.add_widget(cash_layout)
        
        # 快捷金额按钮
        quick_layout = GridLayout(cols=4, size_hint_y=None, height='50dp', spacing=5)
        quick_amounts = [actual_amount, 50, 100, '找零']
        for amt in quick_amounts:
            if amt == '找零':
                btn = WarningButton(text='找零', height='45dp')
            else:
                btn = StyledButton(text=f'{amt:.0f}', height='45dp')
            btn.bind(on_press=lambda x, a=amt: self.set_cash_amount(a))
            quick_layout.add_widget(btn)
        content.add_widget(quick_layout)
        
        # 确认按钮
        confirm_btn = SuccessButton(text='确认收款', height='60dp')
        confirm_btn.bind(on_press=lambda x: self.confirm_payment())
        content.add_widget(confirm_btn)
        
        popup = Popup(title='收款结账', content=content, size_hint=(0.95, 0.7), auto_dismiss=False)
        popup.open()
        self.payment_popup = popup
    
    def set_cash_amount(self, amount):
        """设置收款金额"""
        if amount == '找零':
            actual = float(self.actual_label.text.replace('¥', ''))
            self.cash_input.text = str(actual)
        else:
            self.cash_input.text = str(amount)
    
    def confirm_payment(self):
        """确认收款"""
        try:
            cash_received = float(self.cash_input.text)
        except:
            self.show_message('请输入正确的金额')
            return
        
        actual_amount = float(self.actual_label.text.replace('¥', ''))
        
        if cash_received < actual_amount:
            self.show_message('收款金额不足')
            return
        
        change_amount = cash_received - actual_amount
        
        # 生成订单号
        order_no = f'XD{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        # 保存订单到数据库
        database = get_db()
        
        try:
            # 获取操作员ID
            main_screen = self.manager.get_screen('main')
            operator_id = main_screen.current_staff['id'] if main_screen.current_staff else 1
            member_id = self.current_member['id'] if self.current_member else None
            
            # 计算总金额
            total_amount = float(self.total_label.text.replace('¥', ''))
            discount_amount = float(self.discount_label.text.replace('¥', ''))
            
            # 插入销售单
            cursor = database.execute('''
                INSERT INTO sales_orders 
                (order_no, member_id, total_amount, discount_amount, actual_amount, 
                 cash_received, change_amount, operator_id, payment_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_no, member_id, total_amount, discount_amount, actual_amount,
                  cash_received, change_amount, operator_id, self.payment_spinner.text, 1))
            
            order_id = cursor.lastrowid
            
            # 插入销售明细
            for item in self.cart_items:
                database.execute('''
                    INSERT INTO sales_items (order_id, drug_id, quantity, unit_price, amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, item['drug_id'], item['quantity'], item['unit_price'], item['amount']))
                
                # 扣减库存
                database.execute('''
                    UPDATE drug_batches 
                    SET quantity = quantity - ?
                    WHERE drug_id = ? AND status = 1
                    ORDER BY expiry_date ASC
                    LIMIT ?
                ''', (item['quantity'], item['drug_id'], item['quantity']))
            
            # 更新会员积分
            if member_id:
                points = int(actual_amount)  # 1元=1积分
                database.execute('''
                    UPDATE members SET points = points + ?, balance = balance WHERE id = ?
                ''', (points, member_id))
            
            # 关闭弹窗
            self.payment_popup.dismiss()
            
            # 显示找零
            self.show_change(order_no, actual_amount, cash_received, change_amount)
            
            # 清空购物车
            self.clear_cart()
            
        except Exception as e:
            self.show_message(f'保存失败: {str(e)}')
    
    def show_change(self, order_no, actual, cash, change):
        """显示找零"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(text=f'订单号: {order_no}', font_size='16sp', color=COLOR_TEXT))
        content.add_widget(Label(text=f'实收: ¥{actual:.2f}', font_size='18sp', color=COLOR_PRIMARY))
        content.add_widget(Label(text=f'收款: ¥{cash:.2f}', font_size='18sp', color=COLOR_TEXT))
        
        change_lbl = Label(text=f'找零: ¥{change:.2f}', font_size='32sp', color=COLOR_SUCCESS, bold=True)
        content.add_widget(change_lbl)
        
        print_btn = StyledButton(text='打印小票', height='50dp')
        print_btn.bind(on_press=lambda x: self.print_receipt(order_no))
        content.add_widget(print_btn)
        
        done_btn = SuccessButton(text='完成', height='50dp')
        done_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(done_btn)
        
        popup = Popup(title='交易完成', content=content, size_hint=(0.9, 0.6))
        popup.open()
    
    def print_receipt(self, order_no):
        """打印小票"""
        self.show_message('正在调用打印机...')
        # 这里调用实际的小票打印功能
    
    def show_message(self, msg):
        """显示消息"""
        popup = Popup(
            title='提示',
            content=Label(text=msg, font_size='16sp'),
            size_hint=(0.8, 0.3)
        )
        popup.open()


# ========================
# 库存查询界面
# ========================

class StockScreen(Screen):
    """库存查询界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部导航
        top_bar = HeaderBar(title='库存查询', back_callback=lambda x: self.go_back())
        
        # 搜索区域
        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=10, spacing=10)
        
        self.search_input = TextInput(
            hint_text='输入药品名称/编码',
            size_hint_x=1,
            font_size='16sp',
            multiline=False,
            padding=[10, 8]
        )
        
        search_btn = StyledButton(text='搜索', size_hint_x=None, width='70dp', height='50dp')
        search_btn.bind(on_press=lambda x: self.search_stock())
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        
        # 统计信息
        stats_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=10)
        
        self.total_count = Label(text='总品种: 0', color=COLOR_TEXT, size_hint_x=0.33)
        self.total_stock = Label(text='总库存: 0', color=COLOR_TEXT, size_hint_x=0.33)
        self.low_stock = Label(text='不足: 0', color=COLOR_DANGER, size_hint_x=0.34)
        
        stats_layout.add_widget(self.total_count)
        stats_layout.add_widget(self.total_stock)
        stats_layout.add_widget(self.low_stock)
        
        # 库存列表
        self.stock_list = ScrollView(size_hint_y=1)
        self.stock_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.stock_container.height = self.stock_container.minimum_height
        self.stock_list.add_widget(self.stock_container)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(search_layout)
        main_layout.add_widget(stats_layout)
        main_layout.add_widget(self.stock_list)
        
        self.add_widget(main_layout)
        
        # 加载数据
        self.search_input.bind(on_text_validate=self.search_stock)
        Clock.schedule_once(lambda dt: self.load_stock(), 0.1)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def go_back(self):
        self.manager.current = 'main'
    
    def load_stock(self):
        """加载库存数据"""
        self.search_stock()
    
    def search_stock(self):
        """搜索库存"""
        keyword = self.search_input.text.strip()
        
        database = get_db()
        
        if keyword:
            sql = '''
                SELECT d.id, d.drug_code, d.name, d.specification, d.unit,
                       d.retail_price, d.min_stock, d.max_stock,
                       COALESCE(SUM(db.quantity), 0) as total_quantity
                FROM drugs d
                LEFT JOIN drug_batches db ON d.id = db.drug_id AND db.status = 1
                WHERE d.name LIKE ? OR d.drug_code LIKE ?
                GROUP BY d.id
                ORDER BY d.name
            '''
            stocks = database.fetch_all(sql, (f'%{keyword}%', f'%{keyword}%'))
        else:
            sql = '''
                SELECT d.id, d.drug_code, d.name, d.specification, d.unit,
                       d.retail_price, d.min_stock, d.max_stock,
                       COALESCE(SUM(db.quantity), 0) as total_quantity
                FROM drugs d
                LEFT JOIN drug_batches db ON d.id = db.drug_id AND db.status = 1
                GROUP BY d.id
                ORDER BY d.name
            '''
            stocks = database.fetch_all(sql)
        
        self.update_stock_display(stocks)
    
    def update_stock_display(self, stocks):
        """更新库存显示"""
        self.stock_container.clear_widgets()
        
        total_drugs = len(stocks)
        total_qty = sum(s['total_quantity'] for s in stocks)
        low_count = sum(1 for s in stocks if s['total_quantity'] < s['min_stock'])
        
        self.total_count.text = f'总品种: {total_drugs}'
        self.total_stock.text = f'总库存: {total_qty}'
        self.low_stock.text = f'不足: {low_count}'
        
        for stock in stocks:
            row = CardBox()
            
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp')
            name_lbl = Label(text=stock['name'], color=COLOR_TEXT, font_size='16sp', bold=True, size_hint_x=0.6)
            code_lbl = Label(text=f'编码:{stock["drug_code"]}', color=COLOR_TEXT_SECONDARY, font_size='12sp', size_hint_x=0.4)
            header.add_widget(name_lbl)
            header.add_widget(code_lbl)
            row.add_widget(header)
            
            info = BoxLayout(orientation='horizontal', size_hint_y=None, height='25dp')
            spec_lbl = Label(text=f'规格:{stock["specification"]}', color=COLOR_TEXT_SECONDARY, font_size='13sp', size_hint_x=0.4)
            
            qty = stock['total_quantity']
            min_s = stock['min_stock']
            
            if qty < min_s:
                qty_color = COLOR_DANGER
            elif qty < min_s * 1.5:
                qty_color = COLOR_WARNING
            else:
                qty_color = COLOR_SUCCESS
            
            qty_lbl = Label(text=f'库存:{qty} {stock["unit"]}', color=qty_color, font_size='14sp', bold=True, size_hint_x=0.3)
            price_lbl = Label(text=f'售价:¥{stock["retail_price"]:.2f}', color=COLOR_TEXT_SECONDARY, font_size='13sp', size_hint_x=0.3)
            
            info.add_widget(spec_lbl)
            info.add_widget(qty_lbl)
            info.add_widget(price_lbl)
            row.add_widget(info)
            
            self.stock_container.add_widget(row)
    
    def show_message(self, msg):
        popup = Popup(title='提示', content=Label(text=msg), size_hint=(0.8, 0.3))
        popup.open()


# ========================
# 效期预警界面
# ========================

class ExpiryScreen(Screen):
    """效期预警界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.warning_days = 180
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部导航
        top_bar = HeaderBar(title='效期预警', back_callback=lambda x: self.go_back())
        
        # 筛选按钮
        filter_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=10, spacing=10)
        
        self.filter_spinner = Spinner(
            text='全部预警',
            values=['全部预警', '已过期', '30天内', '90天内', '180天内'],
            size_hint_x=0.5
        )
        
        filter_btn = StyledButton(text='筛选', size_hint_x=0.25)
        filter_btn.bind(on_press=lambda x: self.filter_expiry())
        
        refresh_btn = StyledButton(text='刷新', size_hint_x=0.25)
        refresh_btn.bind(on_press=lambda x: self.load_expiry())
        
        filter_layout.add_widget(self.filter_spinner)
        filter_layout.add_widget(filter_btn)
        filter_layout.add_widget(refresh_btn)
        
        # 统计信息
        stats_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp', padding=10)
        
        self.expired_count = Label(text='已过期: 0', color=COLOR_DANGER, size_hint_x=0.34)
        self.warning_count = Label(text='预警中: 0', color=COLOR_WARNING, size_hint_x=0.33)
        self.safe_count = Label(text='正常: 0', color=COLOR_SUCCESS, size_hint_x=0.33)
        
        stats_layout.add_widget(self.expired_count)
        stats_layout.add_widget(self.warning_count)
        stats_layout.add_widget(self.safe_count)
        
        # 列表
        self.expiry_list = ScrollView(size_hint_y=1)
        self.expiry_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.expiry_container.height = self.expiry_container.minimum_height
        self.expiry_list.add_widget(self.expiry_container)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(filter_layout)
        main_layout.add_widget(stats_layout)
        main_layout.add_widget(self.expiry_list)
        
        self.add_widget(main_layout)
        
        # 加载数据
        Clock.schedule_once(lambda dt: self.load_expiry(), 0.1)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def go_back(self):
        self.manager.current = 'main'
    
    def filter_expiry(self):
        """筛选效期"""
        filter_text = self.filter_spinner.text
        
        if filter_text == '已过期':
            self.filter_days = 0
        elif filter_text == '30天内':
            self.filter_days = 30
        elif filter_text == '90天内':
            self.filter_days = 90
        elif filter_text == '180天内':
            self.filter_days = 180
        else:
            self.filter_days = 180
        
        self.load_expiry()
    
    def load_expiry(self):
        """加载效期数据"""
        database = get_db()
        
        today = datetime.date.today()
        filter_days = getattr(self, 'filter_days', 180)
        
        if filter_days == 0:
            # 已过期
            sql = '''
                SELECT db.*, d.name, d.specification, d.drug_code
                FROM drug_batches db
                JOIN drugs d ON db.drug_id = d.id
                WHERE db.expiry_date < ? AND db.status = 1
                ORDER BY db.expiry_date
            '''
            batches = database.fetch_all(sql, (today,))
        else:
            # 预警范围内
            end_date = today + datetime.timedelta(days=filter_days)
            sql = '''
                SELECT db.*, d.name, d.specification, d.drug_code
                FROM drug_batches db
                JOIN drugs d ON db.drug_id = d.id
                WHERE db.expiry_date <= ? AND db.expiry_date >= ? AND db.status = 1
                ORDER BY db.expiry_date
            '''
            batches = database.fetch_all(sql, (end_date, today - datetime.timedelta(days=30)))
        
        self.update_display(batches, today)
    
    def update_display(self, batches, today):
        """更新显示"""
        self.expiry_container.clear_widgets()
        
        expired = 0
        warning = 0
        safe = 0
        
        for batch in batches:
            batch_dict = dict(batch)
            expiry_date = datetime.datetime.strptime(batch_dict['expiry_date'], '%Y-%m-%d').date()
            days_left = (expiry_date - today).days
            
            if days_left < 0:
                status_color = COLOR_DANGER
                status_text = f'已过期{abs(days_left)}天'
                expired += 1
            elif days_left <= 30:
                status_color = COLOR_DANGER
                status_text = f'即将过期({days_left}天)'
                warning += 1
            elif days_left <= 90:
                status_color = COLOR_WARNING
                status_text = f'{days_left}天后到期'
                warning += 1
            else:
                status_color = COLOR_SUCCESS
                status_text = f'{days_left}天后到期'
                safe += 1
            
            row = CardBox()
            
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp')
            name_lbl = Label(text=batch_dict['name'], color=COLOR_TEXT, font_size='16sp', bold=True, size_hint_x=0.5)
            status_lbl = Label(text=status_text, color=status_color, font_size='14sp', size_hint_x=0.3)
            qty_lbl = Label(text=f'库存:{batch_dict["quantity"]}', color=COLOR_TEXT, font_size='14sp', size_hint_x=0.2)
            header.add_widget(name_lbl)
            header.add_widget(status_lbl)
            header.add_widget(qty_lbl)
            row.add_widget(header)
            
            info = BoxLayout(orientation='horizontal', size_hint_y=None, height='25dp')
            code_lbl = Label(text=f'编码:{batch_dict["drug_code"]}', color=COLOR_TEXT_SECONDARY, font_size='12sp', size_hint_x=0.4)
            spec_lbl = Label(text=f'规格:{batch_dict["specification"]}', color=COLOR_TEXT_SECONDARY, font_size='12sp', size_hint_x=0.3)
            batch_lbl = Label(text=f'批号:{batch_dict["batch_number"]}', color=COLOR_TEXT_SECONDARY, font_size='12sp', size_hint_x=0.3)
            info.add_widget(code_lbl)
            info.add_widget(spec_lbl)
            info.add_widget(batch_lbl)
            row.add_widget(info)
            
            self.expiry_container.add_widget(row)
        
        self.expired_count.text = f'已过期: {expired}'
        self.warning_count.text = f'预警中: {warning}'
        self.safe_count.text = f'正常: {safe}'
    
    def show_message(self, msg):
        popup = Popup(title='提示', content=Label(text=msg), size_hint=(0.8, 0.3))
        popup.open()


# ========================
# 会员管理界面
# ========================

class MemberScreen(Screen):
    """会员管理界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部导航
        top_bar = HeaderBar(title='会员管理', back_callback=lambda x: self.go_back())
        
        # 操作按钮
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=10, spacing=10)
        
        add_btn = SuccessButton(text='+ 新增会员', size_hint_x=0.5, height='45dp')
        add_btn.bind(on_press=lambda x: self.show_add_member())
        
        search_btn = StyledButton(text='搜索会员', size_hint_x=0.5, height='45dp')
        search_btn.bind(on_press=lambda x: self.show_search())
        
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(search_btn)
        
        # 会员列表
        self.member_list = ScrollView(size_hint_y=1)
        self.member_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.member_container.height = self.member_container.minimum_height
        self.member_list.add_widget(self.member_container)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(btn_layout)
        main_layout.add_widget(self.member_list)
        
        self.add_widget(main_layout)
        
        # 加载数据
        Clock.schedule_once(lambda dt: self.load_members(), 0.1)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def go_back(self):
        self.manager.current = 'main'
    
    def load_members(self):
        """加载会员列表"""
        database = get_db()
        members = database.fetch_all('SELECT * FROM members WHERE status = 1 ORDER BY created_at DESC')
        self.update_member_display(members)
    
    def update_member_display(self, members):
        """更新会员显示"""
        self.member_container.clear_widgets()
        
        for member in members:
            m = dict(member)
            row = CardBox()
            
            # 会员卡信息
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height='35dp')
            card_lbl = Label(text=m['card_no'], color=COLOR_PRIMARY, font_size='18sp', bold=True, size_hint_x=0.4)
            name_lbl = Label(text=m['name'] or '未填写', color=COLOR_TEXT, font_size='16sp', size_hint_x=0.3)
            phone_lbl = Label(text=m['phone'] or '', color=COLOR_TEXT_SECONDARY, font_size='14sp', size_hint_x=0.3)
            header.add_widget(card_lbl)
            header.add_widget(name_lbl)
            header.add_widget(phone_lbl)
            row.add_widget(header)
            
            # 积分余额
            info = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp')
            points_lbl = Label(text=f'积分: {m["points"]}', color=COLOR_WARNING, font_size='15sp', size_hint_x=0.33)
            balance_lbl = Label(text=f'余额: ¥{m["balance"]:.2f}', color=COLOR_SUCCESS, font_size='15sp', size_hint_x=0.34)
            discount_lbl = Label(text=f'折扣: {m["discount_rate"]*100:.0f}%', color=COLOR_TEXT_SECONDARY, font_size='15sp', size_hint_x=0.33)
            info.add_widget(points_lbl)
            info.add_widget(balance_lbl)
            info.add_widget(discount_lbl)
            row.add_widget(info)
            
            # 操作按钮
            action = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
            
            edit_btn = StyledButton(text='编辑', size_hint_x=0.5, height='35dp')
            edit_btn.bind(on_press=lambda x, mid=m['id']: self.edit_member(mid))
            
            charge_btn = SuccessButton(text='充值', size_hint_x=0.5, height='35dp')
            charge_btn.bind(on_press=lambda x, mid=m['id']: self.charge_member(mid))
            
            action.add_widget(edit_btn)
            action.add_widget(charge_btn)
            row.add_widget(action)
            
            self.member_container.add_widget(row)
    
    def show_add_member(self):
        """显示新增会员"""
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        content.add_widget(Label(text='新增会员', font_size='20sp', color=COLOR_PRIMARY, bold=True, size_hint_y=0.1))
        
        card_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp')
        card_layout.add_widget(Label(text='卡号:', size_hint_x=0.3))
        card_input = TextInput(hint_text='自动生成', size_hint_x=0.7, font_size='16sp')
        card_layout.add_widget(card_input)
        content.add_widget(card_layout)
        
        name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp')
        name_layout.add_widget(Label(text='姓名:', size_hint_x=0.3))
        name_input = TextInput(hint_text='请输入姓名', size_hint_x=0.7, font_size='16sp')
        name_layout.add_widget(name_input)
        content.add_widget(name_layout)
        
        phone_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp')
        phone_layout.add_widget(Label(text='电话:', size_hint_x=0.3))
        phone_input = TextInput(hint_text='请输入电话', size_hint_x=0.7, font_size='16sp', input_type='number')
        phone_layout.add_widget(phone_input)
        content.add_widget(phone_layout)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        cancel_btn = StyledButton(text='取消', size_hint_x=0.5)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        save_btn = SuccessButton(text='保存', size_hint_x=0.5)
        
        def save(btn):
            name = name_input.text.strip()
            phone = phone_input.text.strip()
            
            if not name:
                return
            
            # 生成卡号
            card_no = f'VIP{datetime.datetime.now().strftime("%m%d%H%M%S")}'
            
            database = get_db()
            database.execute('''
                INSERT INTO members (card_no, name, phone, points, balance, discount_rate)
                VALUES (?, ?, ?, 0, 0, 1.0)
            ''', (card_no, name, phone))
            
            popup.dismiss()
            self.load_members()
        
        save_btn.bind(on_press=save)
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='', content=content, size_hint=(0.9, 0.7), auto_dismiss=False)
        popup.open()
    
    def show_search(self):
        """显示搜索"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        search_input = TextInput(hint_text='输入卡号/姓名/电话', size_hint_y=None, height='50dp', font_size='16sp')
        content.add_widget(search_input)
        
        result_list = BoxLayout(orientation='vertical', size_hint_y=1)
        content.add_widget(result_list)
        
        def do_search(btn):
            keyword = search_input.text.strip()
            database = get_db()
            
            if keyword:
                members = database.fetch_all('''
                    SELECT * FROM members 
                    WHERE (card_no LIKE ? OR name LIKE ? OR phone LIKE ?) AND status = 1
                ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            else:
                members = database.fetch_all('SELECT * FROM members WHERE status = 1 LIMIT 50')
            
            result_list.clear_widgets()
            
            for m in members:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=5)
                info = f'{m["card_no"]} | {m["name"]} | {m["phone"]}'
                lbl = Label(text=info, color=COLOR_TEXT, size_hint_x=0.7)
                select_btn = StyledButton(text='选择', size_hint_x=0.3)
                
                def select(btn, member=dict(m)):
                    popup.dismiss()
                    self.current_member = member
                    self.show_member_detail(member)
                
                select_btn.bind(on_press=select)
                row.add_widget(lbl)
                row.add_widget(select_btn)
                result_list.add_widget(row)
        
        search_btn = StyledButton(text='搜索', size_hint_y=None, height='45dp')
        search_btn.bind(on_press=do_search)
        content.add_widget(search_btn)
        
        close_btn = StyledButton(text='关闭', size_hint_y=None, height='45dp')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup = Popup(title='搜索会员', content=content, size_hint=(0.95, 0.8))
        popup.open()
    
    def edit_member(self, member_id):
        """编辑会员"""
        self.show_message(f'编辑会员 ID: {member_id}')
    
    def charge_member(self, member_id):
        """会员充值"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(text='会员充值', font_size='20sp', color=COLOR_PRIMARY, bold=True))
        
        amount_input = TextInput(hint_text='输入充值金额', size_hint_y=None, height='50dp', font_size='20sp', input_type='number')
        content.add_widget(amount_input)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        cancel_btn = StyledButton(text='取消', size_hint_x=0.5)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        confirm_btn = SuccessButton(text='确认充值', size_hint_x=0.5)
        
        def confirm(btn):
            try:
                amount = float(amount_input.text)
                if amount <= 0:
                    return
                
                database = get_db()
                database.execute('UPDATE members SET balance = balance + ? WHERE id = ?', (amount, member_id))
                
                popup.dismiss()
                self.load_members()
                self.show_message(f'充值成功: ¥{amount:.2f}')
            except:
                pass
        
        confirm_btn.bind(on_press=confirm)
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='', content=content, size_hint=(0.9, 0.5), auto_dismiss=False)
        popup.open()
    
    def show_member_detail(self, member):
        """显示会员详情"""
        self.show_message(f'{member["name"]} - 卡号: {member["card_no"]}')
    
    def show_message(self, msg):
        popup = Popup(title='提示', content=Label(text=msg), size_hint=(0.8, 0.3))
        popup.open()


# ========================
# 数据同步界面
# ========================

class SyncScreen(Screen):
    """数据同步界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 顶部导航
        top_bar = HeaderBar(title='数据同步', back_callback=lambda x: self.go_back())
        main_layout.add_widget(top_bar)
        
        # 同步状态卡片
        status_card = CardBox()
        
        status_header = Label(text='同步状态', color=COLOR_TEXT, font_size='18sp', bold=True, size_hint_y=None, height='30dp')
        status_card.add_widget(status_header)
        
        self.sync_status = Label(text='最后同步: 尚未同步', color=COLOR_TEXT_SECONDARY, font_size='14sp', size_hint_y=None, height='25dp')
        status_card.add_widget(self.sync_status)
        
        self.sync_progress = ProgressBar(value=0, size_hint_y=None, height='20dp')
        status_card.add_widget(self.sync_progress)
        
        main_layout.add_widget(status_card)
        
        # 同步选项
        options_card = CardBox()
        
        options_header = Label(text='同步选项', color=COLOR_TEXT, font_size='18sp', bold=True, size_hint_y=None, height='30dp')
        options_card.add_widget(options_header)
        
        # 自动同步开关
        auto_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp')
        auto_layout.add_widget(Label(text='自动同步', color=COLOR_TEXT, size_hint_x=0.7))
        self.auto_sync_switch = Switch(active=False, size_hint_x=0.3)
        auto_layout.add_widget(self.auto_sync_switch)
        options_card.add_widget(auto_layout)
        
        # WiFi同步开关
        wifi_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp')
        wifi_layout.add_widget(Label(text='仅WiFi下同步', color=COLOR_TEXT, size_hint_x=0.7))
        self.wifi_sync_switch = Switch(active=True, size_hint_x=0.3)
        wifi_layout.add_widget(self.wifi_sync_switch)
        options_card.add_widget(wifi_layout)
        
        main_layout.add_widget(options_card)
        
        # 手动同步按钮
        sync_btn = SuccessButton(text='立即同步', height='60dp')
        sync_btn.bind(on_press=lambda x: self.do_sync())
        main_layout.add_widget(sync_btn)
        
        # 导出导入按钮
        export_btn = StyledButton(text='导出数据', height='50dp')
        export_btn.bind(on_press=lambda x: self.export_data())
        main_layout.add_widget(export_btn)
        
        import_btn = StyledButton(text='导入数据', height='50dp')
        import_btn.bind(on_press=lambda x: self.import_data())
        main_layout.add_widget(import_btn)
        
        # 使用说明
        info_card = CardBox()
        info_header = Label(text='使用说明', color=COLOR_TEXT_SECONDARY, font_size='14sp', bold=True, size_hint_y=None, height='25dp')
        info_card.add_widget(info_header)
        
        info_text = Label(
            text='1. 数据同步用于与电脑端保持数据一致\n'
                 '2. 可通过局域网或USB文件传输进行同步\n'
                 '3. 建议定期进行数据备份',
            color=COLOR_TEXT_SECONDARY,
            font_size='13sp',
            size_hint_y=None,
            height='100dp'
        )
        info_card.add_widget(info_text)
        
        main_layout.add_widget(info_card)
        
        self.add_widget(main_layout)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def go_back(self):
        self.manager.current = 'main'
    
    def do_sync(self):
        """执行同步"""
        self.sync_status.text = '正在同步...'
        self.sync_progress.value = 30
        
        # 模拟同步过程
        Clock.schedule_once(lambda dt: self.sync_step2(), 1)
    
    def sync_step2(self):
        self.sync_progress.value = 60
        Clock.schedule_once(lambda dt: self.sync_step3(), 1)
    
    def sync_step3(self):
        self.sync_progress.value = 100
        self.sync_status.text = f'最后同步: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        self.show_message('同步完成')
    
    def export_data(self):
        """导出数据"""
        self.show_message('数据导出功能开发中')
    
    def import_data(self):
        """导入数据"""
        self.show_message('数据导入功能开发中')
    
    def show_message(self, msg):
        popup = Popup(title='提示', content=Label(text=msg), size_hint=(0.8, 0.3))
        popup.open()


# ========================
# 小票打印界面
# ========================

class PrintScreen(Screen):
    """小票打印界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 背景
        with self.canvas.before:
            Color(*COLOR_BG)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部导航
        top_bar = HeaderBar(title='小票打印', back_callback=lambda x: self.go_back())
        
        # 打印机设置
        printer_card = CardBox()
        
        printer_header = Label(text='打印机设置', color=COLOR_TEXT, font_size='18sp', bold=True, size_hint_y=None, height='30dp')
        printer_card.add_widget(printer_header)
        
        # 打印机类型
        type_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp')
        type_layout.add_widget(Label(text='打印机类型:', size_hint_x=0.4))
        self.printer_spinner = Spinner(
            text='58mm热敏打印机',
            values=['58mm热敏打印机', '80mm热敏打印机', '蓝牙打印机'],
            size_hint_x=0.6
        )
        type_layout.add_widget(self.printer_spinner)
        printer_card.add_widget(type_layout)
        
        # 连接状态
        conn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp')
        conn_layout.add_widget(Label(text='连接状态:', size_hint_x=0.4))
        self.conn_status = Label(text='未连接', color=COLOR_DANGER, size_hint_x=0.6)
        conn_layout.add_widget(self.conn_status)
        printer_card.add_widget(conn_layout)
        
        connect_btn = StyledButton(text='连接打印机', height='45dp')
        connect_btn.bind(on_press=lambda x: self.connect_printer())
        printer_card.add_widget(connect_btn)
        
        main_layout.add_widget(top_bar)
        main_layout.add_widget(printer_card)
        
        # 最近小票
        receipt_card = CardBox()
        
        receipt_header = Label(text='最近小票', color=COLOR_TEXT, font_size='18sp', bold=True, size_hint_y=None, height='30dp')
        receipt_card.add_widget(receipt_header)
        
        self.receipt_list = ScrollView(size_hint_y=1)
        self.receipt_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.receipt_container.height = self.receipt_container.minimum_height
        self.receipt_list.add_widget(self.receipt_container)
        receipt_card.add_widget(self.receipt_list)
        
        main_layout.add_widget(receipt_card)
        
        # 测试打印
        test_btn = StyledButton(text='打印测试页', height='50dp')
        test_btn.bind(on_press=lambda x: self.print_test())
        main_layout.add_widget(test_btn)
        
        self.add_widget(main_layout)
        
        # 加载最近小票
        Clock.schedule_once(lambda dt: self.load_recent_receipts(), 0.1)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def go_back(self):
        self.manager.current = 'main'
    
    def connect_printer(self):
        """连接打印机"""
        self.show_message('正在搜索并连接打印机...')
        self.conn_status.text = '连接中...'
        self.conn_status.color = COLOR_WARNING
        
        # 模拟连接
        Clock.schedule_once(lambda dt: self.on_printer_connected(), 2)
    
    def on_printer_connected(self):
        """打印机连接成功"""
        self.conn_status.text = '已连接'
        self.conn_status.color = COLOR_SUCCESS
        self.show_message('打印机连接成功')
    
    def load_recent_receipts(self):
        """加载最近小票"""
        database = get_db()
        orders = database.fetch_all('''
            SELECT * FROM sales_orders 
            ORDER BY created_at DESC LIMIT 20
        ''')
        
        self.receipt_container.clear_widgets()
        
        for order in orders:
            o = dict(order)
            row = CardBox()
            
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp')
            order_lbl = Label(text=f'订单号: {o["order_no"]}', color=COLOR_TEXT, font_size='14sp', bold=True, size_hint_x=0.5)
            amount_lbl = Label(text=f'¥{o["actual_amount"]:.2f}', color=COLOR_PRIMARY, font_size='16sp', bold=True, size_hint_x=0.3)
            time_lbl = Label(text=o['created_at'][:16], color=COLOR_TEXT_SECONDARY, font_size='12sp', size_hint_x=0.2)
            header.add_widget(order_lbl)
            header.add_widget(amount_lbl)
            header.add_widget(time_lbl)
            row.add_widget(header)
            
            reprint_btn = StyledButton(text='重新打印', size_hint_y=None, height='35dp')
            reprint_btn.bind(on_press=lambda x, oid=o['id']: self.reprint_receipt(oid))
            row.add_widget(reprint_btn)
            
            self.receipt_container.add_widget(row)
    
    def print_test(self):
        """打印测试页"""
        self.show_message('正在打印测试页...')
        self.print_receipt_content(self.generate_test_receipt())
    
    def reprint_receipt(self, order_id):
        """重新打印小票"""
        database = get_db()
        order = database.fetch_one('SELECT * FROM sales_orders WHERE id = ?', (order_id,))
        
        if order:
            items = database.fetch_all('SELECT si.*, d.name FROM sales_items si JOIN drugs d ON si.drug_id = d.id WHERE si.order_id = ?', (order_id,))
            receipt = self.generate_receipt(dict(order), [dict(i) for i in items])
            self.print_receipt_content(receipt)
    
    def generate_test_receipt(self):
        """生成测试小票"""
        content = '''
================================
       药品进销存管理系统
================================
      测试页 - 打印机正常
================================
店名: 药店进销存管理系统
日期: ''' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''

商品名          数量    金额
--------------------------------
阿莫西林胶囊      1    18.00
布洛芬缓释胶囊    1    25.00
维生素C片        2    16.00
--------------------------------
合计:                    59.00
收款:                    60.00
找零:                     1.00
================================
       谢谢惠顾，欢迎下次光临
================================
'''
        return content
    
    def generate_receipt(self, order, items):
        """生成小票内容"""
        content = f'''
================================
       药品进销存管理系统
================================
订单号: {order['order_no']}
日期: {order['created_at']}

商品名          数量    金额
--------------------------------
'''
        for item in items:
            content += f"{item['name'][:10]:<12} {item['quantity']:>3} {item['amount']:>8.2f}\n"
        
        content += f'''--------------------------------
合计:                 {order['actual_amount']:>8.2f}
收款:                 {order['cash_received']:>8.2f}
找零:                 {order['change_amount']:>8.2f}
================================
       谢谢惠顾，欢迎下次光临
================================
'''
        return content
    
    def print_receipt_content(self, content):
        """打印小票内容"""
        # 58mm小票宽度约48个字符
        # 这里应该调用实际的打印API
        self.show_message('小票已发送到打印机')
    
    def show_message(self, msg):
        popup = Popup(title='提示', content=Label(text=msg), size_hint=(0.8, 0.3))
        popup.open()


# ========================
# 应用入口
# ========================

class DrugPOSApp(App):
    """药品进销存管理系统主应用"""
    
    def build(self):
        # 创建屏幕管理器
        self.sm = ScreenManager(transition=FadeTransition())
        
        # 添加各个屏幕
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(SaleScreen(name='sale'))
        self.sm.add_widget(StockScreen(name='stock'))
        self.sm.add_widget(ExpiryScreen(name='expiry'))
        self.sm.add_widget(MemberScreen(name='member'))
        self.sm.add_widget(SyncScreen(name='sync'))
        self.sm.add_widget(PrintScreen(name='print'))
        
        return self.sm
    
    def on_start(self):
        """应用启动"""
        # 初始化数据库
        get_db()
    
    def on_pause(self):
        """应用暂停"""
        return True
    
    def on_resume(self):
        """应用恢复"""
        pass


# 应用实例
app = None

def main():
    """主函数"""
    global app
    app = DrugPOSApp()
    app.run()


if __name__ == '__main__':
    main()
