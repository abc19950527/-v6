// 小票打印工具 - 支持58mm/80mm热敏打印机
// 使用ESC/POS指令

export default {
  // 打印销售小票
  printSalesTicket(order, items, member) {
    const content = this.generateReceipt(order, items, member)
    this.sendToPrinter(content)
    return content
  },

  // 生成小票内容
  generateReceipt(order, items, member) {
    const shopName = localStorage.getItem('shop_name') || '药品进销存管理系统'
    const shopTel = localStorage.getItem('shop_tel') || '联系电话: 400-xxx-xxxx'
    const shopAddr = localStorage.getItem('shop_addr') || ''
    const printWidth = 32 // 58mm纸宽约32字符

    let content = ''
    
    // 分隔线
    content += this.center(shopName, printWidth) + '\n'
    content += this.center(shopTel, printWidth) + '\n'
    if (shopAddr) content += this.center(shopAddr, printWidth) + '\n'
    content += '-'.repeat(printWidth) + '\n'
    
    // 单号和时间
    content += `单号: ${order.order_no || 'N/A'}\n`
    content += `时间: ${order.create_time || new Date().toLocaleString()}\n`
    if (member) content += `会员: ${member.member_name || ''} (${member.card_no || ''})\n`
    content += '-'.repeat(printWidth) + '\n'
    
    // 商品明细
    content += '名称          数量  单价  小计\n'
    content += '-'.repeat(printWidth) + '\n'
    
    items.forEach(item => {
      const name = item.drug_name?.substring(0, 8) || ''
      const qty = String(item.quantity || 0).padStart(3)
      const price = (item.price || 0).toFixed(2)
      const amount = ((item.quantity || 0) * (item.price || 0)).toFixed(2)
      content += `${name}\n`
      content += `             ${qty}  ${price}  ${amount}\n`
    })
    
    content += '-'.repeat(printWidth) + '\n'
    
    // 金额汇总
    const total = order.total_amount || 0
    const discount = order.discount_amount || 0
    const actual = order.actual_amount || 0
    
    content += `${this.alignLeft('商品金额:', printWidth - 10)}${this.alignRight(total.toFixed(2), 10)}\n`
    if (discount > 0) {
      content += `${this.alignLeft('优惠金额:', printWidth - 10)}${this.alignRight('-' + discount.toFixed(2), 10)}\n`
    }
    content += `${this.alignLeft('实收金额:', printWidth - 10)}${this.alignRight(actual.toFixed(2), 10)}\n`
    
    const paymentText = this.getPayMethodText(order.payment_method)
    content += `支付方式: ${paymentText}\n`
    
    if (order.cash_received && order.cash_received > actual) {
      const change = order.change_amount || (order.cash_received - actual)
      content += `收款: ${order.cash_received.toFixed(2)} 找零: ${change.toFixed(2)}\n`
    }
    
    content += '-'.repeat(printWidth) + '\n'
    content += this.center('谢谢惠顾，欢迎下次光临', printWidth) + '\n'
    content += this.center(new Date().toLocaleDateString(), printWidth) + '\n'
    content += '\n\n\n' // 切纸留白
    
    return content
  },

  // 发送打印内容到打印机
  sendToPrinter(content) {
    // 通过Electron IPC发送到主进程
    if (window.electronAPI?.print) {
      window.electronAPI.print(content)
    } else {
      console.log('打印内容:', content)
      // 浏览器环境下打开打印预览
      const printWindow = window.open('', '', 'width=300,height=600')
      printWindow.document.write(`<pre style="font-family: monospace; font-size: 12px;">${content}</pre>`)
      printWindow.document.close()
      printWindow.print()
    }
  },

  // 居中对齐
  center(text, width) {
    const len = this.getStrLen(text)
    const padding = Math.floor((width - len) / 2)
    return ' '.repeat(Math.max(0, padding)) + text
  },

  // 左对齐
  alignLeft(text, width) {
    const len = this.getStrLen(text)
    return text + ' '.repeat(Math.max(0, width - len))
  },

  // 右对齐
  alignRight(text, width) {
    const len = this.getStrLen(String(text))
    return ' '.repeat(Math.max(0, width - len)) + text
  },

  // 获取字符串实际长度(中文算2)
  getStrLen(str) {
    let len = 0
    for (const char of str) {
      len += char.charCodeAt(0) > 255 ? 2 : 1
    }
    return len
  },

  // 支付方式文字
  getPayMethodText(method) {
    const map = {
      cash: '现金',
      wechat: '微信支付',
      alipay: '支付宝',
      card: '银行卡',
      member: '会员卡'
    }
    return map[method] || method || '现金'
  }
}
