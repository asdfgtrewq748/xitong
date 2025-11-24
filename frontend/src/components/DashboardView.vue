<template>
  <div class="dashboard-container">
    <!-- 欢迎横幅 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="welcome-card">
          <div class="welcome-content">
            <div class="welcome-text">
              <h1>🏔️ 矿山工程分析系统</h1>
              <p>专业的煤矿地质数据分析与三维建模平台</p>
              <div class="feature-tags">
                <el-tag type="success" effect="plain">关键层计算</el-tag>
                <el-tag type="primary" effect="plain">三维地质建模</el-tag>
                <el-tag type="warning" effect="plain">钻孔数据分析</el-tag>
                <el-tag type="info" effect="plain">岩性参数查询</el-tag>
              </div>
            </div>
            <div class="welcome-action">
              <el-button type="primary" size="large" @click="showQuickStart = true">
                <el-icon style="margin-right: 8px;"><Guide /></el-icon>
                快速开始教程
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"><el-icon><Coin /></el-icon></div>
            <div class="stat-text">
              <div class="stat-title">岩石数据库</div>
              <div class="stat-value">{{ stats.rock_db_count }}</div>
              <div class="stat-label">条记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);"><el-icon><Files /></el-icon></div>
            <div class="stat-text">
              <div class="stat-title">钻孔文件</div>
              <div class="stat-value">{{ stats.borehole_file_count }}</div>
              <div class="stat-label">个文件</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);"><el-icon><Picture /></el-icon></div>
            <div class="stat-text">
              <div class="stat-title">建模数据</div>
              <div class="stat-value">{{ stats.modeling_record_count }}</div>
              <div class="stat-label">条记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);"><el-icon><DataAnalysis /></el-icon></div>
            <div class="stat-text">
              <div class="stat-title">全局钻孔</div>
              <div class="stat-value">{{ uniqueBoreholes }}</div>
              <div class="stat-label">个钻孔</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能模块卡片 -->
    <el-row :gutter="20" class="feature-row">
      <el-col :span="6">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/key-stratum')">
          <div class="feature-icon" style="background-color: #409EFF;">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <h3>关键层计算</h3>
          <p>基于岩层力学参数,自动计算并标识煤层上覆关键层位置,评估顶板稳定性</p>
          <div class="feature-footer">
            <el-button type="primary" link>立即使用 →</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/geological-modeling')">
          <div class="feature-icon" style="background-color: #67C23A;">
            <el-icon><Picture /></el-icon>
          </div>
          <h3>三维地质建模</h3>
          <p>基于钻孔数据,生成煤层三维块体模型,支持多种插值方法和可视化分析</p>
          <div class="feature-footer">
            <el-button type="success" link>立即使用 →</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/upward-mining-feasibility')">
          <div class="feature-icon" style="background-color: #f59e0b;">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <h3>上行开采可行度</h3>
          <p>基于钻孔CSV数据计算上行开采可行度,评估顶板稳定性</p>
          <div class="feature-footer">
            <el-button type="warning" link>立即使用 →</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="feature-card" @click="$router.push('/database-viewer')">
          <div class="feature-icon" style="background-color: #E6A23C;">
            <el-icon><Coin /></el-icon>
          </div>
          <h3>岩性数据库</h3>
          <p>查询、编辑岩石力学参数数据库,支持按岩性、省份筛选和统计分析</p>
          <div class="feature-footer">
            <el-button type="warning" link>立即使用 →</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 全局数据管理卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="global-data-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon style="vertical-align: middle; margin-right: 8px;"><FolderOpened /></el-icon>
                全局钻孔数据管理
              </span>
              <div>
                <el-tag v-if="globalDataStore.keyStratumData.length > 0" type="primary" size="large">
                  {{ globalDataStore.keyStratumData.length }} 条记录
                </el-tag>
              </div>
            </div>
          </template>
          
          <div v-if="!hasGlobalData" class="empty-state">
            <el-empty description="暂无全局钻孔数据，请先导入原始岩层数据">
              <el-button type="primary" size="large" @click="triggerFileSelect">
                <el-icon style="margin-right: 8px;"><Upload /></el-icon>
                导入钻孔数据
              </el-button>
            </el-empty>
          </div>
          
          <div v-else class="data-summary">
            <div class="summary-grid">
              <div class="summary-item">
                <el-icon class="summary-icon" color="#409EFF"><Document /></el-icon>
                <div class="summary-label">记录数量</div>
                <div class="summary-value">{{ globalDataStore.keyStratumData.length }}</div>
              </div>
              <div class="summary-item">
                <el-icon class="summary-icon" color="#67C23A"><Grid /></el-icon>
                <div class="summary-label">字段数量</div>
                <div class="summary-value">{{ globalDataStore.keyStratumColumns.length }}</div>
              </div>
              <div class="summary-item">
                <el-icon class="summary-icon" color="#E6A23C"><Location /></el-icon>
                <div class="summary-label">钻孔数量</div>
                <div class="summary-value">{{ uniqueBoreholes }}</div>
              </div>
              <div class="summary-item">
                <el-icon class="summary-icon" color="#F56C6C"><SuccessFilled /></el-icon>
                <div class="summary-label">数据状态</div>
                <div class="summary-value">原始数据</div>
              </div>
            </div>
            
            <div class="action-buttons">
              <el-button type="primary" @click="triggerFileSelect">
                <el-icon style="margin-right: 6px;"><RefreshRight /></el-icon>
                重新导入
              </el-button>
              <el-button type="info" @click="previewGlobalData">
                <el-icon style="margin-right: 6px;"><View /></el-icon>
                预览数据
              </el-button>
              <el-button type="warning" @click="exportGlobalData">
                <el-icon style="margin-right: 6px;"><Download /></el-icon>
                导出CSV
              </el-button>
              <el-button type="danger" @click="clearGlobalData">
                <el-icon style="margin-right: 6px;"><Delete /></el-icon>
                清空数据
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据可视化统计 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon style="vertical-align: middle; margin-right: 8px;"><TrendCharts /></el-icon>
                数据统计概览
              </span>
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button value="bar">柱状图</el-radio-button>
                <el-radio-button value="pie">饼图</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div id="statsChart" style="width: 100%; height: 360px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="activity-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon style="vertical-align: middle; margin-right: 8px;"><Clock /></el-icon>
                最近操作记录
              </span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :timestamp="activity.time"
              :color="activity.color"
              placement="top"
            >
              <div class="activity-content">
                <el-icon :color="activity.color" style="margin-right: 8px;">
                  <component :is="activity.icon" />
                </el-icon>
                <span>{{ activity.text }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
          <div v-if="recentActivities.length === 0" class="empty-activity">
            <el-empty description="暂无操作记录" :image-size="80" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 辅助工具与帮助 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="tools-help-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon style="vertical-align: middle; margin-right: 8px;"><Edit /></el-icon>
                快捷工具与帮助
              </span>
            </div>
          </template>
          <div class="tools-help-grid">
            <!-- 数据处理工具 -->
            <div class="tool-item" @click="$router.push('/csv-formatter')">
              <el-icon class="tool-icon" color="#409EFF"><Document /></el-icon>
              <div class="tool-info">
                <div class="tool-name">CSV 格式化工具</div>
                <div class="tool-desc">转换和规范化CSV文件格式</div>
              </div>
              <el-icon><ArrowRight /></el-icon>
            </div>
            <div class="tool-item" @click="$router.push('/borehole-analysis')">
              <el-icon class="tool-icon" color="#67C23A"><DataLine /></el-icon>
              <div class="tool-info">
                <div class="tool-name">钻孔数据分析</div>
                <div class="tool-desc">批量分析钻孔文件,提取煤层信息</div>
              </div>
              <el-icon><ArrowRight /></el-icon>
            </div>

            <!-- 帮助文档 -->
            <div class="tool-item" @click="showQuickStart = true">
              <el-icon class="tool-icon" color="#E6A23C"><Guide /></el-icon>
              <div class="tool-info">
                <div class="tool-name">快速开始指南</div>
                <div class="tool-desc">5分钟了解系统使用方法</div>
              </div>
              <el-icon><ArrowRight /></el-icon>
            </div>
            <div class="tool-item" @click="showFAQ = true">
              <el-icon class="tool-icon" color="#F56C6C"><QuestionFilled /></el-icon>
              <div class="tool-info">
                <div class="tool-name">常见问题解答</div>
                <div class="tool-desc">常见错误和解决方案</div>
              </div>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 导入数据对话框 -->
    <!-- 隐藏的文件输入框 -->
    <input ref="boreholeFileInput" type="file" multiple accept=".csv" class="hidden-input" @change="handleBoreholeImport" />
    
    <!-- 数据预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="全局数据预览" width="90%" top="5vh">
      <div style="margin-bottom: 12px;">
        <el-text>
          显示前 100 条记录 (共 {{ globalDataStore.keyStratumData.length }} 条原始钻孔数据)
        </el-text>
      </div>
      <el-table :data="previewData" border stripe height="60vh" style="width: 100%">
        <el-table-column
          v-for="col in (previewData.length > 0 ? Object.keys(previewData[0]) : [])"
          :key="col"
          :prop="col"
          :label="col"
          min-width="120"
          show-overflow-tooltip
        />
      </el-table>
    </el-dialog>

    <!-- 快速开始教程对话框 -->
    <el-dialog v-model="showQuickStart" title="📖 快速开始指南" width="800px" top="5vh">
      <el-scrollbar max-height="70vh">
        <div class="tutorial-content">
          <el-steps :active="activeStep" finish-status="success" align-center>
            <el-step title="准备数据" />
            <el-step title="导入数据" />
            <el-step title="开始分析" />
          </el-steps>

          <div class="step-content">
            <!-- 步骤1: 准备数据 -->
            <div v-show="activeStep === 0" class="tutorial-step">
              <h3>📁 步骤1: 准备钻孔数据文件</h3>
              <el-alert type="info" :closable="false" style="margin: 16px 0;">
                <p><strong>支持的文件格式:</strong> CSV文件 (UTF-8或GBK编码)</p>
              </el-alert>
              
              <p><strong>钻孔数据文件应包含以下列:</strong></p>
              <ul class="tutorial-list">
                <li><code>岩层名称</code> 或 <code>岩层</code> - 岩层的名称</li>
                <li><code>厚度/m</code> 或 <code>厚度</code> - 岩层厚度(米)</li>
                <li><code>弹性模量/GPa</code> - 岩石弹性模量</li>
                <li><code>容重/kN·m-3</code> - 岩石容重</li>
                <li><code>抗拉强度/MPa</code> - 岩石抗拉强度</li>
                <li>其他力学参数(可选)</li>
              </ul>

              <el-alert type="warning" :closable="false" style="margin: 16px 0;">
                <p><strong>注意事项:</strong></p>
                <ul style="margin: 8px 0; padding-left: 20px;">
                  <li>每个CSV文件代表一个钻孔</li>
                  <li>文件名将作为钻孔名称</li>
                  <li>可批量导入多个钻孔文件</li>
                </ul>
              </el-alert>
            </div>

            <!-- 步骤2: 导入数据 -->
            <div v-show="activeStep === 1" class="tutorial-step">
              <h3>📤 步骤2: 导入钻孔数据</h3>
              
              <div class="tutorial-section">
                <h4>方法一: 通过首页导入 (推荐)</h4>
                <ol class="tutorial-list">
                  <li>点击 <el-button type="primary" size="small" plain>导入钻孔数据</el-button> 按钮</li>
                  <li>选择一个或多个钻孔CSV文件</li>
                  <li>系统自动解析并显示导入结果</li>
                  <li>数据将保存到全局存储,供所有模块使用</li>
                </ol>
              </div>

              <div class="tutorial-section">
                <h4>方法二: 在功能模块中导入</h4>
                <ul class="tutorial-list">
                  <li><strong>关键层计算:</strong> 直接在模块内上传岩层数据文件</li>
                  <li><strong>三维建模:</strong> 需同时上传钻孔数据和坐标文件</li>
                </ul>
              </div>

              <el-alert type="success" :closable="false" style="margin: 16px 0;">
                <p><strong>✅ 导入成功后,您将看到:</strong></p>
                <ul style="margin: 8px 0; padding-left: 20px;">
                  <li>记录总数和钻孔数量统计</li>
                  <li>数据预览和管理功能</li>
                  <li>可随时导出或清空数据</li>
                </ul>
              </el-alert>
            </div>

            <!-- 步骤3: 开始分析 -->
            <div v-show="activeStep === 2" class="tutorial-step">
              <h3>🚀 步骤3: 使用功能模块</h3>
              
              <div class="module-guide">
                <el-card class="module-card" shadow="hover">
                  <h4>🔬 关键层计算</h4>
                  <p><strong>功能:</strong> 自动识别煤层上覆岩层中的关键层位置</p>
                  <p><strong>使用步骤:</strong></p>
                  <ol style="font-size: 13px; padding-left: 20px;">
                    <li>上传钻孔岩层数据文件</li>
                    <li>选择是否从数据库填充缺失参数</li>
                    <li>选择目标煤层</li>
                    <li>点击"计算关键层"</li>
                    <li>查看结果并导出Excel/CSV</li>
                  </ol>
                </el-card>

                <el-card class="module-card" shadow="hover">
                  <h4>🗺️ 三维地质建模</h4>
                  <p><strong>功能:</strong> 基于钻孔数据生成煤层三维块体模型</p>
                  <p><strong>使用步骤:</strong></p>
                  <ol style="font-size: 13px; padding-left: 20px;">
                    <li>上传钻孔数据和坐标文件</li>
                    <li>选择X、Y坐标列和厚度列</li>
                    <li>选择要建模的煤层</li>
                    <li>选择插值方法(线性/三次/RBF等)</li>
                    <li>生成并查看3D可视化模型</li>
                  </ol>
                </el-card>

                <el-card class="module-card" shadow="hover">
                  <h4>💾 岩性数据库</h4>
                  <p><strong>功能:</strong> 查询和管理岩石力学参数数据库</p>
                  <p><strong>使用步骤:</strong></p>
                  <ol style="font-size: 13px; padding-left: 20px;">
                    <li>浏览数据库概览和统计</li>
                    <li>按岩性或省份筛选记录</li>
                    <li>查看岩性参数统计信息</li>
                    <li>编辑或添加新记录</li>
                  </ol>
                </el-card>
              </div>

              <el-alert type="info" :closable="false" style="margin: 16px 0;">
                <p><strong>💡 提示:</strong> 建议先在首页导入全局钻孔数据,然后在各功能模块中直接使用!</p>
              </el-alert>
            </div>
          </div>

          <div class="tutorial-navigation">
            <el-button v-if="activeStep > 0" @click="activeStep--">上一步</el-button>
            <el-button v-if="activeStep < 2" type="primary" @click="activeStep++">下一步</el-button>
            <el-button v-if="activeStep === 2" type="success" @click="showQuickStart = false">开始使用</el-button>
          </div>
        </div>
      </el-scrollbar>
    </el-dialog>

    <!-- 常见问题对话框 -->
    <el-dialog v-model="showFAQ" title="❓ 常见问题解答" width="800px" top="5vh">
      <el-scrollbar max-height="70vh">
        <div class="faq-content">
          <el-collapse accordion>
            <el-collapse-item name="1">
              <template #title>
                <span class="faq-title">❓ 上传文件后提示"缺少必需列"怎么办?</span>
              </template>
              <div class="faq-answer">
                <p><strong>原因:</strong> CSV文件缺少必需的列名或列名格式不正确</p>
                <p><strong>解决方案:</strong></p>
                <ul>
                  <li>检查文件是否包含 <code>岩层名称</code> 和 <code>厚度/m</code> 列</li>
                  <li>使用"CSV格式化工具"转换文件格式</li>
                  <li>确保列名与系统要求一致(可使用示例文件作为参考)</li>
                </ul>
              </div>
            </el-collapse-item>

            <el-collapse-item name="2">
              <template #title>
                <span class="faq-title">❓ 关键层计算时提示"未找到目标岩层"?</span>
              </template>
              <div class="faq-answer">
                <p><strong>原因:</strong> 文件中不包含您选择的煤层名称</p>
                <p><strong>解决方案:</strong></p>
                <ul>
                  <li>点击"获取可选煤层"按钮查看文件中包含的煤层</li>
                  <li>确保选择的煤层名称与文件中完全一致(包括空格)</li>
                  <li>检查岩层名称列是否正确标识了煤层</li>
                </ul>
              </div>
            </el-collapse-item>

            <el-collapse-item name="3">
              <template #title>
                <span class="faq-title">❓ 三维建模时部分岩层被跳过?</span>
              </template>
              <div class="faq-answer">
                <p><strong>原因:</strong> 某些岩层的数据点不足或数据质量问题</p>
                <p><strong>解决方案:</strong></p>
                <ul>
                  <li>查看跳过岩层的详细说明</li>
                  <li>对于数据点很少(1-3个)的岩层,系统会自动使用最近邻插值</li>
                  <li>建议补充更多钻孔数据以提高建模质量</li>
                  <li>可以取消选择数据点不足的岩层</li>
                </ul>
              </div>
            </el-collapse-item>

            <el-collapse-item name="4">
              <template #title>
                <span class="faq-title">❓ 如何从数据库填充缺失的力学参数?</span>
              </template>
              <div class="faq-answer">
                <p><strong>操作步骤:</strong></p>
                <ol>
                  <li>在关键层计算模块上传钻孔文件后</li>
                  <li>点击"从数据库填充"按钮</li>
                  <li>系统自动根据岩层名称匹配数据库中的中位值</li>
                  <li>预览填充后的数据确认无误</li>
                </ol>
                <p><strong>注意:</strong> 只会填充空值或0值,不会覆盖已有数据</p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="5">
              <template #title>
                <span class="faq-title">❓ 三维建模选择哪种插值方法好?</span>
              </template>
              <div class="faq-answer">
                <p><strong>推荐选择:</strong></p>
                <ul>
                  <li><strong>线性插值 (Linear):</strong> 适合数据点较少,速度快,平滑度一般</li>
                  <li><strong>三次样条 (Cubic):</strong> 适合数据点充足(9个以上),平滑度好</li>
                  <li><strong>径向基函数 (RBF):</strong> 适合复杂曲面,计算量大</li>
                  <li><strong>最近邻 (Nearest):</strong> 适合极少数据点,不平滑</li>
                </ul>
                <p><strong>提示:</strong> 可使用"插值方法对比"功能自动选择最佳方法</p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="6">
              <template #title>
                <span class="faq-title">❓ CSV文件编码问题导致乱码?</span>
              </template>
              <div class="faq-answer">
                <p><strong>解决方案:</strong></p>
                <ul>
                  <li>系统自动支持 UTF-8、UTF-8-BOM 和 GBK 编码</li>
                  <li>如仍有乱码,用Excel打开文件,另存为 UTF-8 CSV</li>
                  <li>或用记事本打开,选择"另存为",编码选择UTF-8</li>
                </ul>
              </div>
            </el-collapse-item>
          </el-collapse>

          <el-alert type="info" :closable="false" style="margin-top: 20px;">
            <p><strong>💡 还有其他问题?</strong></p>
            <p>查看完整文档: <code>README.md</code> | <code>QUICKSTART.md</code></p>
          </el-alert>
        </div>
      </el-scrollbar>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  Coin, Files, Picture, UploadFilled, DataAnalysis, Guide,
  FolderOpened, Upload, Document, Grid, Location, SuccessFilled,
  RefreshRight, View, Download, Delete, Edit, ArrowRight,
  QuestionFilled, DataLine, TrendCharts, Clock
} from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import { getApiBase } from '@/utils/api';
import { useGlobalDataStore } from '@/stores/globalData';

