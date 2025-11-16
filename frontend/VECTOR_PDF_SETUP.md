# 矢量PDF导出功能设置指南

## 安装依赖

为了实现矢量PDF导出功能，需要安装 `svg2pdf.js` 库：

```bash
cd frontend
npm install svg2pdf.js
```

或使用 yarn:

```bash
cd frontend
yarn add svg2pdf.js
```

## 功能说明

### 矢量PDF导出
- **完全矢量化**：导出的PDF保持图表的矢量特性，可以无损缩放
- **高质量**：适合学术出版、印刷和专业排版
- **文件小**：相比栅格PDF，文件更小

### 栅格PDF导出（后备方案）
- 如果矢量导出失败，自动降级到高质量栅格PDF（300 DPI）
- 适合快速预览和一般用途

## 使用方法

### 在图表组件中
导出功能会自动尝试使用矢量格式：

1. **散点图/折线图页面**：点击导出 → 选择 PDF
2. **自动处理**：系统会先尝试矢量导出，失败则使用栅格导出

### 导出选项

```javascript
// 矢量PDF（默认）
await exportChartAsPDF(chartInstance, {
  filename: 'my-chart',
  vectorize: true,  // 使用矢量格式
  orientation: 'landscape',  // 横向
  format: 'a4'  // A4纸张
})

// 栅格PDF
await exportChartAsPDF(chartInstance, {
  filename: 'my-chart',
  vectorize: false,  // 使用栅格格式
  dpi: 300  // 分辨率
})
```

## 技术细节

### 矢量PDF优势
- ✅ 文字清晰，可复制粘贴
- ✅ 图形线条平滑
- ✅ 缩放不失真
- ✅ 文件体积小
- ✅ 适合印刷和出版

### 适用场景
- 学术论文配图
- 期刊投稿
- 书籍出版
- 高质量演示文稿
- 专业报告

## 故障排除

### 如果矢量导出失败
1. 检查图表是否使用 SVG 渲染器初始化
2. 查看浏览器控制台错误信息
3. 系统会自动降级到栅格PDF

### 兼容性
- 支持所有现代浏览器（Chrome、Firefox、Edge、Safari）
- 需要 svg2pdf.js 库支持

## 期刊投稿指南

不同期刊对图表格式的要求：

| 期刊类型 | 推荐格式 | 导出方式 |
|---------|---------|---------|
| Nature/Science | TIFF 300 DPI | 导出 → TIFF |
| IEEE | EPS/PDF 矢量 | 导出 → PDF（矢量） |
| PLOS | PDF 300-600 DPI | 导出 → PDF |
| ACS | EPS 矢量 | 导出 → SVG（可转EPS） |
| 在线期刊 | SVG/PDF 矢量 | 导出 → SVG 或 PDF |

## 更新日志

### v1.0.0 (2025-11-16)
- ✨ 新增矢量PDF导出功能
- ✨ 支持自动降级到栅格PDF
- ✨ 优化SVG到PDF转换流程
- 📦 新增 svg2pdf.js 依赖
