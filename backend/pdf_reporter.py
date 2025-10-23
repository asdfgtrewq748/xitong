# backend/pdf_reporter.py
"""
PDF报告生成模块
生成包含统计数据、图表和分析结论的专业报告
"""

import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd


class PDFReporter:
    """PDF报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        self.has_reportlab = self._check_reportlab()

    def _check_reportlab(self) -> bool:
        """检查ReportLab是否已安装"""
        try:
            import reportlab
            return True
        except ImportError:
            return False

    def generate_report(self,
                       title: str,
                       data: Dict[str, Any],
                       charts: Optional[List[Dict]] = None,
                       conclusion: Optional[str] = None) -> bytes:
        """
        生成PDF报告

        Args:
            title: 报告标题
            data: 数据字典 (包含统计信息、表格等)
            charts: 图表列表 (base64编码的图片)
            conclusion: 分析结论

        Returns:
            PDF文件的字节流
        """
        if not self.has_reportlab:
            # 如果没有安装reportlab,生成HTML报告并提示
            return self._generate_html_report(title, data, charts, conclusion)

        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # 创建PDF缓冲区
        buffer = io.BytesIO()

        # 创建PDF文档
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)

        # 容器存放内容
        story = []

        # 样式
        styles = getSampleStyleSheet()

        # 尝试添加中文字体支持
        try:
            # 注意: 需要系统中有中文字体
            pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName='SimSun',
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=1  # 居中
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName='SimSun',
                fontSize=16,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=12
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName='SimSun',
                fontSize=10
            )
        except:
            # 使用默认字体
            title_style = styles['Heading1']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']

        # 1. 封面
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Paragraph("煤层地质建模系统", normal_style))
        story.append(PageBreak())

        # 2. 统计数据
        if data.get('statistics'):
            story.append(Paragraph("一、数据统计", heading_style))
            story.append(Spacer(1, 12))

            stats = data['statistics']
            stats_data = [
                ['统计项', '数值'],
                ['总记录数', str(stats.get('total_records', 'N/A'))],
                ['钻孔数量', str(stats.get('total_boreholes', 'N/A'))],
                ['省份数量', str(stats.get('total_provinces', 'N/A'))],
                ['岩性类型', str(stats.get('lithology_types', 'N/A'))]
            ]

            table = Table(stats_data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)
            story.append(Spacer(1, 20))

        # 3. 详细数据表
        if data.get('table_data'):
            story.append(Paragraph("二、详细数据", heading_style))
            story.append(Spacer(1, 12))

            df = data['table_data']
            if isinstance(df, pd.DataFrame):
                # 限制显示前20行
                df_display = df.head(20)

                # 转换为列表
                table_data = [df_display.columns.tolist()] + df_display.values.tolist()

                # 创建表格
                col_count = len(df_display.columns)
                col_width = 6*inch / col_count

                table = Table(table_data, colWidths=[col_width] * col_count)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(table)

                if len(df) > 20:
                    story.append(Spacer(1, 12))
                    story.append(Paragraph(f"(仅显示前20行,共{len(df)}行)", normal_style))

            story.append(Spacer(1, 20))

        # 4. 图表
        if charts:
            story.append(PageBreak())
            story.append(Paragraph("三、数据可视化", heading_style))
            story.append(Spacer(1, 12))

            for i, chart in enumerate(charts):
                if chart.get('base64_image'):
                    try:
                        # 解码base64图片
                        image_data = base64.b64decode(chart['base64_image'].split(',')[1])
                        img = Image(io.BytesIO(image_data), width=5*inch, height=3*inch)

                        if chart.get('title'):
                            story.append(Paragraph(f"{i+1}. {chart['title']}", normal_style))
                            story.append(Spacer(1, 6))

                        story.append(img)
                        story.append(Spacer(1, 20))
                    except Exception as e:
                        print(f"图表 {i+1} 添加失败: {e}")

        # 5. 分析结论
        if conclusion:
            story.append(PageBreak())
            story.append(Paragraph("四、分析结论", heading_style))
            story.append(Spacer(1, 12))
            story.append(Paragraph(conclusion, normal_style))

        # 6. 页脚
        story.append(Spacer(1, 50))
        story.append(Paragraph("---", normal_style))
        story.append(Paragraph("本报告由煤层地质建模系统自动生成", normal_style))

        # 构建PDF
        doc.build(story)

        # 获取PDF内容
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _generate_html_report(self, title: str, data: Dict[str, Any],
                             charts: Optional[List[Dict]] = None,
                             conclusion: Optional[str] = None) -> bytes:
        """生成HTML报告(当ReportLab不可用时)"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .chart {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart img {{
            max-width: 100%;
            border: 1px solid #ddd;
            padding: 10px;
        }}
        .footer {{
            margin-top: 50px;
            text-align: center;
            color: #7f8c8d;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p style="text-align: center; color: #7f8c8d;">
            生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>

        <div class="warning">
            ⚠️ <strong>提示:</strong> 系统未安装ReportLab库,已生成HTML格式报告。
            <br>如需PDF格式,请安装: <code>pip install reportlab</code>
        </div>
"""

        # 统计数据
        if data.get('statistics'):
            html_content += "<h2>一、数据统计</h2><table>"
            html_content += "<tr><th>统计项</th><th>数值</th></tr>"

            stats = data['statistics']
            for key, value in stats.items():
                html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"

            html_content += "</table>"

        # 图表
        if charts:
            html_content += "<h2>二、数据可视化</h2>"
            for i, chart in enumerate(charts):
                if chart.get('base64_image'):
                    html_content += f"<div class='chart'>"
                    if chart.get('title'):
                        html_content += f"<h3>{i+1}. {chart['title']}</h3>"
                    html_content += f"<img src='{chart['base64_image']}' alt='图表{i+1}'>"
                    html_content += "</div>"

        # 结论
        if conclusion:
            html_content += f"<h2>三、分析结论</h2><p>{conclusion}</p>"

        html_content += """
        <div class="footer">
            <p>本报告由煤层地质建模系统自动生成</p>
        </div>
    </div>
</body>
</html>
"""

        return html_content.encode('utf-8')


def create_simple_report(title: str, statistics: Dict, table_data: pd.DataFrame = None) -> bytes:
    """创建简单报告的便捷函数"""
    reporter = PDFReporter()
    return reporter.generate_report(
        title=title,
        data={
            'statistics': statistics,
            'table_data': table_data
        }
    )