// 初始化store
const globalDataStore = useGlobalDataStore();

const API_BASE = getApiBase();
const stats = ref({
  rock_db_count: 0,
  borehole_file_count: 0,
  modeling_record_count: 0
});

const showPreviewDialog = ref(false);
const showQuickStart = ref(false);
const showFAQ = ref(false);
const isImporting = ref(false);
const activeStep = ref(0);
const boreholeFileInput = ref(null);

// 直接触发文件选择
const triggerFileSelect = () => {
  boreholeFileInput.value?.click();
};

// 图表相关
const chartType = ref('bar');
let myChart = null;

// 最近活动
const recentActivities = ref([
  { time: '刚刚', text: '系统启动成功', color: '#67C23A', icon: 'SuccessFilled' },
  { time: '5分钟前', text: '数据库连接正常', color: '#409EFF', icon: 'Coin' },
  { time: '10分钟前', text: '前端服务已启动', color: '#E6A23C', icon: 'Monitor' }
]);

const hasGlobalData = computed(() => 
  globalDataStore.boreholeData.length > 0 || 
  globalDataStore.keyStratumData.length > 0
);

const uniqueBoreholes = computed(() => {
  const data = globalDataStore.keyStratumData;
  if (!data || !data.length) return 0;
  const boreholes = new Set(data.map(row => row['钻孔名'] || row['钻孔'] || row['BK']).filter(Boolean));
  return boreholes.size;
});

