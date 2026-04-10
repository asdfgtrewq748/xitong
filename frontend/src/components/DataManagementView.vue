<template>
  <div class="data-management-container" role="main" aria-label="全局数据管理中心">
    <!-- 顶部欢迎横幅 -->
    <el-card shadow="hover" class="welcome-banner" role="banner">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1 id="page-title">🗂️ 全局数据管理中心</h1>
          <p>统一管理钻孔数据、煤层参数与地质信息，为所有功能模块提供数据基础</p>
          <div class="feature-badges" role="list" aria-label="功能特性">
            <el-tag type="success" effect="plain" size="large" role="listitem">智能导入</el-tag>
            <el-tag type="primary" effect="plain" size="large" role="listitem">实时预览</el-tag>
            <el-tag type="warning" effect="plain" size="large" role="listitem">版本管理</el-tag>
            <el-tag type="info" effect="plain" size="large" role="listitem">质量检查</el-tag>
          </div>
        </div>
        <div class="welcome-actions">
          <el-button 
            type="primary" 
            size="large" 
            round 
            plain 
            @click="showConceptDialog = true"
            aria-label="了解什么是全局数据"
          >
            <el-icon style="margin-right: 8px;"><QuestionFilled /></el-icon>
            什么是全局数据？
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据统计卡片组 -->
    <el-row :gutter="20" class="stats-row" role="region" aria-label="数据统计概览">
      <el-col :span="6" :xs="24" :sm="12" :md="12" :lg="6">
        <el-card shadow="hover" class="stat-card stat-card-primary" role="article" aria-label="钻孔数量统计">
          <div class="stat-item">
            <div class="stat-icon" aria-hidden="true"><el-icon><DataLine /></el-icon></div>
            <div class="stat-text">
              <div class="stat-label">钻孔数量</div>
              <div class="stat-value" aria-live="polite">{{ statistics.boreholeCount }}</div>
              <div class="stat-unit">个</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="12" :lg="6">
        <el-card shadow="hover" class="stat-card stat-card-success" role="article" aria-label="煤层数据统计">
          <div class="stat-item">
            <div class="stat-icon" aria-hidden="true"><el-icon><Collection /></el-icon></div>
            <div class="stat-text">
              <div class="stat-label">煤层数据</div>
              <div class="stat-value" aria-live="polite">{{ statistics.coalSeamCount }}</div>
              <div class="stat-unit">条</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="12" :lg="6">
        <el-card shadow="hover" class="stat-card stat-card-warning" role="article" aria-label="矿井数量统计">
          <div class="stat-item">
            <div class="stat-icon" aria-hidden="true"><el-icon><OfficeBuilding /></el-icon></div>
            <div class="stat-text">
              <div class="stat-label">矿井数量</div>
              <div class="stat-value" aria-live="polite">{{ statistics.uniqueMines }}</div>
              <div class="stat-unit">个</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="12" :lg="6">
        <el-card shadow="hover" class="stat-card stat-card-info" role="article" aria-label="总记录数统计">
          <div class="stat-item">
            <div class="stat-icon" aria-hidden="true"><el-icon><Files /></el-icon></div>
            <div class="stat-text">
              <div class="stat-label">总记录数</div>
              <div class="stat-value" aria-live="polite">{{ statistics.totalRecords }}</div>
              <div class="stat-unit">条</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 - 左右分栏布局 -->
    <el-row :gutter="20" class="main-content-row">
      <!-- 左侧：数据导入与预览 -->
      <el-col :span="16" :xs="24" :sm="24" :md="24" :lg="16">
        <!-- 快捷操作横幅（仅在无数据时显示） -->
        <el-card shadow="hover" class="quick-actions-card" v-if="!hasGlobalData" role="complementary">
          <div class="quick-actions-banner">
            <div class="banner-left">
              <h3>🚀 快速开始</h3>
              <p>选择一种方式开始使用全局数据功能</p>
            </div>
            <div class="banner-actions">
              <el-button type="primary" size="large" @click="downloadSampleCSV">
                <el-icon style="margin-right: 6px;"><Download /></el-icon>
                下载模板
              </el-button>
              <el-button type="success" size="large" @click="loadExampleData" :loading="loading">
                <el-icon style="margin-right: 6px;"><VideoPlay /></el-icon>
                加载示例
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 数据导入卡片 -->
        <el-card shadow="hover" class="upload-card" ref="uploadRef">
          <template #header>
            <div class="card-header-inline">
              <div class="header-title">
                <el-icon style="vertical-align: middle; margin-right: 6px;"><Upload /></el-icon>
                数据导入
              </div>
              <el-tooltip content="支持批量上传CSV格式钻孔数据" placement="top">
                <el-tag size="small" effect="plain">支持 .csv 格式</el-tag>
              </el-tooltip>
            </div>
          </template>
          
          <div class="upload-wrapper">
            <el-upload
              ref="uploadRefInner"
              class="upload-area"
              drag
              multiple
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
              accept=".csv"
              :limit="100"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="upload-text">
                <strong>点击或拖拽文件到此处</strong>
                <p>支持批量上传多个 CSV 文件</p>
                <p style="font-size: 12px; color: #67C23A; margin-top: 4px;">
                  💡 钻孔名会自动从文件名提取（无需CSV包含钻孔名列）
                </p>
              </div>
            </el-upload>
            
            <div class="upload-actions" v-if="fileList.length > 0">
              <div class="file-count">
                <el-icon style="margin-right: 4px;"><Document /></el-icon>
                已选择 {{ fileList.length }} 个文件
              </div>
              <el-button type="primary" size="large" @click="batchImportFiles" :loading="loading">
                <el-icon style="margin-right: 6px;"><Check /></el-icon>
                开始导入
              </el-button>
            </div>

            <!-- 进度条（细化步骤显示） -->
            <transition name="fade">
              <div class="progress-bar-wrapper" v-if="importing">
                <el-steps :active="importStep" finish-status="success" align-center style="margin-bottom: 16px;">
                  <el-step title="上传文件" />
                  <el-step title="解析数据" />
                  <el-step title="验证质量" />
                  <el-step title="导入完成" />
                </el-steps>
                <el-progress 
                  :percentage="importProgress" 
                  :status="importStatus" 
                  :stroke-width="20" 
                  striped 
                  striped-flow
                >
                  <template #default="{ percentage }">
                    <span style="color: #409EFF; font-weight: 600;">{{ percentage }}%</span>
                  </template>
                </el-progress>
                <p class="progress-text">
                  <el-icon class="is-loading" v-if="importStatus !== 'success' && importStatus !== 'exception'">
                    <Loading />
                  </el-icon>
                  {{ importMessage }}
                </p>
              </div>
            </transition>
          </div>
        </el-card>

        <!-- 数据预览表格 -->
        <el-card shadow="hover" class="table-card" ref="tableRef">
          <template #header>
            <div class="card-header-inline">
              <div class="header-title">
                <el-icon style="vertical-align: middle; margin-right: 6px;"><List /></el-icon>
                数据预览
                <el-tag v-if="globalDataStore.keyStratumData.length" type="info" size="small" style="margin-left: 10px;">
                  {{ globalDataStore.keyStratumData.length }} 条记录
                </el-tag>
                <el-tag v-if="selectedRows.length" type="warning" size="small" style="margin-left: 8px;">
                  已选 {{ selectedRows.length }} 条
                </el-tag>
              </div>
              <div class="header-right">
                <el-tooltip content="批量删除选中数据" placement="top">
                  <el-button
                    type="danger"
                    size="small"
                    :disabled="!selectedRows.length"
                    @click="batchDeleteRows"
                    style="margin-right: 8px;"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="查看统计图表" placement="top">
                  <el-button
                    type="primary"
                    size="small"
                    @click="showStatsChart = true"
                    :disabled="!hasGlobalData"
                    style="margin-right: 8px;"
                  >
                    <el-icon><DataAnalysis /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="列显示管理" placement="top">
                  <el-button
                    type="info"
                    size="small"
                    @click="showColumnManager = true"
                    style="margin-right: 8px;"
                  >
                    <el-icon><Setting /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-input 
                  v-model="searchQuery" 
                  placeholder="搜索..." 
                  :prefix-icon="Search" 
                  clearable 
                  style="width: 200px; margin-right: 8px;" 
                />
                <el-select 
                  v-model="selectedLithology" 
                  placeholder="岩性筛选" 
                  clearable 
                  style="width: 140px; margin-right: 8px;"
                >
                  <el-option v-for="l in uniqueLithologies" :key="l" :label="l" :value="l" />
                </el-select>
                <el-tooltip content="刷新数据" placement="top">
                  <el-button :icon="Refresh" circle @click="refreshData" :loading="loading" />
                </el-tooltip>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="filteredData" 
            stripe 
            style="width: 100%" 
            height="500" 
            v-loading="loading"
            @selection-change="handleSelectionChange"
            ref="tableRef"
          >
              <el-table-column type="selection" width="55" />
              <el-table-column v-if="visibleColumns['钻孔名']" prop="钻孔名" label="钻孔名" width="120" sortable fixed>
                <template #header>
                  <el-tooltip content="点击排序" placement="top">
                    <span>钻孔名</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column v-if="visibleColumns['岩层']" prop="岩层" label="岩层" width="120" sortable>
                <template #default="{ row }">
                  <el-tag :type="getLithologyColor(row['岩层'])" size="small">{{ row['岩层'] }}</el-tag>
                </template>
                <template #header>
                  <el-tooltip content="点击排序 | 不同岩性自动着色" placement="top">
                    <span>岩层</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column v-if="visibleColumns['厚度/m']" prop="厚度/m" label="厚度(m)" sortable />
              <el-table-column v-if="visibleColumns['弹性模量/GPa']" prop="弹性模量/GPa" label="弹模(GPa)" sortable />
              <el-table-column v-if="visibleColumns['容重/kN·m-3']" prop="容重/kN·m-3" label="容重" sortable />
              <el-table-column v-if="visibleColumns['抗拉强度/MPa']" prop="抗拉强度/MPa" label="抗拉" sortable />
              <el-table-column v-if="visibleColumns['泊松比']" prop="泊松比" label="泊松比" sortable />
              <el-table-column v-if="visibleColumns['数据来源']" prop="数据来源" label="来源" sortable />
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="viewDetails(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            
          <template #empty>
            <el-empty description="暂无数据，请先导入钻孔数据" />
          </template>
          
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="globalDataStore.keyStratumData.length"
              layout="total, sizes, prev, pager, next, jumper"
              :page-sizes="[20, 50, 100, 200]"
            />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：历史记录与帮助 -->
      <el-col :span="8" :xs="24" :sm="24" :md="24" :lg="8">
        <el-card shadow="hover" class="history-card" ref="historyRef" role="complementary" aria-label="导入历史记录">
          <template #header>
            <div class="card-header-inline">
              <div class="header-title">
                <el-icon style="vertical-align: middle; margin-right: 6px;"><Timer /></el-icon>
                导入历史
              </div>
              <el-button 
                link 
                type="danger" 
                size="small" 
                @click="handleClearHistory" 
                v-if="globalDataStore.importHistory.length"
                aria-label="清空所有历史记录"
              >
                清空
              </el-button>
            </div>
          </template>
          
          <div class="history-list">
            <el-empty v-if="!globalDataStore.importHistory.length" description="暂无历史记录" :image-size="60" />
            <el-timeline v-else role="list" aria-label="历史记录时间线">
              <el-timeline-item
                v-for="item in globalDataStore.importHistory"
                :key="item.id"
                :timestamp="formatDate(item.timestamp)"
                :type="item.source === '文件导入' ? 'success' : 'primary'"
                size="large"
              >
                <div class="history-item-content">
                  <div class="history-meta">
                    <el-tag size="small" type="success">{{ item.source }}</el-tag>
                    <el-tag size="small" type="info">+{{ item.recordCount }}条</el-tag>
                    <el-tag v-if="item.changes" size="small" type="warning">{{ item.changes }}处变更</el-tag>
                  </div>
                  <div class="history-actions">
                    <el-tooltip content="查看详情" placement="top">
                      <el-button link type="info" size="small" @click="viewHistoryDetail(item)">
                        <el-icon><Document /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="回滚到此版本" placement="top">
                      <el-button link type="primary" size="small" @click="handleRollback(item.id)">
                        <el-icon><RefreshLeft /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="删除记录" placement="top">
                      <el-button link type="danger" size="small" @click="handleDeleteHistory(item.id)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>

        <!-- 数据操作卡片 -->
        <el-card shadow="hover" class="operations-card" style="margin-top: 20px;">
          <template #header>
            <div class="header-title">
              <el-icon style="vertical-align: middle; margin-right: 6px;"><Setting /></el-icon>
              数据操作
            </div>
          </template>
          
          <div class="operation-buttons">
            <el-button 
              type="success" 
              :icon="Download" 
              @click="exportGlobalData"
              :disabled="!hasGlobalData"
            >
              导出CSV
            </el-button>
            <el-button 
              type="warning" 
              :icon="RefreshRight" 
              @click="downloadSampleCSV"
            >
              下载模板
            </el-button>
            <el-button 
              type="danger" 
              :icon="Delete" 
              @click="clearAllData"
              :disabled="!hasGlobalData"
            >
              清空数据
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- "什么是全局数据"对话框 -->
    <el-dialog
      v-model="showConceptDialog"
      title="💡 什么是全局数据？"
      width="600px"
      class="concept-dialog"
    >
      <div class="concept-content">
        <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px;">
          <template #title>
            <strong>核心概念</strong>
          </template>
          全局数据是整个系统共享的基础数据源，所有功能模块都会使用这里导入的钻孔和岩层数据。
        </el-alert>

        <div class="concept-section">
          <h4>🎯 作用说明</h4>
          <ul>
            <li><strong>统一数据源：</strong>避免在每个功能模块重复导入相同数据</li>
            <li><strong>数据共享：</strong>关键层计算、地质建模等功能都使用全局数据</li>
            <li><strong>版本管理：</strong>自动记录导入历史，支持数据回滚</li>
            <li><strong>质量保证：</strong>统一的数据验证和格式检查</li>
          </ul>
        </div>

        <div class="concept-section">
          <h4>📋 使用流程</h4>
          <ol>
            <li>准备CSV格式的钻孔数据文件</li>
            <li>拖拽或点击上传区域选择文件</li>
            <li>系统自动解析并预览数据</li>
            <li>确认无误后点击"开始导入"</li>
            <li>导入后即可在各功能模块中使用</li>
          </ol>
        </div>

        <div class="concept-section">
          <h4>💡 小贴士</h4>
          <el-tag type="success" style="margin-right: 8px;">可批量导入多个文件</el-tag>
          <el-tag type="primary" style="margin-right: 8px;">支持导入历史回滚</el-tag>
          <el-tag type="warning">建议定期导出备份</el-tag>
        </div>

        <div class="concept-section">
          <h4>⌨️ 快捷键</h4>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="Ctrl/Cmd + S">导出CSV数据</el-descriptions-item>
            <el-descriptions-item label="Ctrl/Cmd + U">打开文件上传</el-descriptions-item>
            <el-descriptions-item label="Ctrl/Cmd + D">下载CSV模板</el-descriptions-item>
            <el-descriptions-item label="Ctrl/Cmd + H">跳转到历史记录</el-descriptions-item>
            <el-descriptions-item label="F1">显示帮助信息</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <template #footer>
        <el-button type="primary" @click="showConceptDialog = false">我知道了</el-button>
      </template>
    </el-dialog>

    <!-- 字段映射与数据预览对话框 -->
    <el-dialog
      v-model="showFieldMapping"
      title="🔍 数据预览与字段映射"
      width="1000px"
      class="field-mapping-dialog"
      :close-on-click-modal="false"
    >
      <el-steps :active="2" finish-status="success" align-center style="margin-bottom: 24px;">
        <el-step title="选择文件" :icon="Upload" />
        <el-step title="预览与映射" :icon="View" />
        <el-step title="确认导入" :icon="Check" />
      </el-steps>

      <!-- 质量检查报告 -->
      <el-alert
        v-if="qualityReport && qualityReport.issues.length > 0"
        type="error"
        :closable="false"
        style="margin-bottom: 16px;"
      >
        <template #title>
          <strong>❌ 发现 {{ qualityReport.issues.length }} 个错误</strong>
        </template>
        <ul style="margin: 8px 0 0 20px; padding: 0;">
          <li v-for="(issue, idx) in qualityReport.issues" :key="idx">
            {{ issue.message }}
          </li>
        </ul>
      </el-alert>

      <el-alert
        v-if="qualityReport && qualityReport.warnings.length > 0"
        type="warning"
        :closable="false"
        style="margin-bottom: 16px;"
      >
        <template #title>
          <strong>⚠️ 发现 {{ qualityReport.warnings.length }} 个警告</strong>
        </template>
        <ul style="margin: 8px 0 0 20px; padding: 0;">
          <li v-for="(warning, idx) in qualityReport.warnings" :key="idx">
            {{ warning.message }}
          </li>
        </ul>
      </el-alert>

      <!-- 字段映射配置 -->
      <el-card shadow="never" style="margin-bottom: 16px;">
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span><strong>📋 字段映射配置</strong></span>
            <el-button size="small" type="primary" plain @click="resetFieldMapping">
              <el-icon style="margin-right: 4px;"><Refresh /></el-icon>
              重置为智能映射
            </el-button>
          </div>
        </template>
        
        <el-row :gutter="16">
          <el-col :span="12" v-for="field in detectedFields" :key="field">
            <div style="margin-bottom: 12px;">
              <label style="display: block; margin-bottom: 6px; color: #475569; font-size: 13px;">
                CSV列: <strong>{{ field }}</strong>
              </label>
              <el-select
                v-model="fieldMapping[field]"
                placeholder="选择映射到的标准字段"
                style="width: 100%;"
                size="large"
              >
                <el-option
                  v-for="stdField in STANDARD_FIELDS"
                  :key="stdField.key"
                  :label="`${stdField.label} ${stdField.required ? '(必填)' : ''}`"
                  :value="stdField.key"
                >
                  <span>{{ stdField.label }}</span>
                  <el-tag v-if="stdField.required" type="danger" size="small" style="margin-left: 8px;">必填</el-tag>
                </el-option>
                <el-option :label="`保持原样: ${field}`" :value="field" />
              </el-select>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 数据预览表格 -->
      <el-card shadow="never">
        <template #header>
          <strong>👁️ 数据预览 (前 {{ previewData.length }} 条)</strong>
        </template>
        <el-table
          :data="previewData"
          border
          stripe
          max-height="400"
          style="width: 100%;"
        >
          <el-table-column
            v-for="field in detectedFields"
            :key="field"
            :prop="field"
            :label="field"
            min-width="120"
            show-overflow-tooltip
          >
            <template #header>
              <div>
                <div>{{ field }}</div>
                <el-tag size="small" type="info" effect="plain" style="margin-top: 4px;">
                  → {{ fieldMapping[field] || field }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 统计信息 -->
      <el-card shadow="never" style="margin-top: 16px;" v-if="qualityReport">
        <template #header>
          <strong>📊 数据统计</strong>
        </template>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="总记录数">
            {{ qualityReport.total }} 条
          </el-descriptions-item>
          <el-descriptions-item
            v-for="(stat, field) in qualityReport.statistics"
            :key="field"
            :label="field"
          >
            <div v-if="stat.min !== undefined">
              范围: {{ stat.min.toFixed(2) }} ~ {{ stat.max.toFixed(2) }}<br>
              平均: {{ stat.avg.toFixed(2) }}
            </div>
            <div v-else>
              空值: {{ stat.nullCount }} ({{ stat.nullRate }}%)
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <template #footer>
        <el-button @click="showFieldMapping = false">取消</el-button>
        <el-button
          type="primary"
          @click="confirmImportWithMapping"
          :disabled="qualityReport && qualityReport.issues.length > 0"
        >
          <el-icon style="margin-right: 6px;"><Check /></el-icon>
          确认导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 列显示管理对话框 -->
    <el-dialog
      v-model="showColumnManager"
      title="⚙️ 列显示管理"
      width="500px"
    >
      <div style="padding: 12px 0;">
        <el-checkbox-group v-model="visibleColumnsList">
          <el-row :gutter="12">
            <el-col :span="12" v-for="col in Object.keys(visibleColumns)" :key="col" style="margin-bottom: 12px;">
              <el-checkbox :label="col" border size="large">{{ col }}</el-checkbox>
            </el-col>
          </el-row>
        </el-checkbox-group>
      </div>
      <template #footer>
        <el-button @click="showColumnManager = false">关闭</el-button>
        <el-button type="primary" @click="applyColumnSettings">应用</el-button>
      </template>
    </el-dialog>

    <!-- 数据统计图表对话框 -->
    <el-dialog
      v-model="showStatsChart"
      title="📈 数据统计分析"
      width="900px"
      class="stats-chart-dialog"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>
              <strong>岩性分布</strong>
            </template>
            <div style="text-align: center; padding: 20px;">
              <el-tag
                v-for="lithology in uniqueLithologies"
                :key="lithology"
                :type="getLithologyColor(lithology)"
                size="large"
                style="margin: 6px;"
              >
                {{ lithology }}: {{ globalDataStore.keyStratumData.filter(r => r['岩层'] === lithology).length }} 条
              </el-tag>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>
              <strong>数据质量概览</strong>
            </template>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="总记录数">
                {{ globalDataStore.keyStratumData.length }} 条
              </el-descriptions-item>
              <el-descriptions-item label="钻孔数量">
                {{ statistics.boreholeCount }} 个
              </el-descriptions-item>
              <el-descriptions-item label="煤层记录">
                {{ statistics.coalSeamCount }} 条
              </el-descriptions-item>
              <el-descriptions-item label="平均厚度">
                {{ averageThickness.toFixed(2) }} m
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
      <template #footer>
        <el-button @click="showStatsChart = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 历史记录详情对话框 -->
    <el-dialog
      v-model="showHistoryDetail"
      title="📜 导入历史详情"
      width="700px"
      class="history-detail-dialog"
    >
      <div v-if="currentHistoryItem" style="padding: 12px 0;">
        <el-descriptions :column="2" border size="large">
          <el-descriptions-item label="导入时间">
            {{ formatDate(currentHistoryItem.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="数据来源">
            <el-tag type="success">{{ currentHistoryItem.source }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="记录数量">
            <el-tag type="info">{{ currentHistoryItem.recordCount }} 条</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="操作类型">
            <el-tag>{{ currentHistoryItem.operation || '导入' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="文件名" :span="2">
            {{ currentHistoryItem.fileName || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="导入说明" :span="2">
            {{ currentHistoryItem.description || '批量导入钻孔数据' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">数据变更摘要</el-divider>
        <el-alert
          v-if="currentHistoryItem.changes"
          type="info"
          :closable="false"
          show-icon
        >
          <template #title>
            <strong>检测到 {{ currentHistoryItem.changes }} 处数据变更</strong>
          </template>
          <ul style="margin: 8px 0 0 20px; padding: 0;">
            <li v-if="currentHistoryItem.added">新增记录: {{ currentHistoryItem.added }} 条</li>
            <li v-if="currentHistoryItem.updated">更新记录: {{ currentHistoryItem.updated }} 条</li>
            <li v-if="currentHistoryItem.deleted">删除记录: {{ currentHistoryItem.deleted }} 条</li>
          </ul>
        </el-alert>
        <el-empty v-else description="暂无变更记录" :image-size="60" />

        <el-divider content-position="left">操作日志</el-divider>
        <el-timeline>
          <el-timeline-item
            v-for="(log, idx) in (currentHistoryItem.logs || [])"
            :key="idx"
            :timestamp="log.time"
            :type="log.level === 'error' ? 'danger' : log.level === 'warning' ? 'warning' : 'primary'"
          >
            {{ log.message }}
          </el-timeline-item>
          <el-timeline-item v-if="!currentHistoryItem.logs || !currentHistoryItem.logs.length" type="info">
            无详细日志记录
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <el-button @click="showHistoryDetail = false">关闭</el-button>
        <el-button type="primary" @click="handleRollback(currentHistoryItem.id); showHistoryDetail = false">
          <el-icon style="margin-right: 6px;"><RefreshLeft /></el-icon>
          回滚到此版本
        </el-button>
      </template>
    </el-dialog>

    <!-- 数据详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="📊 数据详情"
      width="700px"
      class="detail-dialog"
    >
      <el-descriptions :column="2" border size="large">
        <el-descriptions-item
          v-for="(value, key) in currentRow"
          :key="key"
          :label="key"
        >
          {{ value }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  UploadFilled, QuestionFilled, DataLine, Collection, 
  OfficeBuilding, Files, Download, VideoPlay, Upload, 
  Document, Check, Loading, List, Delete, DataAnalysis, 
  Setting, Search, Refresh, Timer, RefreshLeft, RefreshRight, View
} from '@element-plus/icons-vue'
import { useGlobalDataStore } from '@/stores/globalData'

// 初始化store
const globalDataStore = useGlobalDataStore()

// 响应式数据
const loading = ref(false)
const boreholeData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const selectedLithology = ref('')
const detailDialogVisible = ref(false)
const currentRow = ref({})
const uploadRef = ref(null)
// const statsRef = ref(null)
const tableRef = ref(null)
const historyRef = ref(null)
const fileList = ref([])

// 导入进度相关
const importing = ref(false)
const importProgress = ref(0)
const importStatus = ref('')
const importMessage = ref('')
const importStep = ref(0) // 当前导入步骤 (0-3)

// 智能导入相关状态
const showFieldMapping = ref(false)
const detectedFields = ref([])
const fieldMapping = ref({})
const previewData = ref([])
const qualityReport = ref(null)
const showConceptDialog = ref(false)

// 列管理和批量操作
const visibleColumns = ref({
  '钻孔名': true,
  '岩层': true,
  '厚度/m': true,
  '弹性模量/GPa': true,
  '容重/kN·m-3': true,
  '抗拉强度/MPa': true,
  '泊松比': true,
  '数据来源': true
})
const selectedRows = ref([])
const showColumnManager = ref(false)
const showStatsChart = ref(false)
const showHistoryDetail = ref(false)
const currentHistoryItem = ref(null)

// ── 目标字段与自动映射 ──
// const targetFields = ['钻孔名', '岩层', '厚度/m', '弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa', '泊松比', '数据来源']

const STANDARD_FIELDS = [
  { key: '钻孔名', label: '钻孔名', aliases: ['钻孔', '孔号', 'borehole', 'hole'], required: false },
  { key: '岩层', label: '岩层', aliases: ['岩性', 'lithology', 'rock', '名称', 'name'], required: true },
  { key: '厚度/m', label: '厚度/m', aliases: ['厚度', 'thickness', 'h'], required: true },
  { key: '弹性模量/GPa', label: '弹性模量/GPa', aliases: ['弹性模量', 'E', 'modulus'], required: false },
  { key: '容重/kN·m-3', label: '容重/kN·m-3', aliases: ['容重', 'density', 'γ'], required: false },
  { key: '抗拉强度/MPa', label: '抗拉强度/MPa', aliases: ['抗拉', 'tensile'], required: false },
  { key: '泊松比', label: '泊松比', aliases: ['泊松', 'poisson', 'ν'], required: false },
  { key: '数据来源', label: '数据来源', aliases: ['来源', 'source'], required: false }
]

const autoMapFields = (headers) => {
  const mapping = {}
  headers.forEach(header => {
    const normalized = header.toLowerCase().trim()
    for (const field of STANDARD_FIELDS) {
      if (header === field.key || header === field.label) { mapping[header] = field.key; return }
      for (const alias of field.aliases) {
        if (normalized.includes(alias.toLowerCase())) { mapping[header] = field.key; return }
      }
    }
    mapping[header] = header
  })
  return mapping
}

// 数据质量检查
const checkDataQuality = (data, headers) => {
  const report = {
    total: data.length,
    issues: [],
    warnings: [],
    statistics: {}
  }
  
  // 检查必填字段（钻孔名除外，因为会从文件名自动提取）
  const requiredFields = STANDARD_FIELDS.filter(f => f.required && f.key !== '钻孔名').map(f => f.key)
  const missingRequired = requiredFields.filter(field => !headers.includes(field))
  
  if (missingRequired.length > 0) {
    // 仅作为警告，不阻止导入
    report.warnings.push({
      type: 'missing_required',
      message: `缺少推荐字段: ${missingRequired.join(', ')} (可在导入后手动补充或映射)`,
      severity: 'info'  // 降级为信息级别
    })
  }
  
  // 检查空值
  headers.forEach(header => {
    const nullCount = data.filter(row => !row[header] || row[header] === '').length
    const nullRate = (nullCount / data.length * 100).toFixed(1)
    
    report.statistics[header] = {
      nullCount,
      nullRate: parseFloat(nullRate)
    }
    
    if (nullRate > 50) {
      report.warnings.push({
        type: 'high_null_rate',
        message: `字段 "${header}" 空值率过高 (${nullRate}%)`,
        severity: 'warning',
        field: header
      })
    }
  })
  
  // 检查数值字段范围
  const numericFields = ['厚度/m', '弹性模量/GPa', '容重/kN·m-3', '抗拉强度/MPa', '泊松比']
  numericFields.forEach(field => {
    if (!headers.includes(field)) return
    
    const values = data.map(row => parseFloat(row[field])).filter(v => !isNaN(v))
    if (values.length === 0) return
    
    const min = Math.min(...values)
    const max = Math.max(...values)
    const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)
    
    report.statistics[field] = {
      ...report.statistics[field],
      min,
      max,
      avg: parseFloat(avg)
    }
    
    // 异常值检测
    if (field === '厚度/m' && (min < 0 || max > 1000)) {
      report.warnings.push({
        type: 'abnormal_value',
        message: `"${field}" 存在异常值 (范围: ${min.toFixed(2)} ~ ${max.toFixed(2)} m)`,
        severity: 'warning',
        field
      })
    }
    
    if (field === '泊松比' && (min < 0 || max > 0.5)) {
      report.warnings.push({
        type: 'abnormal_value',
        message: `"${field}" 超出合理范围 (范围: ${min.toFixed(2)} ~ ${max.toFixed(2)})`,
        severity: 'warning',
        field
      })
    }
  })
  
  return report
}

const downloadSampleCSV = () => {
  const headers = ['钻孔名','岩层','厚度/m','弹性模量/GPa','容重/kN·m-3','抗拉强度/MPa','泊松比','数据来源']
  const rows = [
    ['BK-1', '泥岩', '12.5', '15.2', '26.5', '4.2', '0.25', '钻孔数据'],
    ['BK-1', '砂岩', '8.4', '22.1', '27.2', '8.5', '0.21', '钻孔数据'],
    ['BK-1', '煤层', '3.5', '10.5', '14.2', '2.1', '0.32', '钻孔数据']
  ]
  
  const csvContent = '\uFEFF' + [ // 添加BOM防止乱码
    headers.join(','),
    ...rows.map(r => r.join(','))
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'sample_data_template.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  ElMessage.success('示例CSV模板已下载')
}

const loadExampleData = async () => {
  loading.value = true
  try {
    // 生成若干示例记录
    const cols = ['钻孔名','岩层','厚度/m','弹性模量/GPa','容重/kN·m-3','抗拉强度/MPa','泊松比','数据来源']
    const records = []
    for (let i = 1; i <= 30; i++) {
      records.push({
        '钻孔名': `示例孔_${i}`,
        '岩层': i % 3 === 0 ? '煤层' : (i % 3 === 1 ? '砂岩' : '泥岩'),
        '厚度/m': (2 + (i % 8)).toFixed(2),
        '弹性模量/GPa': (10 + (i % 5)).toFixed(2),
        '容重/kN·m-3': (25 + (i % 4)).toFixed(2),
        '抗拉强度/MPa': (5 + (i % 6)).toFixed(2),
        '泊松比': (0.2 + (i % 10) * 0.01).toFixed(2),
        '数据来源': '示例数据'
      })
    }

    // 使用 store 的加载函数
    await globalDataStore.loadKeyStratumData(records, cols)
    // 保存到历史（模拟）
    // store 内部会记录 last updated, 我们这里直接刷新界面
    await refreshData()
    ElMessage.success('已加载 30 条示例数据，开始体验吧！')
  } catch (err) {
    console.error('加载示例数据失败', err)
    ElMessage.error('加载示例数据失败: ' + err.message)
  } finally {
    loading.value = false
  }
}





// 重置字段映射为智能识别结果
const resetFieldMapping = () => {
  if (detectedFields.value.length > 0) {
    fieldMapping.value = autoMapFields(detectedFields.value)
    ElMessage.success('已重置为智能识别的字段映射')
  }
}

// 确认导入（应用字段映射）
const confirmImportWithMapping = async () => {
  try {
    // 应用字段映射转换预览数据
    // eslint-disable-next-line no-unused-vars
    const mappedData = previewData.value.map(row => {
      const newRow = {}
      Object.keys(row).forEach(oldKey => {
        const newKey = fieldMapping.value[oldKey] || oldKey
        newRow[newKey] = row[oldKey]
      })
      return newRow
    })
    
    // 提取映射后的列名
    const mappedHeaders = Object.values(fieldMapping.value)
    
    // 验证必填字段
    const requiredFields = STANDARD_FIELDS.filter(f => f.required).map(f => f.key)
    const missingRequired = requiredFields.filter(field => !mappedHeaders.includes(field))
    
    if (missingRequired.length > 0) {
      ElMessage.error(`缺少必填字段: ${missingRequired.join(', ')}`)
      return
    }
    
    // 关闭预览对话框
    showFieldMapping.value = false
    
    // 继续正常的批量导入流程
    await batchImportFiles()
    
  } catch (error) {
    console.error('字段映射确认失败:', error)
    ElMessage.error('字段映射确认失败: ' + error.message)
  }
}

// 批量删除选中行
const batchDeleteRows = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条数据吗？此操作不可撤销。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 从全局数据中移除选中行
    const selectedIds = new Set(selectedRows.value.map(r => JSON.stringify(r)))
    const newData = globalDataStore.keyStratumData.filter(row => {
      return !selectedIds.has(JSON.stringify(row))
    })
    
    await globalDataStore.loadKeyStratumData(newData, Object.keys(newData[0] || {}))
    selectedRows.value = []
    
    ElMessage.success(`已删除 ${selectedIds.size} 条数据`)
    await refreshData()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败: ' + error.message)
    }
  }
}

// 表格选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 计算属性
const statistics = computed(() => {
  return {
    boreholeCount: globalDataStore.keyStratumData.length,
    coalSeamCount: globalDataStore.keyStratumData.filter(row => 
      row['岩层'] && row['岩层'].includes('煤')
    ).length,
    uniqueMines: new Set(globalDataStore.keyStratumData.map(row => row['钻孔名'])).size,
    totalRecords: globalDataStore.keyStratumData.length
  }
})

const uniqueLithologies = computed(() => {
  const lithologies = new Set()
  globalDataStore.keyStratumData.forEach(row => {
    if (row['岩层']) {
      lithologies.add(row['岩层'])
    }
  })
  return Array.from(lithologies)
})

const filteredData = computed(() => {
  let result = globalDataStore.keyStratumData

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(row => {
      return Object.values(row).some(value =>
        value && value.toString().toLowerCase().includes(query)
      )
    })
  }

  // 岩性过滤
  if (selectedLithology.value) {
    result = result.filter(row => 
      row['岩层'] && row['岩层'].includes(selectedLithology.value)
    )
  }

  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 平均厚度计算
const averageThickness = computed(() => {
  const thicknesses = globalDataStore.keyStratumData
    .map(row => parseFloat(row['厚度/m']))
    .filter(v => !isNaN(v))
  
  if (thicknesses.length === 0) return 0
  return thicknesses.reduce((a, b) => a + b, 0) / thicknesses.length
})

// 列显示列表（用于checkbox-group）
const visibleColumnsList = computed({
  get: () => Object.keys(visibleColumns.value).filter(k => visibleColumns.value[k]),
  set: (val) => {
    Object.keys(visibleColumns.value).forEach(k => {
      visibleColumns.value[k] = val.includes(k)
    })
  }
})

// 应用列设置
const applyColumnSettings = () => {
  showColumnManager.value = false
  ElMessage.success('列显示设置已应用')
}

// 文件选择处理（带实时预览）
const handleFileChange = async (file, files) => {
  // 验证文件类型
  const isCSV = file.name.endsWith('.csv') || file.raw?.type === 'text/csv'
  if (!isCSV) {
    ElMessage.error(`文件 ${file.name} 不是CSV格式！`)
    files.splice(files.indexOf(file), 1)
    return false
  }

  // 验证文件大小
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error(`文件 ${file.name} 超过10MB！`)
    files.splice(files.indexOf(file), 1)
    return false
  }

  fileList.value = files
  
  // 实时预览第一个文件
  if (files.length === 1) {
    await previewFile(file.raw)
  }
}

// 预览文件内容
const previewFile = async (file) => {
  try {
    const text = await file.text()
    const lines = text.split('\n').filter(line => line.trim())
    
    if (lines.length === 0) {
      ElMessage.warning('文件为空')
      return
    }
    
    // 解析CSV（简单处理，实际生产环境建议使用Papa Parse等库）
    const parseCSVLine = (line) => {
      const result = []
      let current = ''
      let inQuotes = false
      
      for (let i = 0; i < line.length; i++) {
        const char = line[i]
        if (char === '"') {
          inQuotes = !inQuotes
        } else if (char === ',' && !inQuotes) {
          result.push(current.trim())
          current = ''
        } else {
          current += char
        }
      }
      result.push(current.trim())
      return result
    }
    
    const headers = parseCSVLine(lines[0])
    const dataLines = lines.slice(1, Math.min(11, lines.length)) // 预览前10行
    
    const preview = dataLines.map(line => {
      const values = parseCSVLine(line)
      const row = {}
      headers.forEach((header, index) => {
        row[header] = values[index] || ''
      })
      return row
    })
    
    // 智能字段映射
    const mapping = autoMapFields(headers)
    fieldMapping.value = mapping
    detectedFields.value = headers
    previewData.value = preview
    
    // 数据质量检查
    qualityReport.value = checkDataQuality(preview, headers)
    
    // 显示预览对话框
    showFieldMapping.value = true
    
    // 提示用户
    ElMessage.success({
      message: `已预览 ${preview.length} 条数据，检测到 ${headers.length} 个字段`,
      duration: 2000
    })
    
  } catch (error) {
    console.error('文件预览失败:', error)
    ElMessage.error('文件预览失败: ' + error.message)
  }
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

// 批量导入文件（细化步骤）
const batchImportFiles = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要导入的CSV文件')
    return
  }

  importing.value = true
  importProgress.value = 0
  importStep.value = 0
  importStatus.value = ''
  loading.value = true

  try {
    // 步骤1: 上传文件
    importStep.value = 1
    importMessage.value = `正在上传 ${fileList.value.length} 个文件...`
    importProgress.value = 10
    
    const formData = new FormData()
    fileList.value.forEach((fileWrapper) => {
      formData.append('files', fileWrapper.raw)
    })
    
    await new Promise(resolve => setTimeout(resolve, 300)) // 模拟上传延迟
    
    // 步骤2: 解析数据
    importStep.value = 2
    importMessage.value = '正在解析文件内容...'
    importProgress.value = 30

    const result = await globalDataStore.importRawFiles(formData)
    
    // 步骤3: 验证质量
    importStep.value = 3
    importMessage.value = '正在验证数据质量...'
    importProgress.value = 60
    
    await new Promise(resolve => setTimeout(resolve, 200))
    importProgress.value = 80

    if (result && result.status === 'success') {
      // 步骤4: 导入完成
      importStep.value = 4
      importProgress.value = 100
      importStatus.value = 'success'
      importMessage.value = `✅ 导入成功！共处理 ${result.valid_count}/${result.file_count} 个文件，${result.record_count} 条记录`

      if (result.errors && result.errors.length > 0) {
        console.warn('导入时发生的错误:', result.errors)
        ElMessage.warning({
          message: `部分文件导入失败，成功: ${result.valid_count}/${result.file_count}`,
          description: '💡 建议检查文件格式是否符合模板要求',
          duration: 5000,
          showClose: true
        })
      } else {
        showSuccessWithDetails(
          `成功导入 ${result.record_count} 条记录`,
          `📊 钻孔数据已加载到系统，可在各功能模块中使用`
        )
      }

      // 清空文件列表
      fileList.value = []
      if (uploadRef.value && uploadRef.value.$refs && uploadRef.value.$refs.uploadRefInner) {
        uploadRef.value.$refs.uploadRefInner.clearFiles()
      }

        // 刷新显示
        await refreshData()
      } else {
        throw new Error((result && result.message) || '导入失败')
      }
    } catch (error) {
      console.error('批量导入失败:', error)
      importProgress.value = 100
      importStatus.value = 'exception'
      importMessage.value = '导入失败: ' + (error.message || error)
      ElMessage.error('批量导入失败: ' + (error.message || error))
    } finally {
      loading.value = false
      setTimeout(() => {
        importing.value = false
      }, 2000)
    }
}

// 从数据库加载
// eslint-disable-next-line no-unused-vars
const importFromDatabase = async () => {
  loading.value = true
  try {
    const result = await globalDataStore.loadFromDatabase(1, 10000)
    if (result && result.status === 'success') {
      ElMessage.success(`从数据库加载 ${result.total || globalDataStore.keyStratumData.length} 条记录`)
      await refreshData()
    } else {
      throw new Error((result && result.message) || '加载失败')
    }
  } catch (error) {
    console.error('从数据库加载失败:', error)
    ElMessage.error('从数据库加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  // 直接从全局存储刷新显示
  boreholeData.value = globalDataStore.keyStratumData
  currentPage.value = 1
}

const clearAllData = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有全局数据吗？此操作不可恢复！',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    globalDataStore.clearKeyStratumData()
    boreholeData.value = []
    fileList.value = []
    if (uploadRef.value) {
      uploadRef.value.clearFiles()
    }
    currentPage.value = 1
    ElMessage.success('全局数据已清空！')
  } catch {
    // 用户取消操作
  }
}

const viewDetails = (row) => {
  currentRow.value = row
  detailDialogVisible.value = true
}

// 历史记录操作
const handleRollback = async (historyId) => {
  try {
    await ElMessageBox.confirm(
      '确定要回滚到此历史版本吗？当前数据将被替换！',
      '确认回滚',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const snapshot = globalDataStore.rollbackToHistory(historyId)
    await refreshData()
    ElMessage.success(`已回滚到 ${snapshot.timestamp} 的数据 (${snapshot.recordCount} 条记录)`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('回滚失败: ' + error.message)
    }
  }
}

const handleDeleteHistory = async (historyId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条历史记录吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    globalDataStore.deleteHistoryItem(historyId)
    ElMessage.success('历史记录已删除')
  } catch {
    // 用户取消操作
  }
}

const handleClearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有历史记录吗？',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    globalDataStore.clearHistory()
    ElMessage.success('历史记录已清空')
  } catch {
    // 用户取消操作
  }
}

// 导出全局数据为CSV
const exportGlobalData = () => {
  if (!hasGlobalData.value) {
    ElMessage.warning('暂无数据可导出')
    return
  }

  try {
    const data = globalDataStore.keyStratumData
    const cols = globalDataStore.keyStratumColumns

    if (!cols.length || !data.length) {
      ElMessage.warning('暂无数据可导出')
      return
    }

    // 构建CSV内容
    const csvContent = '\uFEFF' + [ // 添加BOM防止乱码
      cols.join(','),
      ...data.map(row => cols.map(col => row[col] || '').join(','))
    ].join('\n')

    // 下载
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `global_data_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + error.message)
  }
}

// 岩层颜色映射
const getLithologyColor = (lithology) => {
  if (!lithology) return ''
  if (lithology.includes('煤')) return 'success'
  if (lithology.includes('砂')) return 'warning'
  if (lithology.includes('泥')) return 'info'
  return ''
}

// 时间格式化
const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 计算属性 - hasGlobalData
const hasGlobalData = computed(() => {
  return globalDataStore.keyStratumData && globalDataStore.keyStratumData.length > 0
})

// 查看历史详情
const viewHistoryDetail = (item) => {
  currentHistoryItem.value = item
  showHistoryDetail.value = true
}

// 改进的错误处理 - 带解决方案提示
// eslint-disable-next-line no-unused-vars
const handleError = (error, context = '操作') => {
  console.error(`${context}失败:`, error)
  
  let solution = ''
  const errorMsg = error.message || error.toString()
  
  // 根据错误类型提供解决方案
  if (errorMsg.includes('Network') || errorMsg.includes('网络')) {
    solution = '请检查网络连接后重试'
  } else if (errorMsg.includes('timeout') || errorMsg.includes('超时')) {
    solution = '服务器响应超时，请稍后重试'
  } else if (errorMsg.includes('CSV') || errorMsg.includes('格式')) {
    solution = '请确保文件格式正确，建议下载模板参考'
  } else if (errorMsg.includes('权限') || errorMsg.includes('Permission')) {
    solution = '权限不足，请联系管理员'
  } else {
    solution = '如问题持续，请联系技术支持'
  }
  
  ElMessage({
    type: 'error',
    message: `${context}失败: ${errorMsg}`,
    description: `💡 解决方案: ${solution}`,
    duration: 5000,
    showClose: true
  })
}

// 改进的成功提示 - 带详细信息
const showSuccessWithDetails = (message, details = null) => {
  ElMessage({
    type: 'success',
    message: message,
    description: details,
    duration: 3000,
    showClose: true
  })
}

// eslint-disable-next-line no-unused-vars
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

// eslint-disable-next-line no-unused-vars
const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 初始化
onMounted(() => {
  refreshData()
  
  // 快捷键支持
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// 快捷键处理
const handleKeydown = (e) => {
  // Ctrl/Cmd + S: 导出数据
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    if (hasGlobalData.value) {
      exportGlobalData()
    }
  }
  
  // Ctrl/Cmd + U: 打开上传
  if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
    e.preventDefault()
    if (uploadRef.value && uploadRef.value.$el) {
      uploadRef.value.$el.querySelector('.el-upload')?.click()
    }
  }
  
  // Ctrl/Cmd + D: 下载模板
  if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
    e.preventDefault()
    downloadSampleCSV()
  }
  
  // F1: 显示帮助
  if (e.key === 'F1') {
    e.preventDefault()
    showConceptDialog.value = true
  }
  
  // Ctrl/Cmd + H: 显示历史
  if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
    e.preventDefault()
    if (historyRef.value && historyRef.value.$el) {
      historyRef.value.$el.scrollIntoView({ behavior: 'smooth' })
    }
  }
}
</script>

<style scoped>
/* ========== 整体容器 ========== */
.data-management-container {
  padding: 20px;
  background-color: #f8fafc;
  min-height: 100vh;
}

/* ========== 欢迎横幅 ========== */
.welcome-banner {
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
  color: white;
  margin-bottom: 20px;
  border: none;
}

.welcome-banner :deep(.el-card__body) {
  padding: 24px 32px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.feature-badges {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.feature-badges .el-tag {
  font-size: 13px;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

/* ========== 统计卡片 ========== */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  margin-right: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card-primary .stat-icon {
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
}

.stat-card-success .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-card-warning .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-card-info .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-text {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
  margin-bottom: 2px;
}

.stat-unit {
  font-size: 12px;
  color: #C0C4CC;
}

/* ========== 主内容区 ========== */
.main-content-row {
  margin-bottom: 20px;
}

/* 快捷操作横幅 */
.quick-actions-card {
  margin-bottom: 20px;
}

.quick-actions-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.banner-left h3 {
  margin: 0 0 6px 0;
  font-size: 18px;
  color: #0f172a;
}

.banner-left p {
  margin: 0;
  color: #475569;
  font-size: 14px;
}

.banner-actions {
  display: flex;
  gap: 12px;
}

/* 卡片头部 */
.card-header-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

/* ========== 上传区域 ========== */
.upload-card {
  margin-bottom: 20px;
}

.upload-wrapper {
  padding: 12px 0;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 40px 20px;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.upload-area :deep(.el-upload-dragger):hover {
  border-color: #059669;
  background-color: rgba(64, 158, 255, 0.05);
  transform: translateY(-2px);
}

.upload-text {
  text-align: center;
}

.upload-text strong {
  font-size: 16px;
  color: #0f172a;
}

.upload-text p {
  margin: 8px 0 0 0;
  font-size: 13px;
  color: #94a3b8;
}

.el-icon--upload {
  font-size: 64px;
  color: #059669;
  margin-bottom: 16px;
}

.upload-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 8px;
}

.file-count {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.progress-bar-wrapper {
  margin-top: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.progress-text {
  margin: 12px 0 0 0;
  text-align: center;
  font-size: 13px;
  color: #475569;
}

/* ========== 表格卡片 ========== */
.table-card {
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

/* ========== 历史记录卡片 ========== */
.history-card {
  margin-bottom: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.history-list {
  padding: 12px 0;
}

.history-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.history-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.history-actions {
  display: flex;
  gap: 8px;
}

/* 数据操作卡片 */
.operations-card {
}

.operation-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.operation-buttons .el-button {
  width: 100%;
  margin-left: 0;
}

/* ========== 对话框样式 ========== */
.concept-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
  color: white;
  padding: 20px;
}

.concept-dialog :deep(.el-dialog__title) {
  color: white;
  font-size: 20px;
}

.concept-content {
  padding: 20px;
}

.concept-section {
  margin-bottom: 24px;
}

.concept-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #0f172a;
}

.concept-section ul,
.concept-section ol {
  margin: 0;
  padding-left: 24px;
  line-height: 1.8;
}

.concept-section li {
  margin-bottom: 8px;
  color: #475569;
}

/* 字段映射对话框 */
.field-mapping-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
  color: white;
  padding: 20px;
}

.field-mapping-dialog :deep(.el-dialog__title) {
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.field-mapping-dialog :deep(.el-dialog__body) {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.field-mapping-dialog :deep(.el-card) {
  border: 1px solid #e2e8f0;
}

.field-mapping-dialog :deep(.el-card__header) {
  background: #f8fafc;
  padding: 12px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.field-mapping-dialog :deep(.el-steps) {
  padding: 0 40px;
}

.field-mapping-dialog :deep(.el-alert) {
  border-radius: 8px;
}

.field-mapping-dialog :deep(.el-table) {
  font-size: 13px;
}

.field-mapping-dialog :deep(.el-table th) {
  background: #f8fafc;
  font-weight: 600;
}

/* 列管理对话框 */
.column-manager-dialog :deep(.el-checkbox) {
  width: 100%;
}

.column-manager-dialog :deep(.el-checkbox.is-bordered) {
  padding: 10px 16px;
}

/* 统计图表对话框 */
.stats-chart-dialog :deep(.el-descriptions__label) {
  font-weight: 600;
  color: #475569;
}

.stats-chart-dialog :deep(.el-descriptions__content) {
  color: #0f172a;
}

/* 历史详情对话框 */
.history-detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
  color: white;
  padding: 20px;
}

.history-detail-dialog :deep(.el-dialog__title) {
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.history-detail-dialog :deep(.el-descriptions) {
  margin-bottom: 16px;
}

.history-detail-dialog :deep(.el-timeline) {
  padding-left: 8px;
}

.history-detail-dialog :deep(.el-alert) {
  border-radius: 8px;
}

/* 进度条增强 */
.progress-bar-wrapper {
  margin-top: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.05);
}

.progress-text {
  margin: 16px 0 0 0;
  text-align: center;
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.progress-text .is-loading {
  animation: rotate 1.5s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========== 新手引导覆盖层 ========== */
/* ========== 动画效果 ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
}

.stat-icon {
  animation: float 3s ease-in-out infinite;
}

.stat-card:nth-child(1) .stat-icon { animation-delay: 0s; }
.stat-card:nth-child(2) .stat-icon { animation-delay: 0.5s; }
.stat-card:nth-child(3) .stat-icon { animation-delay: 1s; }
.stat-card:nth-child(4) .stat-icon { animation-delay: 1.5s; }

/* ========== 响应式设计 ========== */
@media (max-width: 1200px) {
  .welcome-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .welcome-actions {
    width: 100%;
    justify-content: center;
  }
  
  .stats-row .el-col {
    flex: 0 0 50% !important;
    max-width: 50% !important;
    margin-bottom: 12px;
  }
}

@media (max-width: 768px) {
  .data-management-container {
    padding: 12px;
  }
  
  .welcome-banner h1 {
    font-size: 24px;
  }
  
  .welcome-banner p {
    font-size: 14px;
  }
  
  .feature-badges {
    flex-wrap: wrap;
  }
  
  .stats-row .el-col {
    flex: 0 0 100% !important;
    max-width: 100% !important;
  }
  
  .main-content-row .el-col {
    flex: 0 0 100% !important;
    max-width: 100% !important;
    margin-bottom: 20px;
  }
  
  .card-header-inline {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 12px;
  }
  
  .header-right {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .header-right .el-input,
  .header-right .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }
}

@media (max-width: 480px) {
  .welcome-banner h1 {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 24px !important;
  }
  
  .welcome-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .welcome-actions .el-button {
    width: 100%;
  }
}

/* ========== 无障碍支持 ========== */
/* 键盘焦点增强 */
*:focus-visible {
  outline: 2px solid #059669;
  outline-offset: 2px;
  border-radius: 4px;
}

.el-button:focus-visible,
.el-input:focus-visible,
.el-select:focus-visible {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .data-management-container {
    background-color: #ffffff;
  }
  
  .welcome-banner {
    background: #000000 !important;
    color: #ffffff !important;
    border: 2px solid #ffffff;
  }
  
  .stat-card {
    border: 2px solid #000000;
  }
  
  .el-button {
    border-width: 2px;
  }
}

/* 减少动画（用户偏好） */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  .stat-icon {
    animation: none;
  }
}

/* 暗黑模式支持 */
@media (prefers-color-scheme: dark) {
  .data-management-container {
    background-color: #1a1a1a;
    color: #e0e0e0;
  }
  
  .el-card {
    background-color: #1e293b;
    border-color: #3a3a3a;
  }
  
  .progress-bar-wrapper {
    background: linear-gradient(135deg, #1e293b 0%, #333333 100%);
  }
}

/* 屏幕阅读器专用文本 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* 触摸友好的按钮尺寸 */
@media (hover: none) and (pointer: coarse) {
  .el-button {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 20px;
  }
  
  .el-table {
    font-size: 14px;
  }
  
  .el-table th,
  .el-table td {
    padding: 12px 8px;
  }
}

/* 打印样式 */
@media print {
  .welcome-banner,
  .upload-card,
  .operations-card,
  .data-management-container {
    background: white;
  }
  
  .el-card {
    box-shadow: none;
    border: 1px solid #000;
  }
  
  .table-card {
    page-break-inside: avoid;
  }
}
</style>
