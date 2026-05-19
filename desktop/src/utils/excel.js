// Excel 导出工具
import * as XLSX from 'xlsx'

export default {
  // 导出药品档案
  exportDrugs(data) {
    const ws = XLSX.utils.json_to_sheet(data.map(item => ({
      '药品编码': item.drug_code,
      '药品名称': item.drug_name,
      '规格': item.spec,
      '单位': item.unit,
      '分类': item.category,
      '生产厂家': item.manufacturer,
      '批准文号': item.approval_number,
      '零售价': item.price,
      '成本价': item.cost_price,
      '最低库存': item.min_stock,
      '处方类型': item.prescription_type === 'OTC' ? '非处方药' : '处方药',
      '状态': item.status === '1' ? '启用' : '禁用'
    })))
    
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '药品档案')
    XLSX.writeFile(wb, `药品档案_${new Date().toISOString().slice(0,10)}.xlsx`)
  },

  // 导出销售单据
  exportSalesOrders(data) {
    const ws = XLSX.utils.json_to_sheet(data.map(item => ({
      '单号': item.order_no,
      '会员': item.member_name || '散客',
      '商品金额': item.total_amount,
      '优惠金额': item.discount_amount,
      '实收金额': item.actual_amount,
      '支付方式': this.payMethodText(item.payment_method),
      '时间': item.create_time
    })))
    
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '销售记录')
    XLSX.writeFile(wb, `销售记录_${new Date().toISOString().slice(0,10)}.xlsx`)
  },

  // 导出入库单据
  exportPurchaseOrders(data) {
    const ws = XLSX.utils.json_to_sheet(data.map(item => ({
      '单号': item.order_no,
      '供应商': item.supplier_name,
      '总金额': item.total_amount,
      '操作员': item.staff_name,
      '时间': item.create_time,
      '状态': item.status === '1' ? '已完成' : '已取消'
    })))
    
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '入库记录')
    XLSX.writeFile(wb, `入库记录_${new Date().toISOString().slice(0,10)}.xlsx`)
  },

  // 导出库存报表
  exportInventory(data) {
    const ws = XLSX.utils.json_to_sheet(data.map(item => ({
      '药品编码': item.drug_code,
      '药品名称': item.drug_name,
      '规格': item.spec,
      '批次号': item.batch_number,
      '库存数量': item.quantity,
      '有效期': item.expiry_date,
      '进货价': item.cost_price,
      '库存价值': item.quantity * item.cost_price
    })))
    
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '库存明细')
    XLSX.writeFile(wb, `库存报表_${new Date().toISOString().slice(0,10)}.xlsx`)
  },

  // 导出销售统计报表
  exportSalesReport(stats) {
    const ws = XLSX.utils.json_to_sheet([{
      '统计项目': '销售订单数',
      '数值': stats.total_orders || 0
    }, {
      '统计项目': '总销售额',
      '数值': stats.total_sales || 0
    }, {
      '统计项目': '实收金额',
      '数值': stats.total_actual || 0
    }, {
      '统计项目': '优惠金额',
      '数值': (stats.total_sales || 0) - (stats.total_actual || 0)
    }, {
      '统计项目': '平均客单价',
      '数值': stats.avg_order || 0
    }])
    
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '销售统计')
    XLSX.writeFile(wb, `销售统计报表_${new Date().toISOString().slice(0,10)}.xlsx`)
  },

  payMethodText(method) {
    const map = { cash: '现金', wechat: '微信', alipay: '支付宝', card: '银行卡', member: '会员卡' }
    return map[method] || method
  }
}