const previewData = computed(() => {
  // 只显示岩层数据(钻孔原始数据)
  if (globalDataStore.keyStratumData.length > 0) {
    return globalDataStore.keyStratumData.slice(0, 100);
  }
  return [];
});

const fetchStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/dashboard/stats`);
    
    // 检查响应状态
    if (!response.ok) {
      console.error('服务器返回错误状态:', response.status, response.statusText);
      // 使用默认值，不显示错误
      stats.value = {
        rock_db_count: 0,
        borehole_file_count: 0,
        modeling_record_count: 0,
      };
      return;
    }
    
    // 尝试解析 JSON
    const res = await response.json();
    if (res.status === 'success') {
      stats.value = {
        rock_db_count: res.stats?.rock_db_count ?? 0,
        borehole_file_count: res.stats?.borehole_file_count ?? 0,
        modeling_record_count: res.stats?.modeling_record_count ?? 0,
      };
    } else {
      ElMessage.error(res.message || '获取统计数据失败');
    }
  } catch (e) {
    console.error('获取统计数据失败:', e);
    // 使用默认值，不显示重复的错误消息
    stats.value = {
      rock_db_count: 0,
      borehole_file_count: 0,
      modeling_record_count: 0,
    };
  }
};

const handleBoreholeImport = async (event) => {
  const files = Array.from(event.target.files || []);
  event.target.value = '';
  if (!files.length) return;

  isImporting.value = true;
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  try {
    // 使用原始数据导入接口,不做业务处理
    const res = await fetch(`${API_BASE}/raw/import`, {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    
    if (!res.ok || data.status !== 'success') {
      throw new Error(data.detail || data.message || '导入失败');
    }

    const records = data.records || [];
    const columns = data.columns || [];
    const excludedColumns = data.excluded_columns || [];
    
    console.log('原始钻孔数据导入成功');
    console.log('记录数:', records.length);
    console.log('保留的列名:', columns);
    console.log('排除的列名:', excludedColumns);
    
    // 保存到岩层数据存储(用于关键层计算)
    globalDataStore.loadKeyStratumData(
      records,
      columns
    );

    let message = `成功导入 ${records.length} 条原始钻孔数据`;
    if (excludedColumns.length > 0) {
      message += ` (已过滤 ${excludedColumns.length} 个计算字段)`;
    }
    
    ElMessage.success(message);
  } catch (error) {
    console.error('导入钻孔数据失败:', error);
    ElMessage.error(error.message || '导入失败');
  } finally {
    isImporting.value = false;
  }
};

const previewGlobalData = () => {
  showPreviewDialog.value = true;
};

const exportGlobalData = async () => {
  try {
    if (globalDataStore.keyStratumData.length === 0) {
      ElMessage.warning('没有可导出的数据');
      return;
    }
    
    const records = globalDataStore.keyStratumData;
    const columns = globalDataStore.keyStratumColumns;
    const filename = `钻孔原始数据_${new Date().toISOString().slice(0,10)}.csv`;
    
    const csv = convertToCSV(records, columns);
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
    ElMessage.success('数据已导出');
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败');
  }
};

const convertToCSV = (records, columns) => {
  if (!records || !records.length) return '';
  const header = columns.join(',');
  const rows = records.map(record => 
    columns.map(col => {
      const value = record[col];
      return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
    }).join(',')
  );
  return [header, ...rows].join('\n');
};

const clearGlobalData = async () => {
  try {
    await ElMessageBox.confirm('确定要清空全局数据吗？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    globalDataStore.clear();
    ElMessage.success('已清空全局数据');
  } catch {
    // 用户取消
  }
};

// 初始化图表
const initChart = () => {
  nextTick(() => {
    const chartDom = document.getElementById('statsChart');
    if (!chartDom) return;
    
    myChart = echarts.init(chartDom);
    updateChart();
  });
};

// 更新图表
const updateChart = () => {
  if (!myChart) return;
  
  const option = chartType.value === 'bar' ? getBarOption() : getPieOption();
  myChart.setOption(option);
};

// 柱状图配置
const getBarOption = () => {
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['岩石数据库', '钻孔文件', '建模记录', '全局钻孔'],
      axisLabel: { interval: 0, rotate: 0 }
    },
    yAxis: {
      type: 'value',
      name: '数量'
    },
    series: [
      {
        name: '数据统计',
        type: 'bar',
        data: [
          { value: stats.value.rock_db_count, itemStyle: { color: '#667eea' } },
          { value: stats.value.borehole_file_count, itemStyle: { color: '#f093fb' } },
          { value: stats.value.modeling_record_count, itemStyle: { color: '#4facfe' } },
          { value: uniqueBoreholes.value, itemStyle: { color: '#43e97b' } }
        ],
        barWidth: '50%',
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        }
      }
    ]
  };
};

// 饼图配置
const getPieOption = () => {
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center'
    },
    series: [
      {
        name: '数据分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: stats.value.rock_db_count, name: '岩石数据库', itemStyle: { color: '#667eea' } },
          { value: stats.value.borehole_file_count, name: '钻孔文件', itemStyle: { color: '#f093fb' } },
          { value: stats.value.modeling_record_count, name: '建模记录', itemStyle: { color: '#4facfe' } },
          { value: uniqueBoreholes.value, name: '全局钻孔', itemStyle: { color: '#43e97b' } }
        ]
      }
    ]
  };
};

// 监听图表类型变化
watch(chartType, () => {
  updateChart();
});

// 监听数据变化
watch(stats, () => {
  updateChart();
}, { deep: true });

// 监听窗口大小变化
const handleResize = () => {
  if (myChart) {
    myChart.resize();
  }
};

onMounted(() => {
  fetchStats();
  initChart();
  window.addEventListener('resize', handleResize);
});
</script>

<style scoped>
.dashboard-container { 
  padding: 20px;
  background-color: #f0f2f5;
}

/* 欢迎卡片 */
.welcome-card { 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; 
  margin-bottom: 20px;
  border: none;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.welcome-text h1 { 
  margin: 0 0 12px 0; 
  font-size: 32px;
  font-weight: 700;
}

.welcome-text p {
  opacity: 0.95;
  font-size: 16px;
  margin: 0 0 16px 0;
}

.feature-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.feature-tags .el-tag {
  font-size: 13px;
}

/* 统计卡片 */
.stats-row { 
  margin-bottom: 20px; 
}

.stat-card {
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-item { 
  display: flex; 
  align-items: center;
  padding: 4px 0;
}

.stat-icon {
  width: 64px; 
  height: 64px; 
  border-radius: 16px;
  display: flex; 
  align-items: center; 
  justify-content: center;
  font-size: 32px; 
  color: white; 
  margin-right: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stat-text {
  flex: 1;
}

.stat-title { 
  font-size: 13px; 
  color: #909399;
  margin-bottom: 4px;
}

.stat-value { 
  font-size: 28px; 
  font-weight: 700; 
  color: #303133;
  line-height: 1;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: #C0C4CC;
}

/* 功能模块卡片 */
.feature-row {
  margin-bottom: 20px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  padding: 16px 8px;
  min-height: 240px;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.feature-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: white;
  margin: 0 auto 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.feature-card p {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 16px 0;
  min-height: 60px;
}

.feature-footer {
  margin-top: auto;
}

/* 全局数据卡片 */
.global-data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.data-summary {
  padding: 12px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-item {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf0 100%);
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s ease;
}

.summary-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.summary-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin: 8px 0;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 工具和帮助卡片 */
.tools-help-card {
  margin-bottom: 20px;
}

.tools-help-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.tool-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tool-item:hover {
  background: #e8ecf0;
  transform: translateX(4px);
}

.tool-icon {
  font-size: 28px;
  margin-right: 16px;
}

.tool-info {
  flex: 1;
}

.tool-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.tool-desc {
  font-size: 13px;
  color: #909399;
}

/* 对话框样式 */
.import-section {
  padding: 40px 20px;
  text-align: center;
}

.import-tip {
  margin-top: 16px;
  color: #909399;
  font-size: 13px;
}

.hidden-input {
  display: none;
}

/* 教程内容 */
.tutorial-content {
  padding: 20px 0;
}

.step-content {
  min-height: 400px;
  margin-top: 32px;
}

.tutorial-step h3 {
  color: #303133;
  font-size: 20px;
  margin-bottom: 16px;
}

.tutorial-step h4 {
  color: #409EFF;
  font-size: 16px;
  margin: 20px 0 12px;
}

.tutorial-list {
  line-height: 1.8;
  color: #606266;
  padding-left: 24px;
}

.tutorial-list li {
  margin: 8px 0;
}

.tutorial-list code {
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
  color: #409EFF;
  font-size: 13px;
}

.tutorial-section {
  margin: 24px 0;
}

.tutorial-navigation {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.module-guide {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin: 20px 0;
}

.module-card {
  margin-bottom: 0;
}

.module-card h4 {
  color: #303133;
  font-size: 16px;
  margin: 0 0 12px 0;
}

.module-card p {
  font-size: 13px;
  color: #606266;
  margin: 8px 0;
  line-height: 1.6;
}

/* FAQ样式 */
.faq-content {
  padding: 12px 0;
}

.faq-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.faq-answer {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-top: 8px;
}

.faq-answer p {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.faq-answer ul,
.faq-answer ol {
  margin: 12px 0;
  padding-left: 24px;
  color: #606266;
  line-height: 1.8;
}

.faq-answer li {
  margin: 6px 0;
}

.faq-answer code {
  background: #e8ecf0;
  padding: 2px 8px;
  border-radius: 4px;
  color: #409EFF;
  font-size: 13px;
}

/* 图表卡片 */
.chart-card {
  margin-bottom: 20px;
}

/* 活动卡片 */
.activity-card {
  margin-bottom: 20px;
}

.activity-content {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.empty-activity {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .welcome-content {
    flex-direction: column;
    text-align: center;
  }

  .welcome-action {
    margin-top: 16px;
  }

  .tools-help-grid {
    grid-template-columns: 1fr;
  }
}
</style>