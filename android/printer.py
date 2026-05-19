# -*- coding: utf-8 -*-
"""
58mm小票打印机驱动模块
支持ESC/POS指令集的打印机
"""

import time


class ReceiptPrinter:
    """小票打印机类 - 支持58mm热敏打印机"""
    
    # ESC/POS指令常量
    ESC = b'\x1b'
    GS = b'\x1d'
    LF = b'\x0a'
    
    # 对齐方式
    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2
    
    # 字体大小
    FONT_NORMAL = 0
    FONT_LARGE = 1
    
    def __init__(self, port='/dev/usb/lp0'):
        """初始化打印机
        
        Args:
            port: 打印机端口，默认为USB打印机
        """
        self.port = port
        self.output = bytearray()
    
    def reset(self):
        """重置打印机"""
        self.output.extend(self.ESC + b'@')
        return self
    
    def line_feed(self, lines=1):
        """换行
        
        Args:
            lines: 换行行数
        """
        for _ in range(lines):
            self.output.extend(self.LF)
        return self
    
    def align(self, align):
        """设置对齐方式
        
        Args:
            align: 对齐方式 (ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT)
        """
        self.output.extend(self.ESC + b'a' + bytes([align]))
        return self
    
    def font_size(self, size):
        """设置字体大小
        
        Args:
            size: 字体大小 (FONT_NORMAL, FONT_LARGE)
        """
        self.output.extend(self.GS + b'!' + bytes([size]))
        return self
    
    def bold(self, enable=True):
        """设置粗体
        
        Args:
            enable: 是否启用粗体
        """
        if enable:
            self.output.extend(self.ESC + b'E' + b'\x01')
        else:
            self.output.extend(self.ESC + b'E' + b'\x00')
        return self
    
    def text(self, text):
        """添加文本
        
        Args:
            text: 要添加的文本
        """
        if isinstance(text, str):
            self.output.extend(text.encode('gbk'))
        else:
            self.output.extend(text)
        return self
    
    def text_line(self, text):
        """添加文本并换行
        
        Args:
            text: 要添加的文本
        """
        self.text(text)
        self.line_feed()
        return self
    
    def cut(self):
        """切纸"""
        self.output.extend(self.GS + b'V' + b'\x41')
        return self
    
    def open_cash_drawer(self):
        """打开钱箱"""
        self.output.extend(self.ESC + b'p' + b'\x00' + b'\x19' + b'\xFA')
        return self
    
    def print_receipt(self, receipt_data):
        """打印小票
        
        Args:
            receipt_data: 小票数据字典
        """
        self.reset()
        
        # 店名标题
        self.align(self.ALIGN_CENTER)
        self.font_size(self.FONT_LARGE)
        self.bold(True)
        self.text_line('药品进销存管理系统')
        self.font_size(self.FONT_NORMAL)
        self.bold(False)
        self.line_feed()
        
        # 分隔线
        self.align(self.ALIGN_CENTER)
        self.text_line('================================')
        
        # 订单信息
        self.align(self.ALIGN_LEFT)
        self.text_line(f"订单号: {receipt_data.get('order_no', '')}")
        self.text_line(f"日  期: {receipt_data.get('date', '')}")
        self.text_line(f"收银员: {receipt_data.get('cashier', '')}")
        
        # 会员信息
        if receipt_data.get('member'):
            self.text_line(f"会  员: {receipt_data['member']}")
        
        self.line_feed()
        
        # 商品明细
        self.align(self.ALIGN_CENTER)
        self.text_line('--------------------------------')
        
        self.align(self.ALIGN_LEFT)
        header = f"{'商品名称':<10} {'数量':>3} {'单价':>8} {'金额':>8}"
        self.text_line(header)
        self.text_line('--------------------------------')
        
        for item in receipt_data.get('items', []):
            name = item.get('name', '')[:10]
            qty = item.get('quantity', 0)
            price = item.get('price', 0)
            amount = item.get('amount', 0)
            
            line = f"{name:<10} {qty:>3} {price:>8.2f} {amount:>8.2f}"
            self.text_line(line)
        
        self.text_line('--------------------------------')
        
        # 金额汇总
        self.align(self.ALIGN_RIGHT)
        self.text_line(f"合计:              {receipt_data.get('total', 0):>8.2f}")
        self.text_line(f"优惠:              {receipt_data.get('discount', 0):>8.2f}")
        self.bold(True)
        self.font_size(self.FONT_LARGE)
        self.text_line(f"实收:              {receipt_data.get('actual', 0):>8.2f}")
        self.font_size(self.FONT_NORMAL)
        self.bold(False)
        
        self.text_line('')
        self.text_line(f"收款:              {receipt_data.get('cash', 0):>8.2f}")
        self.text_line(f"找零:              {receipt_data.get('change', 0):>8.2f}")
        
        # 底部信息
        self.line_feed()
        self.align(self.ALIGN_CENTER)
        self.text_line('================================')
        self.text_line('谢谢惠顾，欢迎下次光临')
        self.line_feed()
        
        # 切纸
        self.cut()
        
        return bytes(self.output)
    
    def print_test_page(self):
        """打印测试页"""
        self.reset()
        
        self.align(self.ALIGN_CENTER)
        self.font_size(self.FONT_LARGE)
        self.bold(True)
        self.text_line('打印机测试')
        self.line_feed()
        
        self.font_size(self.FONT_NORMAL)
        self.bold(False)
        self.align(self.ALIGN_LEFT)
        self.text_line('1234567890')
        self.text_line('abcdefghij')
        self.text_line('中文测试')
        
        self.line_feed()
        self.align(self.ALIGN_CENTER)
        self.text_line('测试完成')
        
        self.cut()
        
        return bytes(self.output)
    
    def send_to_printer(self):
        """发送到打印机"""
        # 在Android上，这里应该使用Android Bluetooth API或USB API发送数据
        # 暂时返回字节数据供后续处理
        return bytes(self.output)


class BluetoothPrinter(ReceiptPrinter):
    """蓝牙打印机类"""
    
    def __init__(self, bluetooth_address=None):
        super().__init__()
        self.bluetooth_address = bluetooth_address
        self.socket = None
    
    def connect(self):
        """连接蓝牙打印机"""
        try:
            import android.bluetooth as bluetooth
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.connect((self.bluetooth_address, 1))
            return True
        except Exception as e:
            print(f"蓝牙连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开蓝牙连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def send(self):
        """通过蓝牙发送数据"""
        if self.socket:
            self.socket.send(bytes(self.output))
        return bytes(self.output)


# 58mm小票格式常量
class ReceiptFormat:
    """小票格式定义"""
    
    # 58mm小票宽度约48个字符
    WIDTH = 48
    
    @staticmethod
    def format_line(left, right='', width=None):
        """格式化一行
        
        Args:
            left: 左侧文本
            right: 右侧文本
            width: 行宽度，默认48
        """
        if width is None:
            width = ReceiptFormat.WIDTH
        
        left_str = str(left)
        right_str = str(right)
        
        # 计算中间空格
        space = width - len(left_str) - len(right_str)
        if space < 1:
            space = 1
        
        return left_str + ' ' * space + right_str
    
    @staticmethod
    def format_header(title):
        """格式化标题"""
        width = ReceiptFormat.WIDTH
        space = (width - len(title)) // 2
        return ' ' * space + title
    
    @staticmethod
    def separator(char='-', width=None):
        """生成分隔线"""
        if width is None:
            width = ReceiptFormat.WIDTH
        return char * width


def create_receipt(order_data):
    """创建小票数据
    
    Args:
        order_data: 订单数据字典
    
    Returns:
        bytes: 小票字节数据
    """
    printer = ReceiptPrinter()
    return printer.print_receipt(order_data)


def print_sale_receipt(order, items, member=None, cashier='系统'):
    """打印销售小票
    
    Args:
        order: 订单信息
        items: 商品明细
        member: 会员信息
        cashier: 收银员
    
    Returns:
        bytes: 小票数据
    """
    import datetime
    
    receipt_data = {
        'order_no': order.get('order_no', ''),
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cashier': cashier,
        'member': member.get('name') if member else None,
        'items': items,
        'total': order.get('total_amount', 0),
        'discount': order.get('discount_amount', 0),
        'actual': order.get('actual_amount', 0),
        'cash': order.get('cash_received', 0),
        'change': order.get('change_amount', 0),
    }
    
    return create_receipt(receipt_data)


# 测试代码
if __name__ == '__main__':
    # 测试数据
    test_receipt = {
        'order_no': 'XD20240101123456',
        'date': '2024-01-01 12:34:56',
        'cashier': '张三',
        'member': '李四',
        'items': [
            {'name': '阿莫西林胶囊', 'quantity': 1, 'price': 18.00, 'amount': 18.00},
            {'name': '布洛芬缓释胶囊', 'quantity': 2, 'price': 25.00, 'amount': 50.00},
            {'name': '维生素C片', 'quantity': 1, 'price': 8.00, 'amount': 8.00},
        ],
        'total': 76.00,
        'discount': 3.80,
        'actual': 72.20,
        'cash': 80.00,
        'change': 7.80,
    }
    
    printer = ReceiptPrinter()
    data = printer.print_receipt(test_receipt)
    
    print("小票数据长度:", len(data))
    print("小票内容预览:")
    print(data.decode('gbk', errors='ignore'))
