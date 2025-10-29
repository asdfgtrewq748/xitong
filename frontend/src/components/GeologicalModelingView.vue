<template>
  <div class="geo-modeling-container">
    <el-steps :active="step" finish-status="success" align-center style="margin-bottom: 20px;">
      <el-step title="数据加载" />
      <el-step title="参数选择" />
      <el-step title="建模与可视化" />
    </el-steps>
    <el-row :gutter="20" class="content-row">
      <el-col :span="6" class="panel-col">
        <div class="panel">
          <div v-show="step === 0" class="panel-step">
            <el-alert
              title="请准备钻孔数据与坐标文件"
              description="支持使用全局数据或上传新文件。坐标文件需包含相同的钻孔标识列"
              type="info"
              :closable="false"
              show-icon
            />
            
            <!-- 全局数据状态提示 -->
            <div v-if="globalDataStore.keyStratumData.length > 0" class="data-status-info">
              <el-icon class="status-icon"><CircleCheckFilled /></el-icon>
              <span class="status-text">全局数据已加载</span>
              <span class="status-count">({{ globalDataStore.keyStratumData.length }} 条)</span>
            </div>
            
            <!-- 数据源选择 -->
            <div class="data-source-selector">
              <el-radio-group v-model="useGlobalData" size="default">
                <el-radio-button :value="true">使用全局数据</el-radio-button>
                <el-radio-button :value="false">上传新文件</el-radio-button>
              </el-radio-group>
            </div>
            
            <!-- 统一说明 -->
            <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px;">
              <div style="font-size: 12px; line-height: 1.6;">
                <template v-if="useGlobalData">
                  <b>全局数据模式：</b>使用已导入的全局钻孔数据进行建模。
                  <span v-if="hasCoordinatesInGlobalData">数据已包含坐标信息，无需额外上传坐标文件。</span>
                  <span v-else>需要上传坐标文件进行数据合并。</span>
                </template>
                <template v-else>
                  <b>上传文件模式：</b>上传新的钻孔CSV文件和坐标CSV文件进行建模。两种模式的建模算法和效果完全一致。
                </template>
              </div>
            </el-alert>
            
            <!-- 钻孔数据选择 -->
            <div v-if="!useGlobalData" class="file-group">
              <div class="file-group__header">
                <h5>钻孔数据 (可多选)</h5>
                <el-button type="primary" plain size="small" @click="triggerBoreholeSelection">选择文件</el-button>
                <input ref="boreholeInput" class="hidden-input" type="file" accept=".csv" multiple @change="handleBoreholeFiles" />
              </div>
              <el-empty v-if="boreholeFiles.length === 0" description="未选择文件" :image-size="80" />
              <el-scrollbar v-else class="file-scroll">
                <ul class="file-list">
                  <li v-for="(file, idx) in boreholeFiles" :key="`${file.name}-${idx}`">
                    <span>{{ file.name }}</span>
                    <el-tag size="small" type="info" effect="plain">{{ formatFileSize(file.size) }}</el-tag>
                  </li>
                </ul>
              </el-scrollbar>
            </div>
            <div v-else class="file-group">
              <div class="file-group__header">
                <h5>钻孔数据来源</h5>
              </div>
              <div class="global-data-summary">
                <el-icon class="data-icon"><DataAnalysis /></el-icon>
                <div class="data-info">
                  <span class="data-label">全局钻孔数据</span>
                  <span class="data-count">{{ globalDataStore.keyStratumData.length }} 条记录</span>
                </div>
              </div>
            </div>
            
            <!-- 坐标文件 (条件必需) -->
            <div class="file-group">
              <div class="file-group__header">
                <h5>坐标文件 
                  <el-tag v-if="useGlobalData && hasCoordinatesInGlobalData" size="small" type="info">可选</el-tag>
                  <el-tag v-else size="small" type="danger">必需</el-tag>
                </h5>
                <el-button type="primary" plain size="small" @click="triggerCoordsSelection">选择文件</el-button>
                <input ref="coordsInput" class="hidden-input" type="file" accept=".csv" @change="handleCoordsFile" />
              </div>
              <div class="coords-summary">
                <span v-if="coordsFile">{{ coordsFile.name }} ({{ formatFileSize(coordsFile.size) }})</span>
                <span v-else-if="useGlobalData && hasCoordinatesInGlobalData" class="info-text">
                  全局数据已包含坐标信息
                </span>
                <span v-else class="muted">未选择文件</span>
              </div>
              <el-alert v-if="useGlobalData && hasCoordinatesInGlobalData && !coordsFile" 
                type="success" :closable="false" show-icon style="margin-top: 8px;">
                <div style="font-size: 11px;">
                  系统检测到全局数据已包含X、Y坐标信息，无需再上传坐标文件。
                </div>
              </el-alert>
            </div>
            
            <el-button type="primary" @click="loadAndMergeData" :loading="isLoading" class="full-width">
              加载并合并数据
            </el-button>
          </div>
          <div v-show="step === 1">
            <el-form label-position="top" :disabled="isLoading || columns.numeric.length === 0">
              <el-form-item label="X坐标"><el-select v-model="params.x_col" placeholder="选择X坐标列" style="width: 100%;"><el-option v-for="c in columns.numeric" :key="c" :label="c" :value="c"/></el-select></el-form-item>
              <el-form-item label="Y坐标"><el-select v-model="params.y_col" placeholder="选择Y坐标列" style="width: 100%;"><el-option v-for="c in columns.numeric" :key="c" :label="c" :value="c"/></el-select></el-form-item>
              <el-form-item label="Z值/厚度"><el-select v-model="params.thickness_col" placeholder="选择厚度/Z值列" style="width: 100%;"><el-option v-for="c in columns.numeric" :key="c" :label="c" :value="c"/></el-select></el-form-item>
              <el-form-item label="岩层列"><el-select v-model="params.seam_col" @change="updateSeamList" placeholder="选择岩层列" style="width: 100%;"><el-option v-for="c in columns.text" :key="c" :label="c" :value="c"/></el-select></el-form-item>
            </el-form>
            <div v-if="availableSeams.length > 0">
              <h5>选择建模岩层 (可多选)</h5>
              <el-alert type="warning" :closable="false" show-icon style="margin-bottom: 8px;">
                <div style="font-size: 11px;">
                  <b>重要提示：</b>岩层将按照列表顺序从下到上堆叠建模。<br/>
                  • 如果数据包含"序号"列，系统已自动按序号排序<br/>
                  • 请确保第一个岩层是最底层，最后一个是最顶层<br/>
                  • 可通过拖拽调整顺序（如果需要）
                </div>
              </el-alert>
              <el-select v-model="params.selected_seams" multiple placeholder="选择岩层" style="width: 100%;"><el-option v-for="s in availableSeams" :key="s" :label="s" :value="s"/></el-select>
            </div>
            <el-button type="primary" @click="step = 2" :disabled="!canProceedToModeling" class="full-width">下一步</el-button>
            <el-button text type="info" @click="step = 0" class="full-width">重新选择文件</el-button>
          </div>
          <div v-show="step === 2">
            <el-form label-position="top">
              <el-form-item label="插值方法">
                <el-select v-model="params.method" style="width: 100%;">
                  <el-option v-for="(name, key) in interpolationMethods" :key="key" :label="name" :value="key" />
                </el-select>
              </el-form-item>
              <el-divider content-position="left">高级参数</el-divider>
              <el-form-item label="网格分辨率">
                <el-input-number v-model="params.resolution" :min="20" :max="200" :step="10" style="width: 100%;" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px;">分辨率越高，模型越精细，但计算时间更长</div>
              </el-form-item>
              <el-form-item label="首层基底高程 (m)">
                <el-input-number v-model="params.base_level" :step="0.5" style="width: 100%;" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px;">最底层岩层的底面高程基准值</div>
              </el-form-item>
              <el-form-item label="层间可视化间隔 (m)">
                <el-input-number v-model="params.gap" :min="0" :step="0.1" style="width: 100%;" />
                <div style="font-size: 12px; color: #909399; margin-top: 4px;">用于3D可视化时各层之间的间距,不影响实际厚度</div>
              </el-form-item>
              
              <!-- 建模顺序说明 -->
              <el-alert type="info" :closable="false" style="margin-top: 8px;">
                <template #title>
                  <div style="font-size: 13px; font-weight: 500;">建模顺序说明</div>
                </template>
                <div style="font-size: 12px; line-height: 1.6;">
                  • 岩层按<b>列表顺序从下到上</b>依次堆叠<br/>
                  • 第1层（列表第一个）：底面 = 基底高程，顶面 = 底面 + 厚度<br/>
                  • 第2层开始：底面 = 上一层顶面 + 间隔，顶面 = 底面 + 厚度<br/>
                  • 如有"序号"列，已自动按序号排序（从小到大）<br/>
                  • <span style="color: #e6a23c;">煤层自动显示为黑色</span><br/>
                  • <span style="color: #409eff;">相同名称岩层使用相同颜色</span>
                </div>
              </el-alert>
            </el-form>
            <el-row :gutter="10" style="margin-bottom: 10px;">
              <el-col :span="12">
                <el-button type="success" @click="generateContour" :loading="isLoading" :disabled="!params.thickness_col" class="full-width">生成 2D 等值线图</el-button>
              </el-col>
              <el-col :span="12">
                <el-button type="success" @click="generate3DModel" :loading="isLoading" :disabled="params.selected_seams.length === 0" class="full-width">生成 3D 块体模型</el-button>
              </el-col>
            </el-row>
            
            <!-- 剖面图按钮 - 显眼位置 -->
            <div v-if="current3DModel && current3DModel.type !== '2D'">
              <el-button type="warning" @click="showCrossSectionDialog" class="full-width" style="margin-bottom: 12px;">
                <el-icon style="margin-right: 4px;"><Grid /></el-icon>
                查看地质剖面图
              </el-button>
            </div>
            
            <!-- 导出按钮 (适用于2D和3D) -->
            <div v-if="current3DModel">
              <el-button type="primary" @click="exportModel" class="full-width" :loading="isExporting" style="margin-bottom: 12px;">
                <el-icon style="margin-right: 4px;"><Download /></el-icon>
                导出当前图表
              </el-button>
            </div>
            
            <!-- 3D视图控制 (仅在3D模型生成后显示) -->
            <div v-if="current3DModel && current3DModel.type !== '2D'">
              <el-divider content-position="left">3D 视图控制</el-divider>
              <el-form label-position="top">
                <el-form-item label="视图距离">
                  <el-slider v-model="viewControl.distance" :min="80" :max="300" @input="update3DView" />
                </el-form-item>
                <el-form-item label="俯仰角度 (α)">
                  <el-slider v-model="viewControl.alpha" :min="-90" :max="90" @input="update3DView" />
                </el-form-item>
                <el-form-item label="旋转角度 (β)">
                  <el-slider v-model="viewControl.beta" :min="-180" :max="180" @input="update3DView" />
                </el-form-item>
                <el-form-item>
                  <el-checkbox v-model="viewControl.autoRotate" @change="update3DView">自动旋转</el-checkbox>
                </el-form-item>
              </el-form>
              
              <el-divider content-position="left">渲染选项</el-divider>
              <el-form label-position="top" size="small">
                <el-form-item label="着色模式">
                  <el-select v-model="renderOptions.shadingMode" @change="update3DView" class="full-width">
                    <el-option label="真实感 (Realistic)" value="realistic" />
                    <el-option label="朗伯 (Lambert)" value="lambert" />
                    <el-option label="纯色 (Color)" value="color" />
                  </el-select>
                </el-form-item>
                <el-form-item label="光照强度">
                  <el-slider v-model="renderOptions.lightIntensity" :min="0.5" :max="3" :step="0.1" @input="update3DView" />
                </el-form-item>
                <el-form-item label="环境光强度">
                  <el-slider v-model="renderOptions.ambientIntensity" :min="0.2" :max="1.5" :step="0.1" @input="update3DView" />
                </el-form-item>
                <el-form-item label="阴影质量">
                  <el-select v-model="renderOptions.shadowQuality" @change="update3DView" class="full-width">
                    <el-option label="低" value="low" />
                    <el-option label="中" value="medium" />
                    <el-option label="高" value="high" />
                    <el-option label="超高" value="ultra" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-checkbox v-model="renderOptions.showWireframe" @change="update3DView">显示网格线</el-checkbox>
                </el-form-item>
                <el-form-item>
                  <el-checkbox v-model="renderOptions.showAxisPointer" @change="update3DView">显示坐标指示器</el-checkbox>
                </el-form-item>
              </el-form>
              
              <el-row :gutter="10" style="margin-bottom: 10px;">
                <el-col :span="12">
                  <el-button @click="resetView" size="small" class="full-width">重置视图</el-button>
                </el-col>
                <el-col :span="12">
                  <el-button @click="showLayerControl" size="small" class="full-width">图层控制</el-button>
                </el-col>
              </el-row>
            </div>
            
            <el-divider content-position="left">插值方法对比</el-divider>
            <el-form label-position="top">
              <el-form-item label="验证集比例 (%)">
                <el-slider v-model="params.validation_ratio" :min="10" :max="50" show-input></el-slider>
              </el-form-item>
            </el-form>
            <el-button type="warning" @click="runComparison" :loading="isLoading" :disabled="!params.thickness_col" class="full-width">
              对比所有插值方法
            </el-button>
            <el-button text type="info" @click="step = 1" class="full-width">返回列选择</el-button>
          </div>
        </div>
      </el-col>
      <el-col :span="18" class="chart-col">
        <div class="chart-container">
          <!-- 快捷工具栏 -->
          <div v-if="current3DModel && current3DModel.type !== '2D'" class="quick-toolbar">
            <el-tooltip content="重置视图" placement="bottom">
              <el-button circle size="small" @click="resetView">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="俯视图" placement="bottom">
              <el-button circle size="small" @click="setTopView">
                <el-icon><Top /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="侧视图" placement="bottom">
              <el-button circle size="small" @click="setSideView">
                <el-icon><Right /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="前视图" placement="bottom">
              <el-button circle size="small" @click="setFrontView">
                <el-icon><Back /></el-icon>
              </el-button>
            </el-tooltip>
            <el-divider direction="vertical" />
            <el-tooltip :content="viewControl.autoRotate ? '停止旋转' : '自动旋转'" placement="bottom">
              <el-button circle size="small" :type="viewControl.autoRotate ? 'primary' : ''" @click="toggleAutoRotate">
                <el-icon><VideoPlay /></el-icon>
              </el-button>
            </el-tooltip>
            <el-divider direction="vertical" />
            <el-tooltip content="截图" placement="bottom">
              <el-button circle size="small" @click="captureImage">
                <el-icon><Camera /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="全屏" placement="bottom">
              <el-button circle size="small" @click="toggleFullscreen">
                <el-icon><FullScreen /></el-icon>
              </el-button>
            </el-tooltip>
          </div>

          <!-- 模型统计信息面板 -->
          <div v-if="modelStats" class="stats-panel">
            <div class="stats-header">
              <h4>模型统计信息</h4>
              <el-button text @click="modelStats = null" size="small">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <el-row :gutter="12">
              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-label">岩层数量</div>
                  <div class="stat-value">{{ modelStats.layerCount }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-label">总数据点</div>
                  <div class="stat-value">{{ modelStats.totalPoints }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-item">
                  <div class="stat-label">模型体积</div>
                  <div class="stat-value">{{ modelStats.totalVolume.toFixed(2) }} m³</div>
                </div>
              </el-col>
            </el-row>
            <el-divider style="margin: 10px 0;" />
            <el-scrollbar style="max-height: 150px;">
              <div v-for="layer in modelStats.layers" :key="layer.name" class="layer-stat">
                <div class="layer-name">{{ layer.name }}</div>
                <div class="layer-details">
                  <span>厚度: {{ layer.avgThickness.toFixed(2) }}m ({{ layer.minThickness.toFixed(2) }} ~ {{ layer.maxThickness.toFixed(2) }}m)</span>
                  <span>点数: {{ layer.points }}</span>
                  <span>体积: {{ layer.volume.toFixed(2) }} m³</span>
                </div>
              </div>
            </el-scrollbar>
          </div>
          
          <div class="chart-wrapper" v-loading="isLoading" element-loading-text="正在计算和渲染模型...">
            <div v-show="chartMessage" class="chart-placeholder">{{ chartMessage }}</div>
            <div ref="chartRef" class="chart-canvas"></div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-dialog v-model="comparisonDialogVisible" title="插值方法对比结果" width="70%">
      <el-alert v-if="bestMethod" type="success" :closable="false" style="margin-bottom: 15px;">
        <b>推荐方法: {{ bestMethod.method }}</b> (R²: {{ bestMethod.r2 }}, RMSE: {{ bestMethod.rmse }})
      </el-alert>
      <el-table :data="comparisonResults" border stripe height="400px" :default-sort="{ prop: 'r2', order: 'descending' }">
        <el-table-column property="method" label="方法" width="180"/>
        <el-table-column property="r2" label="R² (决定系数)" sortable />
        <el-table-column property="mae" label="MAE (平均绝对误差)" sortable />
        <el-table-column property="rmse" label="RMSE (均方根误差)" sortable />
      </el-table>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="comparisonDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 图层控制对话框 -->
    <el-dialog v-model="layerControlVisible" title="图层显示控制" width="50%">
      <div v-for="layer in layerVisibility" :key="layer.name" class="layer-control-item">
        <el-row :gutter="12" align="middle">
          <el-col :span="1">
            <el-checkbox v-model="layer.visible" @change="updateLayerVisibility" />
          </el-col>
          <el-col :span="8">
            <span class="layer-control-name">{{ layer.name }}</span>
          </el-col>
          <el-col :span="6">
            <el-color-picker 
              v-model="layer.color" 
              @change="updateLayerVisibility"
              size="small"
            />
          </el-col>
          <el-col :span="9">
            <el-slider 
              v-model="layer.opacity" 
              :min="0" 
              :max="100"
              :format-tooltip="(val) => `${val}%`"
              @input="updateLayerVisibility"
            />
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <el-button @click="resetLayers">重置</el-button>
        <el-button type="primary" @click="layerControlVisible = false">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导出选项对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出模型" width="40%">
      <el-form label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportOptions.format">
            <el-radio value="png">PNG 图片</el-radio>
            <el-radio value="svg">SVG 矢量图</el-radio>
            <el-radio value="json">JSON 数据</el-radio>
            <el-radio value="csv">CSV 数据</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="exportOptions.format === 'png' || exportOptions.format === 'svg'" label="图片尺寸">
          <el-row :gutter="10">
            <el-col :span="11">
              <el-input-number v-model="exportOptions.width" :min="800" :max="4000" placeholder="宽度" />
            </el-col>
            <el-col :span="2" style="text-align: center;">×</el-col>
            <el-col :span="11">
              <el-input-number v-model="exportOptions.height" :min="600" :max="4000" placeholder="高度" />
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item v-if="exportOptions.format === 'png'" label="图片质量">
          <el-slider v-model="exportOptions.quality" :min="50" :max="100" show-input />
        </el-form-item>
        <el-form-item label="文件名">
          <el-input v-model="exportOptions.filename" placeholder="输入文件名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExport" :loading="isExporting">导出</el-button>
      </template>
    </el-dialog>

    <!-- 剖面对话框 -->
    <el-dialog v-model="crossSectionDialogVisible" title="地质剖面图" width="85%" top="5vh">
      <div class="cross-section-container">
        <!-- 剖面设置 -->
        <el-form :inline="true" size="small" style="margin-bottom: 16px;">
          <el-form-item label="剖面方向">
            <el-select v-model="crossSection.direction" @change="generateCrossSection" style="width: 120px;">
              <el-option label="X方向剖面" value="x" />
              <el-option label="Y方向剖面" value="y" />
            </el-select>
          </el-form-item>
          <el-form-item :label="crossSection.direction === 'x' ? 'X坐标位置' : 'Y坐标位置'">
            <el-slider 
              v-model="crossSection.position" 
              :min="crossSection.range.min" 
              :max="crossSection.range.max" 
              :step="crossSection.range.step"
              @input="generateCrossSection"
              style="width: 200px; margin: 0 16px;"
            />
            <el-input-number 
              v-model="crossSection.position" 
              :min="crossSection.range.min" 
              :max="crossSection.range.max" 
              :step="crossSection.range.step"
              @change="generateCrossSection"
              size="small"
              style="width: 120px;"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="generateCrossSection" :loading="isLoadingCrossSection">
              生成剖面
            </el-button>
          </el-form-item>
        </el-form>
        
        <!-- 剖面图表 -->
        <div ref="crossSectionChartRef" style="width: 100%; height: 600px; border: 1px solid #e5e7eb; border-radius: 4px;"></div>
        
        <!-- 剖面说明 -->
        <el-alert type="success" :closable="false" style="margin-top: 16px;" show-icon>
          <template #title>
            <span style="font-size: 14px; font-weight: bold;">剖面图使用说明</span>
          </template>
          <div style="font-size: 12px; line-height: 1.8;">
            <b>📊 功能说明：</b><br/>
            • 剖面图以彩色填充显示选定位置的地层垂直分布结构<br/>
            • <b>X方向剖面</b>：固定X坐标，沿Y轴切割查看地层<br/>
            • <b>Y方向剖面</b>：固定Y坐标，沿X轴切割查看地层<br/><br/>
            
            <b>🎨 视觉元素：</b><br/>
            • 填充色块：每个岩层的厚度范围，颜色与3D模型一致<br/>
            • 实线：岩层顶面边界<br/>
            • 虚线：岩层底面边界<br/><br/>
            
            <b>💡 交互提示：</b><br/>
            • 鼠标悬停查看精确坐标和高程<br/>
            • 点击图例可显示/隐藏特定岩层<br/>
            • 拖动底部滑块可局部放大查看<br/>
            • 鼠标滚轮可缩放视图
          </div>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="crossSectionDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="exportCrossSection">导出剖面图</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>

import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  CircleCheckFilled, 
  DataAnalysis, 
  Close, 
  Download,
  Refresh, 
  Top, 
  Right, 
  Back, 
  VideoPlay, 
  Camera, 
  FullScreen,
  Grid
} from '@element-plus/icons-vue';
import * as echarts from 'echarts';
import 'echarts-gl'; // 必须导入 echarts-gl 以支持 3D 图表
import { getApiBase } from '@/utils/api';
import { useGlobalDataStore } from '@/stores/globalData';

// 初始化store
const globalDataStore = useGlobalDataStore();

console.log('[GeologicalModeling] echarts版本:', echarts.version);
console.log('[GeologicalModeling] 可用图表类型:', Object.keys(echarts.ComponentModel || {}));


// 所有变量和方法都直接声明，模板可直接访问
const isLoading = ref(false);
const step = ref(0);
const useGlobalData = ref(true); // 默认使用全局数据
const boreholeFiles = ref([]); // File[]
const coordsFile = ref(null); // File
const boreholeInput = ref(null);
const coordsInput = ref(null);
const columns = ref({ numeric: [], text: [] });
const availableSeams = ref([]);
const chartMessage = ref('请先上传钻孔数据与坐标文件。');

// 为不同岩层分配颜色 - 使用更深的配色方案
const layerColors = [
  '#2c5aa0', '#52883d', '#d4941e', '#c73e3a', '#2e91b8', 
  '#2d7a54', '#d65a2c', '#7841a3', '#c94f9f', '#a67845',
  '#6b4428', '#3e4f5c', '#8a94a0', '#8b3a62', '#5c6b2f'
];

// 岩层名称到颜色的映射缓存
const layerColorMap = new Map();

function getColorForLayer(layerName) {
  // 判断是否为煤层 (名称中包含"煤"字)
  if (typeof layerName === 'string' && layerName.includes('煤')) {
    return '#000000'; // 所有煤层使用黑色
  }
  
  // 如果已经为该岩层名称分配过颜色,使用相同颜色
  if (layerColorMap.has(layerName)) {
    return layerColorMap.get(layerName);
  }
  
  // 为新的岩层名称分配颜色
  const colorIndex = layerColorMap.size % layerColors.length;
  const color = layerColors[colorIndex];
  layerColorMap.set(layerName, color);
  
  return color;
}
const interpolationMethods = {
  // 基础griddata方法
  "linear": "线性 (Linear)",
  "cubic": "三次样条 (Cubic)",
  "nearest": "最近邻 (Nearest)",
  // RBF径向基函数方法
  "multiquadric": "多重二次 (Multiquadric)",
  "inverse": "反距离 (Inverse)",
  "gaussian": "高斯 (Gaussian)",
  "linear_rbf": "线性RBF (Linear RBF)",
  "cubic_rbf": "三次RBF (Cubic RBF)",
  "quintic_rbf": "五次RBF (Quintic RBF)",
  "thin_plate": "薄板样条 (Thin Plate)",
  // 高级插值方法
  "modified_shepard": "修正谢泼德 (Modified Shepard)",
  "natural_neighbor": "自然邻点 (Natural Neighbor)",
  "radial_basis": "径向基函数 (Radial Basis)",
  "ordinary_kriging": "普通克里金 (Ordinary Kriging)",
  "universal_kriging": "通用克里金 (Universal Kriging)",
  "bilinear": "双线性 (Bilinear)",
  "anisotropic": "各向异性 (Anisotropic)",
  "idw": "反距离加权 (IDW)"
};
const API_BASE = getApiBase();
const params = reactive({
  x_col: '', y_col: '', thickness_col: '', seam_col: '',
  selected_seams: [],
  method: 'linear',
  validation_ratio: 20,
  resolution: 80,    // 网格分辨率
  base_level: 0.0,   // 首层基底高程
  gap: 0.0,          // 层间可视化间隔
});
const chartRef = ref(null);
let myChart = null;
let resizeHandler = null;
const comparisonDialogVisible = ref(false);
const comparisonResults = ref([]);
const bestMethod = computed(() => (comparisonResults.value.length > 0 ? comparisonResults.value[0] : null));
const canProceedToModeling = computed(() =>
  !!(params.x_col && params.y_col && params.thickness_col && params.seam_col && params.selected_seams.length > 0)
);

// 检查全局数据是否包含坐标信息
const hasCoordinatesInGlobalData = computed(() => {
  if (!useGlobalData.value || !globalDataStore.keyStratumColumns || globalDataStore.keyStratumColumns.length === 0) {
    return false;
  }
  
  const coordColumns = ['X', 'x', 'X坐标', 'x坐标', 'Y', 'y', 'Y坐标', 'y坐标'];
  const hasX = coordColumns.some(coord => 
    globalDataStore.keyStratumColumns.some(col => col.includes(coord.includes('X') || coord.includes('x') ? 'x' : 'X'))
  );
  const hasY = coordColumns.some(coord => 
    globalDataStore.keyStratumColumns.some(col => col.includes(coord.includes('Y') || coord.includes('y') ? 'y' : 'Y'))
  );
  
  return hasX && hasY;
});

// 新增状态
const current3DModel = ref(null); // 当前生成的3D模型数据
const modelStats = ref(null); // 模型统计信息
const layerControlVisible = ref(false); // 图层控制对话框
const layerVisibility = ref([]); // 图层可见性配置
const exportDialogVisible = ref(false); // 导出对话框
const isExporting = ref(false); // 导出状态

// 剖面相关状态
const crossSectionDialogVisible = ref(false); // 剖面对话框
const crossSectionChartRef = ref(null); // 剖面图表引用
let crossSectionChart = null; // 剖面图表实例
const isLoadingCrossSection = ref(false); // 剖面生成状态
const crossSection = reactive({
  direction: 'x', // 剖面方向: 'x' 或 'y'
  position: 0, // 剖面位置
  range: {
    min: 0,
    max: 100,
    step: 1
  }
});

// 3D视图控制参数
const viewControl = reactive({
  distance: 180, // 增加距离以便看清全景
  alpha: 25, // 调整俯仰角
  beta: 45, // 调整旋转角
  autoRotate: false
});

// 渲染选项
const renderOptions = reactive({
  showWireframe: false, // 默认不显示网格线,性能更好
  showAxisPointer: false, // 默认禁用以避免错误
  shadingMode: 'lambert', // 使用lambert模式更稳定
  lightIntensity: 1.5,
  ambientIntensity: 0.7,
  shadowQuality: 'medium',
  showSides: true // 是否显示侧面
});

// 导出选项
const exportOptions = reactive({
  format: 'png',
  width: 1920,
  height: 1080,
  quality: 90,
  filename: '地质模型'
});

function triggerBoreholeSelection() {
  boreholeInput.value?.click();
}
function triggerCoordsSelection() {
  coordsInput.value?.click();
}
function handleBoreholeFiles(event) {
  const files = Array.from(event.target.files || []);
  boreholeFiles.value = files;
  chartMessage.value = files.length ? '数据已选择，请点击“加载并合并数据”。' : '请先上传钻孔数据与坐标文件。';
}
function handleCoordsFile(event) {
  const [file] = Array.from(event.target.files || []);
  coordsFile.value = file || null;
}
function formatFileSize(size) {
  if (size === undefined || size === null) return '';
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}
async function loadAndMergeData() {
  // 验证数据
  if (useGlobalData.value) {
    if (globalDataStore.keyStratumData.length === 0) {
      ElMessage.warning('全局数据为空，请先在Dashboard导入钻孔数据');
      return;
    }
    // 检查是否需要坐标文件
    if (!hasCoordinatesInGlobalData.value && !coordsFile.value) {
      ElMessage.warning('全局数据不包含坐标信息，请上传坐标文件');
      return;
    }
  } else {
    // 使用上传文件模式
    if (boreholeFiles.value.length === 0) {
      ElMessage.warning('请上传钻孔文件');
      return;
    }
    if (!coordsFile.value) {
      ElMessage.warning('请上传坐标文件');
      return;
    }
  }

  isLoading.value = true;
  try {
    const formData = new FormData();
    let useMergedData = false;

    if (useGlobalData.value) {
      // 使用全局数据：将数据转换为CSV并上传
      const data = globalDataStore.keyStratumData;
      const columns = globalDataStore.keyStratumColumns;

      if (!columns || columns.length === 0) {
        throw new Error('全局数据列信息缺失');
      }

      // 检查全局数据是否已包含坐标信息
      const coordColumns = ['X', 'x', 'X坐标', 'x坐标', 'Y', 'y', 'Y坐标', 'y坐标'];
      const hasCoordinates = coordColumns.some(coord => 
        columns.some(col => col.includes(coord))
      );

      console.log('全局数据列:', columns);
      console.log('是否包含坐标:', hasCoordinates);

      if (hasCoordinates) {
        // 数据已包含坐标，使用已合并数据模式
        useMergedData = true;
        console.log('使用已合并数据模式（数据已包含坐标）');
      } else {
        // 数据不包含坐标，需要坐标文件
        if (!coordsFile.value) {
          ElMessage.warning('全局数据不包含坐标信息，请上传坐标文件');
          isLoading.value = false;
          return;
        }
        console.log('使用传统模式（需要合并坐标文件）');
      }

      // 转换为CSV格式
      const csvHeader = columns.join(',');
      const csvRows = data.map(record =>
        columns.map(col => {
          const value = record[col];
          if (value === null || value === undefined) return '';
          const strValue = String(value);
          return strValue.includes(',') ? `"${strValue}"` : strValue;
        }).join(',')
      );
      const csv = [csvHeader, ...csvRows].join('\n');

      // 创建Blob并上传
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
      formData.append('borehole_files', blob, 'global_data.csv');
      console.log('使用全局数据，记录数:', data.length);
    } else {
      // 使用上传的文件
      boreholeFiles.value.forEach(f => formData.append('borehole_files', f));
      console.log('使用上传文件，文件数:', boreholeFiles.value.length);
    }

    // 添加坐标文件（如果需要）
    if (!useMergedData && coordsFile.value) {
      formData.append('coords_file', coordsFile.value);
    }

    // 添加标志参数
    formData.append('use_merged_data', useMergedData.toString());

    const response = await fetch(`${API_BASE}/modeling/columns`, {
      method: 'POST',
      body: formData
    });

    // 检查HTTP状态码
    if (!response.ok) {
      throw new Error(`服务器响应错误: ${response.status} ${response.statusText}`);
    }

    // 检查响应是否为 JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await response.text();
      console.error('服务器返回非JSON响应:', text.substring(0, 200));
      throw new Error(`服务器返回错误格式，期待JSON但收到: ${contentType || '未知'}`);
    }

    const res = await response.json();

    if (res.status === 'success') {
      // 验证返回的数据
      if (!res.numeric_columns || !Array.isArray(res.numeric_columns)) {
        throw new Error('服务器返回的数值列数据无效');
      }
      if (!res.text_columns || !Array.isArray(res.text_columns)) {
        throw new Error('服务器返回的文本列数据无效');
      }

      columns.value.numeric = res.numeric_columns;
      columns.value.text = res.text_columns;

      const recordCount = res.record_count || 0;
      const dataSource = useGlobalData.value ? '全局数据' : '上传文件';
      ElMessage.success(`${dataSource}加载成功，共 ${recordCount} 条记录`);

      // 智能选择列
      params.x_col = res.numeric_columns.find(c => c.toLowerCase().includes('x')) || res.numeric_columns[0] || '';
      params.y_col = res.numeric_columns.find(c => c.toLowerCase().includes('y')) || res.numeric_columns[1] || '';
      params.thickness_col = res.numeric_columns.find(c => c.toLowerCase().includes('厚')) || res.numeric_columns.find(c => c.toLowerCase().includes('z')) || res.numeric_columns[2] || '';
      params.seam_col = res.text_columns.find(c => c.toLowerCase().includes('岩')) || res.text_columns[0] || '';

      if (params.seam_col) {
        await updateSeamList(params.seam_col);
      }

      step.value = 1;
      chartMessage.value = '请选择列并生成等值线或三维模型。';
    } else {
      const errorMsg = res.detail || res.message || '数据加载失败';
      ElMessage.error(errorMsg);
      chartMessage.value = errorMsg;
    }
  } catch (e) {
    console.error('数据加载失败:', e);
    const errorMsg = e.message || '数据加载失败，请检查文件格式和网络连接';
    ElMessage.error(errorMsg);
    chartMessage.value = errorMsg;
  } finally {
    isLoading.value = false;
  }
}
async function updateSeamList(seamCol) {
  if (!seamCol) {
    availableSeams.value = [];
    params.selected_seams = [];
    return;
  }
  const previousLoading = isLoading.value;
  isLoading.value = true;
  try {
  const res = await fetch(`${API_BASE}/modeling/seams?column=${encodeURIComponent(seamCol)}`).then(r => r.json());
    if (res.status === 'success') {
      availableSeams.value = res.values;
      params.selected_seams = res.values;
    } else {
      ElMessage.error(res.message);
    }
  } catch (e) {
    ElMessage.error('岩层获取失败: ' + e.message);
  } finally {
    isLoading.value = previousLoading;
  }
}
function initChart() {
  console.log('[initChart] 开始初始化图表...');

  // 销毁旧图表实例
  if (myChart) {
    console.log('[initChart] 销毁旧图表实例');
    try {
      myChart.dispose();
    } catch (e) {
      console.warn('[initChart] 销毁图表实例时出错:', e);
    }
    myChart = null;
  }

  if (!chartRef.value) {
    console.error('[initChart] ❌ chartRef.value 为空!');
    return;
  }

  console.log('[initChart] 图表容器尺寸:', {
    width: chartRef.value.offsetWidth,
    height: chartRef.value.offsetHeight,
    clientWidth: chartRef.value.clientWidth,
    clientHeight: chartRef.value.clientHeight
  });

  // 确保容器有有效的尺寸
  if (chartRef.value.offsetWidth === 0 || chartRef.value.offsetHeight === 0) {
    console.error('[initChart] ❌ 图表容器尺寸为0!');
    return;
  }

  try {
    myChart = echarts.init(chartRef.value, null, {
      renderer: 'canvas',
      useDirtyRect: true,  // 启用脏矩形优化
      devicePixelRatio: window.devicePixelRatio || 1
    });
    console.log('[initChart] ✅ 图表实例创建成功');

    // 添加错误处理
    myChart.on('error', (err) => {
      console.error('[echarts] 渲染错误:', err);
      ElMessage.error('图表渲染出错: ' + (err.message || '未知错误'));
    });
  } catch (error) {
    console.error('[initChart] ❌ 创建图表实例失败:', error);
    ElMessage.error('图表初始化失败: ' + error.message);
  }
}
onMounted(() => {
  console.log('[onMounted] 组件已挂载');
  console.log('[onMounted] echarts版本:', echarts.version);
  console.log('[onMounted] echarts对象keys:', Object.keys(echarts).slice(0, 20));
  
  // 检查 echarts-gl 是否加载
  try {
    // 尝试创建一个简单的3D图表来测试
    const testDiv = document.createElement('div');
    testDiv.style.width = '100px';
    testDiv.style.height = '100px';
    const testChart = echarts.init(testDiv);
    const testOption = {
      xAxis3D: {},
      yAxis3D: {},
      zAxis3D: {},
      grid3D: {},
      series: []
    };
    testChart.setOption(testOption);
    console.log('[onMounted] ✅ echarts-gl 3D支持可用');
    testChart.dispose();
  } catch (error) {
    console.error('[onMounted] ❌ echarts-gl 3D支持不可用:', error);
  }
  
  initChart();
  resizeHandler = () => myChart?.resize();
  window.addEventListener('resize', resizeHandler);
});
onUnmounted(() => {
  console.log('[onUnmounted] 组件卸载，清理资源...');

  // 移除事件监听器
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler);
    resizeHandler = null;
    console.log('[onUnmounted] ✅ 移除resize监听器');
  }

  // 销毁主图表实例
  if (myChart) {
    try {
      myChart.dispose();
      myChart = null;
      console.log('[onUnmounted] ✅ 销毁主图表实例');
    } catch (e) {
      console.warn('[onUnmounted] 销毁主图表实例时出错:', e);
    }
  }

  // 销毁剖面图表实例
  if (crossSectionChart) {
    try {
      crossSectionChart.dispose();
      crossSectionChart = null;
      console.log('[onUnmounted] ✅ 销毁剖面图表实例');
    } catch (e) {
      console.warn('[onUnmounted] 销毁剖面图表实例时出错:', e);
    }
  }

  // 重置状态
  chartMessage.value = '请先上传钻孔数据与坐标文件。';
  console.log('[onUnmounted] ✅ 清理完成');
});
async function generateContour() {
  isLoading.value = true;
  try {
  const res = await fetch(`${API_BASE}/modeling/contour`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x_col: params.x_col,
        y_col: params.y_col,
        z_col: params.thickness_col,
        method: params.method,
        seams: params.selected_seams
      })
    }).then(r => r.json());
    if (res.status === 'success') {
      initChart();
      const option = {
        title: { text: `${params.thickness_col} 等值线图 (${interpolationMethods[params.method]})`, left: 'center' },
        tooltip: { trigger: 'item', formatter: 'X: {b0}<br/>Y: {b1}<br/>Z: {c2}' },
        toolbox: {
          feature: {
            saveAsImage: { 
              title: '保存为图片',
              pixelRatio: 2
            },
            dataView: { 
              title: '数据视图',
              readOnly: false 
            },
            restore: { title: '还原' }
          },
          right: 20,
          top: 10
        },
        grid: { right: '15%', left: '5%', top: '15%', bottom: '10%' },
        visualMap: {
          min: Math.min(...res.points.z),
          max: Math.max(...res.points.z),
          calculable: true, orient: 'vertical', left: 'left', top: 'center',
          inRange: { color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'].reverse() },
        },
        xAxis: { type: 'category', data: res.grid.x, name: params.x_col, axisLabel: {formatter: v => Number(v).toFixed(0)} },
        yAxis: { type: 'category', data: res.grid.y, name: params.y_col, axisLabel: {formatter: v => Number(v).toFixed(0)} },
        series: [{
          name: '等值线', type: 'heatmap',
          data: res.grid.z.flatMap((row, i) => row.map((val, j) => [j, i, val])),
          progressive: 1000,
          animation: false
        }, {
          name: '原始数据点', type: 'scatter',
          data: res.points.x.map((x, i) => [x, res.points.y[i], res.points.z[i]]),
          symbolSize: 8, itemStyle: { color: '#000' },
          xAxisIndex: 0, yAxisIndex: 0
        }]
      };
      myChart.setOption(option, true);
      
      // 保存当前图表类型用于导出
      current3DModel.value = {
        type: '2D',
        data: res
      };
      
      ElMessage.success('2D等值线图生成成功！');
      chartMessage.value = '';
    } else {
      ElMessage.error(res.message);
      chartMessage.value = res.message || '生成等值线失败。';
    }
  } catch (e) {
    ElMessage.error('等值线生成失败: ' + e.message);
    chartMessage.value = '等值线生成失败，请检查数据输入。';
  } finally {
    isLoading.value = false;
  }
}
/* eslint-disable no-unused-vars */
async function generate3DModel() {
  // 参数验证
  if (!params.x_col || !params.y_col || !params.thickness_col || !params.seam_col) {
    ElMessage.warning('请先选择所有必需的列');
    return;
  }
  if (!params.selected_seams || params.selected_seams.length === 0) {
    ElMessage.warning('请至少选择一个岩层进行建模');
    return;
  }

  isLoading.value = true;
  try {
    const response = await fetch(`${API_BASE}/modeling/block_model`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x_col: params.x_col,
        y_col: params.y_col,
        thickness_col: params.thickness_col,
        seam_col: params.seam_col,
        selected_seams: params.selected_seams,
        method: params.method,
        resolution: params.resolution,
        base_level: params.base_level,
        gap: params.gap
      })
    });

    // 检查HTTP响应
    if (!response.ok) {
      throw new Error(`服务器响应错误: ${response.status} ${response.statusText}`);
    }

    const res = await response.json();

    if (res.status === 'success') {
      console.log('[3D建模] 响应数据:', res);
      console.log('[3D建模] 模型数量:', res.models?.length);
      console.log('[3D建模] 跳过数量:', res.total_skipped);
      
      // 输出建模顺序信息
      console.log('========== 建模顺序信息 ==========');
      console.log('建模顺序说明: 岩层从底部到顶部依次堆叠');
      console.log('每一层的底面 = 上一层的顶面 + 间隔(gap)');
      res.models.forEach((model, index) => {
        console.log(`${index + 1}. ${model.name} (${model.points || 0}个数据点)`);
      });
      console.log('=================================');

      // 验证响应数据
      if (!res.models || !Array.isArray(res.models)) {
        throw new Error('服务器返回的模型数据格式无效');
      }

      if (res.models.length === 0) {
        let warningMsg = '未能生成任何块体模型';
        if (res.skipped && res.skipped.length > 0) {
          warningMsg += `\n跳过的岩层:\n${res.skipped.join('\n')}`;
        }
        ElMessage.warning(warningMsg);
        chartMessage.value = '所有岩层数据不足,无法生成模型';
        return;
      }

      // 验证第一个模型的数据完整性
      const firstModel = res.models[0];
      if (!firstModel.grid_x || !firstModel.grid_y || !firstModel.top_surface_z) {
        throw new Error('模型数据缺少必需字段 (grid_x, grid_y, top_surface_z)');
      }

      console.log('[3D建模] 第一个模型:', firstModel.name);
      console.log('[3D建模] X网格长度:', firstModel.grid_x.length);
      console.log('[3D建模] Y网格长度:', firstModel.grid_y.length);
      console.log('[3D建模] Z矩阵维度:', firstModel.top_surface_z.length, 'x', firstModel.top_surface_z[0]?.length);

      // 初始化图表
      if (!myChart) {
        initChart();
      }

      if (!myChart) {
        throw new Error('图表初始化失败');
      }

      // 为每个岩层生成顶面和底面,形成完整的块体
      const series = [];

      res.models.forEach((model) => {
        // 验证数据完整性
        if (!model.grid_x || !Array.isArray(model.grid_x) || model.grid_x.length === 0) {
          console.warn(`[3D建模] 岩层 ${model.name} 的grid_x数据无效`);
          return;
        }
        if (!model.grid_y || !Array.isArray(model.grid_y) || model.grid_y.length === 0) {
          console.warn(`[3D建模] 岩层 ${model.name} 的grid_y数据无效`);
          return;
        }
        if (!model.top_surface_z || !Array.isArray(model.top_surface_z) || model.top_surface_z.length === 0) {
          console.warn(`[3D建模] 岩层 ${model.name} 的top_surface_z数据无效`);
          return;
        }
        if (!model.bottom_surface_z || !Array.isArray(model.bottom_surface_z) || model.bottom_surface_z.length === 0) {
          console.warn(`[3D建模] 岩层 ${model.name} 的bottom_surface_z数据无效`);
          return;
        }

        // 验证矩阵维度
        if (model.top_surface_z.length !== model.grid_y.length) {
          console.warn(`[3D建模] 岩层 ${model.name} 的Z矩阵行数不匹配: Z行=${model.top_surface_z.length}, Y长度=${model.grid_y.length}`);
          return;
        }
        if (model.top_surface_z[0] && model.top_surface_z[0].length !== model.grid_x.length) {
          console.warn(`[3D建模] 岩层 ${model.name} 的Z矩阵列数不匹配: Z列=${model.top_surface_z[0].length}, X长度=${model.grid_x.length}`);
          return;
        }

        const layerColor = getColorForLayer(model.name);
        const baseOpacity = model.name.includes('煤') ? 0.75 : 0.65; // 煤层稍微不透明一点

        console.log(`[3D建模] 岩层 ${model.name}: 网格尺寸 ${model.grid_x.length} × ${model.grid_y.length}, 颜色=${layerColor}`);
        console.log(`[3D建模] - grid_x范围: [${model.grid_x[0]}, ${model.grid_x[model.grid_x.length-1]}]`);
        console.log(`[3D建模] - grid_y范围: [${model.grid_y[0]}, ${model.grid_y[model.grid_y.length-1]}]`);
        console.log(`[3D建模] - top_surface_z样本: [${model.top_surface_z[0][0]}, ${model.top_surface_z[0][1]}, ${model.top_surface_z[0][2]}]`);

        // 将Z矩阵展平为一维数组
        const topZFlat = [];
        const bottomZFlat = [];
        for (let i = 0; i < model.grid_y.length; i++) {
          for (let j = 0; j < model.grid_x.length; j++) {
            const topZ = model.top_surface_z[i] && model.top_surface_z[i][j] !== undefined 
              ? model.top_surface_z[i][j] 
              : 0;
            const bottomZ = model.bottom_surface_z[i] && model.bottom_surface_z[i][j] !== undefined 
              ? model.bottom_surface_z[i][j] 
              : 0;
            topZFlat.push(topZ);
            bottomZFlat.push(bottomZ);
          }
        }

        console.log(`[3D建模] - Z数据长度: 顶面=${topZFlat.length}, 底面=${bottomZFlat.length}`);

        // 添加顶面 - 使用数组格式
        series.push({
          type: 'surface',
          name: model.name, // 使用岩层名称，不加后缀
          data: topZFlat.map((z, idx) => {
            const j = idx % model.grid_x.length;
            const i = Math.floor(idx / model.grid_x.length);
            return [model.grid_x[j], model.grid_y[i], z];
          }),
          wireframe: {
            show: renderOptions.showWireframe,
            lineStyle: {
              color: 'rgba(0,0,0,0.1)',
              width: 0.5
            }
          },
          shading: renderOptions.shadingMode,
          realisticMaterial: renderOptions.shadingMode === 'realistic' ? {
            roughness: 0.4,
            metalness: 0.1,
            textureTiling: 1
          } : undefined,
          itemStyle: {
            color: layerColor,
            opacity: baseOpacity + 0.15
          },
          emphasis: {
            itemStyle: {
              color: layerColor,
              opacity: 1.0
            }
          }
        });

        // 添加底面
        series.push({
          type: 'surface',
          name: model.name, // 使用相同的岩层名称
          data: bottomZFlat.map((z, idx) => {
            const j = idx % model.grid_x.length;
            const i = Math.floor(idx / model.grid_x.length);
            return [model.grid_x[j], model.grid_y[i], z];
          }),
          wireframe: {
            show: renderOptions.showWireframe,
            lineStyle: {
              color: 'rgba(0,0,0,0.08)',
              width: 0.5
            }
          },
          shading: renderOptions.shadingMode,
          realisticMaterial: renderOptions.shadingMode === 'realistic' ? {
            roughness: 0.5,
            metalness: 0.1,
            textureTiling: 1
          } : undefined,
          itemStyle: {
            color: layerColor,
            opacity: baseOpacity - 0.1
          },
          emphasis: {
            itemStyle: {
              color: layerColor,
              opacity: 0.9
            }
          }
        });

        // 添加四个侧面以形成真正的块体
        if (renderOptions.showSides) {
          // 添加四个侧面以形成真正的块体
          const xLen = model.grid_x.length;
          const yLen = model.grid_y.length;
          
          // 侧面1: 前侧 (Y最小)
        const frontSide = [];
        for (let j = 0; j < xLen; j++) {
          const x = model.grid_x[j];
          const y = model.grid_y[0];
          const topZ = model.top_surface_z[0][j];
          const bottomZ = model.bottom_surface_z[0][j];
          frontSide.push([x, y, topZ]);
          frontSide.push([x, y, bottomZ]);
        }
        
        series.push({
          type: 'surface',
          name: model.name, // 使用相同的岩层名称
          parametric: true,
          wireframe: {
            show: renderOptions.showWireframe,
            lineStyle: {
              color: 'rgba(0,0,0,0.1)',
              width: 0.5
            }
          },
          parametricEquation: {
            u: { min: 0, max: xLen - 1, step: 1 },
            v: { min: 0, max: 1, step: 1 },
            x: (u) => model.grid_x[Math.floor(u)],
            y: () => model.grid_y[0],
            z: (u, v) => {
              const j = Math.floor(u);
              return v === 0 ? model.bottom_surface_z[0][j] : model.top_surface_z[0][j];
            }
          },
          shading: renderOptions.shadingMode,
          itemStyle: {
            color: layerColor,
            opacity: baseOpacity * 0.7
          }
        });

        // 侧面2: 后侧 (Y最大)
        series.push({
          type: 'surface',
          name: model.name, // 使用相同的岩层名称
          parametric: true,
          wireframe: {
            show: renderOptions.showWireframe,
            lineStyle: {
              color: 'rgba(0,0,0,0.1)',
              width: 0.5
            }
          },
          parametricEquation: {
            u: { min: 0, max: xLen - 1, step: 1 },
            v: { min: 0, max: 1, step: 1 },
            x: (u) => model.grid_x[Math.floor(u)],
            y: () => model.grid_y[yLen - 1],
            z: (u, v) => {
              const j = Math.floor(u);
              return v === 0 ? model.bottom_surface_z[yLen - 1][j] : model.top_surface_z[yLen - 1][j];
            }
          },
          shading: renderOptions.shadingMode,
          itemStyle: {
            color: layerColor,
            opacity: baseOpacity * 0.7
          }
        });

        // 侧面3: 左侧 (X最小)
        series.push({
          type: 'surface',
          name: model.name, // 使用相同的岩层名称
          parametric: true,
          wireframe: {
            show: renderOptions.showWireframe,
            lineStyle: {
              color: 'rgba(0,0,0,0.1)',
              width: 0.5
            }
          },
          parametricEquation: {
            u: { min: 0, max: yLen - 1, step: 1 },
            v: { min: 0, max: 1, step: 1 },
            x: () => model.grid_x[0],
            y: (u) => model.grid_y[Math.floor(u)],
            z: (u, v) => {
              const i = Math.floor(u);
              return v === 0 ? model.bottom_surface_z[i][0] : model.top_surface_z[i][0];
            }
          },
          shading: renderOptions.shadingMode,
          itemStyle: {
            color: layerColor,
            opacity: baseOpacity * 0.7
          }
        });

        // 侧面4: 右侧 (X最大)
        series.push({
          type: 'surface',
          name: model.name, // 使用相同的岩层名称
          parametric: true,
          wireframe: {
            show: renderOptions.showWireframe,
            lineStyle: {
              color: 'rgba(0,0,0,0.1)',
              width: 0.5
            }
          },
          parametricEquation: {
            u: { min: 0, max: yLen - 1, step: 1 },
            v: { min: 0, max: 1, step: 1 },
            x: () => model.grid_x[xLen - 1],
            y: (u) => model.grid_y[Math.floor(u)],
            z: (u, v) => {
              const i = Math.floor(u);
              return v === 0 ? model.bottom_surface_z[i][xLen - 1] : model.top_surface_z[i][xLen - 1];
            }
          },
          shading: renderOptions.shadingMode,
          itemStyle: {
            color: layerColor,
            opacity: baseOpacity * 0.7
          }
        });
        } // 结束侧面渲染
      });

      if (series.length === 0) {
        throw new Error('所有模型的数据验证都失败了');
      }

      console.log('[3D建模] 生成的有效 series 数量:', series.length);

      // 计算数据范围用于设置坐标轴
      let xMin = Infinity, xMax = -Infinity;
      let yMin = Infinity, yMax = -Infinity;
      let zMin = Infinity, zMax = -Infinity;

      res.models.forEach(model => {
        if (model.grid_x && Array.isArray(model.grid_x) && model.grid_x.length > 0) {
          const validX = model.grid_x.filter(v => isFinite(v));
          if (validX.length > 0) {
            xMin = Math.min(xMin, ...validX);
            xMax = Math.max(xMax, ...validX);
          }
        }
        if (model.grid_y && Array.isArray(model.grid_y) && model.grid_y.length > 0) {
          const validY = model.grid_y.filter(v => isFinite(v));
          if (validY.length > 0) {
            yMin = Math.min(yMin, ...validY);
            yMax = Math.max(yMax, ...validY);
          }
        }
        if (model.top_surface_z && Array.isArray(model.top_surface_z)) {
          model.top_surface_z.forEach(row => {
            if (row && Array.isArray(row) && row.length > 0) {
              const validZ = row.filter(v => isFinite(v));
              if (validZ.length > 0) {
                zMin = Math.min(zMin, ...validZ);
                zMax = Math.max(zMax, ...validZ);
              }
            }
          });
        }
      });

      // 检查计算的范围是否有效
      if (!isFinite(xMin) || !isFinite(xMax) || !isFinite(yMin) || !isFinite(yMax) || !isFinite(zMin) || !isFinite(zMax)) {
        throw new Error('无法计算有效的坐标范围');
      }

      console.log('[3D建模] 数据范围:', { xMin, xMax, yMin, yMax, zMin, zMax });
      
      // 计算合理的box尺寸比例,基于实际数据范围
      const xRange = xMax - xMin;
      const yRange = yMax - yMin;
      const zRange = zMax - zMin;
      
      // 归一化到合理的显示范围 (修正box尺寸计算)
      const maxRange = Math.max(xRange, yRange, zRange);
      const boxWidth = maxRange > 0 ? (xRange / maxRange) * 100 : 100;
      const boxDepth = maxRange > 0 ? (yRange / maxRange) * 100 : 100;
      const boxHeight = maxRange > 0 ? (zRange / maxRange) * 60 : 60; // Z轴压缩以便更好观察地层
      
      console.log('[3D建模] Box尺寸:', { boxWidth, boxDepth, boxHeight, xRange, yRange, zRange });
      
      // 保存模型数据用于后续操作
      current3DModel.value = {
        models: res.models,
        series: series,
        xRange: { min: xMin, max: xMax },
        yRange: { min: yMin, max: yMax },
        zRange: { min: zMin, max: zMax },
        boxSize: { width: boxWidth, depth: boxDepth, height: boxHeight }
      };
      
      // 初始化图层可见性控制
      layerVisibility.value = series.map((s) => ({
        name: s.name,
        visible: true,
        color: getColorForLayer(s.name),
        opacity: 85
      }));
      
      // 计算模型统计信息
      calculateModelStats(res.models);
      
      const option = {
        title: [
          {
            text: `三维地质块体模型`,
            subtext: `${res.models.length}个岩层单元 | 插值方法: ${interpolationMethods[params.method]} | 分辨率: ${params.resolution}×${params.resolution}`,
            left: 'center',
            top: 10,
            textStyle: { 
              fontSize: 18, 
              fontWeight: 'bold', 
              color: '#1a1a1a',
              fontFamily: 'Arial, SimHei'
            },
            subtextStyle: {
              fontSize: 11,
              color: '#666',
              fontFamily: 'Arial, SimSun'
            }
          },
          // 添加坐标系信息
          {
            text: `坐标系统\nX轴: ${params.x_col}\nY轴: ${params.y_col}\nZ轴: 高程 (m)`,
            left: 15,
            bottom: 15,
            textStyle: {
              fontSize: 10,
              color: '#444',
              lineHeight: 16,
              fontFamily: 'Arial, SimSun'
            }
          },
          // 添加数据范围信息
          {
            text: `数据范围\nX: ${xMin.toFixed(1)} ~ ${xMax.toFixed(1)} m\nY: ${yMin.toFixed(1)} ~ ${yMax.toFixed(1)} m\nZ: ${zMin.toFixed(1)} ~ ${zMax.toFixed(1)} m`,
            right: 15,
            bottom: 15,
            textStyle: {
              fontSize: 10,
              color: '#444',
              lineHeight: 16,
              fontFamily: 'Arial, SimSun',
              align: 'right'
            }
          }
        ],
        backgroundColor: '#ffffff',
        tooltip: { 
          formatter: (p) => {
            if(p.value && Array.isArray(p.value) && p.value.length >= 3) {
              const layerName = p.seriesName;
              return `
                <div style="padding: 8px; font-family: Arial, SimSun;">
                  <div style="font-weight: bold; font-size: 13px; margin-bottom: 6px; color: #1a1a1a;">${layerName}</div>
                  <div style="font-size: 11px; line-height: 18px; color: #333;">
                    <span style="display: inline-block; width: 60px;">X坐标:</span><b>${p.value[0].toFixed(2)}</b> m<br/>
                    <span style="display: inline-block; width: 60px;">Y坐标:</span><b>${p.value[1].toFixed(2)}</b> m<br/>
                    <span style="display: inline-block; width: 60px;">高程:</span><b>${p.value[2].toFixed(2)}</b> m
                  </div>
                </div>
              `;
            }
            return p.seriesName || '未知';
          },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#ddd',
          borderWidth: 1,
          padding: 0,
          textStyle: {
            color: '#333'
          }
        },
        legend: { 
          data: [...new Set(res.models.map(m => m.name))], // 只显示唯一的岩层名称
          orient: 'vertical', 
          right: 15, 
          top: 80,
          backgroundColor: 'rgba(255,255,255,0.95)',
          padding: [10, 12],
          borderRadius: 6,
          borderColor: '#e0e0e0',
          borderWidth: 1,
          type: 'scroll',
          pageButtonPosition: 'end',
          selector: [
            {
              type: 'all',
              title: '全选'
            },
            {
              type: 'inverse',
              title: '反选'
            }
          ],
          selected: res.models.reduce((acc, model) => {
            acc[model.name] = true; // 默认全部选中
            return acc;
          }, {}),
          formatter: (name) => {
            // 在图例中添加图标和格式化名称
            const isCoal = name.includes('煤');
            return isCoal ? `{coal|●} ${name}` : `{normal|●} ${name}`;
          },
          textStyle: {
            fontSize: 11,
            fontFamily: 'Arial, SimSun',
            rich: {
              coal: {
                color: '#000000',
                fontSize: 14
              },
              normal: {
                fontSize: 14
              }
            }
          }
        },
        xAxis3D: { 
          type: 'value', 
          name: `${params.x_col} (m)`,
          nameTextStyle: {
            fontSize: 12,
            fontWeight: 'bold',
            color: '#333',
            fontFamily: 'Arial, SimSun'
          },
          min: xMin,
          max: xMax,
          axisLabel: {
            fontSize: 10,
            color: '#666',
            formatter: (value) => value !== undefined && value !== null ? value.toFixed(0) : '0'
          },
          splitNumber: 5
        },
        yAxis3D: { 
          type: 'value', 
          name: `${params.y_col} (m)`,
          nameTextStyle: {
            fontSize: 12,
            fontWeight: 'bold',
            color: '#333',
            fontFamily: 'Arial, SimSun'
          },
          min: yMin,
          max: yMax,
          axisLabel: {
            fontSize: 10,
            color: '#666',
            formatter: (value) => value !== undefined && value !== null ? value.toFixed(0) : '0'
          },
          splitNumber: 5
        },
        zAxis3D: { 
          type: 'value', 
          name: '高程 (m)',
          nameTextStyle: {
            fontSize: 12,
            fontWeight: 'bold',
            color: '#333',
            fontFamily: 'Arial, SimSun'
          },
          min: zMin,
          max: zMax,
          axisLabel: {
            fontSize: 10,
            color: '#666',
            formatter: (value) => value !== undefined && value !== null ? value.toFixed(1) : '0.0'
          },
          splitNumber: 5
        },
        grid3D: {
          show: true,
          boxWidth: boxWidth,
          boxDepth: boxDepth,
          boxHeight: boxHeight,
          environment: '#fff',
          backgroundColor: '#ffffff',
          viewControl: { 
            projection: 'perspective', 
            autoRotate: viewControl.autoRotate,
            autoRotateSpeed: 10,
            distance: viewControl.distance,
            alpha: viewControl.alpha,
            beta: viewControl.beta,
            minAlpha: -90,
            maxAlpha: 90,
            minDistance: 80,
            maxDistance: 300,
            rotateSensitivity: 1,
            zoomSensitivity: 1,
            panSensitivity: 1,
            animation: true,
            animationDurationUpdate: 300
          },
          axisLine: {
            show: true,
            lineStyle: {
              color: '#666',
              width: 1.5
            }
          },
          axisPointer: {
            show: renderOptions.showAxisPointer,
            lineStyle: {
              color: '#f00',
              width: 2
            },
            label: {
              show: true,
              formatter: function (params) {
                return params && params.value !== undefined && params.value !== null 
                  ? params.value.toFixed(2) 
                  : '0.00';
              }
            }
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: 'rgba(100, 100, 100, 0.15)',
              width: 1
            }
          },
          splitArea: {
            show: false
          },
          light: {
            main: {
              intensity: renderOptions.lightIntensity,
              shadow: true,
              shadowQuality: renderOptions.shadowQuality,
              alpha: 30,
              beta: 40
            },
            ambient: {
              intensity: renderOptions.ambientIntensity
            }
          },
          postEffect: {
            enable: false
          },
          temporalSuperSampling: {
            enable: true
          }
        },
        series: series
      };
      
      console.log('[3D建模] 设置 echarts option, series数量:', option.series.length);
      
      if (!myChart) {
        console.error('[3D建模] ❌ myChart 实例不存在! 重新初始化...');
        initChart();
        if (!myChart) {
          ElMessage.error('图表初始化失败');
          return;
        }
      }
      
      try {
        // 使用nextTick确保在DOM更新后执行
        nextTick(() => {
          if (!myChart) return;
          
          myChart.setOption(option, { notMerge: true, replaceMerge: ['series'] });
          console.log('[3D建模] ✅ echarts setOption 完成');
          console.log('[3D建模] 验证series配置:', {
            seriesCount: option.series.length,
            firstSeries: option.series[0] ? {
              type: option.series[0].type,
              name: option.series[0].name,
              hasData: !!option.series[0].data,
              dataType: typeof option.series[0].data
            } : null
          });
          
          // 延迟刷新,确保渲染完成
          setTimeout(() => {
            if (myChart) {
              myChart.resize();
              console.log('[3D建模] 图表resize完成');
            }
          }, 200);
        });
      } catch (error) {
        console.error('[3D建模] ❌ setOption 失败:', error);
        console.error('[3D建模] 错误堆栈:', error.stack);
        ElMessage.error('图表渲染失败: ' + error.message);
        return;
      }
      
      // 成功消息
      ElMessage.success(`3D块体模型生成成功! 已建模 ${res.models.length} 个岩层`);
      chartMessage.value = '';
      
      // 跳过的岩层提示
      if(res.skipped && res.skipped.length > 0) {
        const skippedCount = res.skipped.length;
        
        ElMessageBox.alert(
          `<div style="max-height: 300px; overflow-y: auto;">
            <p><b>以下岩层因数据点不足未能建模:</b></p>
            <ul style="text-align: left; padding-left: 20px;">
              ${res.skipped.map(s => `<li>${s}</li>`).join('')}
            </ul>
            <p style="margin-top: 12px; color: #606266; font-size: 13px;">
              <b>建议:</b><br/>
              • 数据点过少(1-3个)的岩层会自动使用最近邻插值<br/>
              • 对于重要岩层,建议补充更多钻孔数据<br/>
              • 可以取消选择数据点不足的岩层以提高建模质量
            </p>
          </div>`,
          `部分岩层被跳过 (${skippedCount}个)`,
          {
            dangerouslyUseHTMLString: true,
            confirmButtonText: '我知道了'
          }
        );
      }
    } else {
      const errorMsg = res.message || '生成3D模型失败';
      ElMessage.error(errorMsg);
      chartMessage.value = errorMsg;
    }
  } catch (e) {
    console.error('3D模型生成失败:', e);
    const errorMsg = e.message || '3D模型生成失败，请检查数据和网络连接';
    ElMessage.error(errorMsg);
    chartMessage.value = errorMsg;
  } finally {
    isLoading.value = false;
  }
}

// 计算模型统计信息
function calculateModelStats(models) {
  if (!models || models.length === 0) {
    modelStats.value = null;
    return;
  }

  const layers = models.map(model => {
    // 计算体积 (简化计算:网格面积 × 平均厚度)
    const gridArea = (model.grid_x[model.grid_x.length - 1] - model.grid_x[0]) * 
                     (model.grid_y[model.grid_y.length - 1] - model.grid_y[0]);
    
    // 计算厚度统计
    const thicknesses = [];
    for (let i = 0; i < model.top_surface_z.length; i++) {
      for (let j = 0; j < model.top_surface_z[i].length; j++) {
        const thickness = model.top_surface_z[i][j] - (model.bottom_surface_z?.[i]?.[j] || 0);
        if (isFinite(thickness) && thickness > 0) {
          thicknesses.push(thickness);
        }
      }
    }
    
    const avgThickness = thicknesses.length > 0 
      ? thicknesses.reduce((a, b) => a + b, 0) / thicknesses.length 
      : 0;
    const minThickness = thicknesses.length > 0 ? Math.min(...thicknesses) : 0;
    const maxThickness = thicknesses.length > 0 ? Math.max(...thicknesses) : 0;
    const volume = gridArea * avgThickness;

    return {
      name: model.name || '未命名',
      points: model.points || 0,
      avgThickness,
      minThickness,
      maxThickness,
      volume
    };
  });

  const totalPoints = layers.reduce((sum, l) => sum + l.points, 0);
  const totalVolume = layers.reduce((sum, l) => sum + l.volume, 0);

  modelStats.value = {
    layerCount: models.length,
    totalPoints,
    totalVolume,
    layers
  };
}
/* eslint-enable no-unused-vars */

// 更新3D视图
function update3DView() {
  if (!myChart || !current3DModel.value) return;

  const updateOption = {
    grid3D: {
      viewControl: {
        autoRotate: viewControl.autoRotate,
        distance: viewControl.distance,
        alpha: viewControl.alpha,
        beta: viewControl.beta
      },
      light: {
        main: {
          intensity: renderOptions.lightIntensity,
          shadow: true,
          shadowQuality: renderOptions.shadowQuality,
          alpha: 30,
          beta: 40
        },
        ambient: {
          intensity: renderOptions.ambientIntensity
        }
      }
    }
  };

  // 如果有series数据,也更新series的渲染选项
  if (current3DModel.value.series && current3DModel.value.series.length > 0) {
    updateOption.series = current3DModel.value.series.map(s => ({
      ...s,
      wireframe: {
        ...s.wireframe,
        show: renderOptions.showWireframe
      },
      shading: renderOptions.shadingMode,
      realisticMaterial: renderOptions.shadingMode === 'realistic' ? {
        roughness: s.name.includes('底') ? 0.5 : 0.4,
        metalness: 0.1,
        textureTiling: 1
      } : undefined
    }));
  }

  // 使用nextTick避免在渲染过程中调用
  nextTick(() => {
    if (myChart) {
      myChart.setOption(updateOption, { notMerge: false, lazyUpdate: false });
    }
  });
}

// 重置视图
function resetView() {
  viewControl.distance = 180;
  viewControl.alpha = 25;
  viewControl.beta = 45;
  viewControl.autoRotate = false;
  update3DView();
  ElMessage.success('视图已重置');
}

// 设置俯视图
function setTopView() {
  viewControl.alpha = 90;
  viewControl.beta = 0;
  viewControl.autoRotate = false;
  update3DView();
  ElMessage.success('已切换到俯视图');
}

// 设置侧视图
function setSideView() {
  viewControl.alpha = 0;
  viewControl.beta = 90;
  viewControl.autoRotate = false;
  update3DView();
  ElMessage.success('已切换到侧视图');
}

// 设置前视图
function setFrontView() {
  viewControl.alpha = 0;
  viewControl.beta = 0;
  viewControl.autoRotate = false;
  update3DView();
  ElMessage.success('已切换到前视图');
}

// 切换自动旋转
function toggleAutoRotate() {
  viewControl.autoRotate = !viewControl.autoRotate;
  update3DView();
}

// 截图
function captureImage() {
  if (!myChart) {
    ElMessage.warning('没有可截图的内容');
    return;
  }
  
  const dataURL = myChart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff'
  });
  
  const link = document.createElement('a');
  link.href = dataURL;
  link.download = `地质模型_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.png`;
  link.click();
  
  ElMessage.success('截图已保存');
}

// 全屏切换
function toggleFullscreen() {
  const container = chartRef.value?.parentElement;
  if (!container) return;
  
  if (!document.fullscreenElement) {
    container.requestFullscreen().then(() => {
      ElMessage.success('已进入全屏模式');
      // 全屏后重新调整图表大小
      setTimeout(() => {
        myChart?.resize();
      }, 100);
    }).catch(() => {
      ElMessage.error('进入全屏失败');
    });
  } else {
    document.exitFullscreen().then(() => {
      ElMessage.success('已退出全屏');
      setTimeout(() => {
        myChart?.resize();
      }, 100);
    });
  }
}

// 显示图层控制
function showLayerControl() {
  layerControlVisible.value = true;
}

// 更新图层可见性
function updateLayerVisibility() {
  if (!myChart || !current3DModel.value) return;

  const updatedSeries = current3DModel.value.series.map((s, idx) => {
    const layer = layerVisibility.value[idx];
    return {
      ...s,
      silent: !layer.visible,
      itemStyle: {
        ...s.itemStyle,
        color: layer.color,
        opacity: layer.opacity / 100
      },
      emphasis: {
        ...s.emphasis,
        itemStyle: {
          ...s.emphasis.itemStyle,
          color: layer.color,
          opacity: Math.min((layer.opacity + 15) / 100, 1)
        }
      }
    };
  }).filter((s, idx) => layerVisibility.value[idx].visible);

  myChart.setOption({
    series: updatedSeries,
    legend: {
      data: updatedSeries.map(s => s.name)
    }
  });
}

// 重置图层
function resetLayers() {
  if (!current3DModel.value) return;
  
  layerVisibility.value = current3DModel.value.series.map((s) => ({
    name: s.name,
    visible: true,
    color: getColorForLayer(s.name),
    opacity: 85
  }));
  
  updateLayerVisibility();
  ElMessage.success('图层设置已重置');
}

// 导出模型
function exportModel() {
  if (!myChart && !current3DModel.value) {
    ElMessage.warning('没有可导出的模型');
    return;
  }
  
  // 根据当前模型类型设置默认文件名
  if (current3DModel.value?.type === '2D') {
    exportOptions.filename = '地质等值线图';
  } else {
    exportOptions.filename = '地质3D模型';
  }
  
  exportDialogVisible.value = true;
}

// 确认导出
async function confirmExport() {
  if (!exportOptions.filename) {
    ElMessage.warning('请输入文件名');
    return;
  }

  isExporting.value = true;
  try {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = `${exportOptions.filename}_${timestamp}`;

    switch (exportOptions.format) {
      case 'png':
        await exportAsPNG(filename);
        break;
      case 'svg':
        await exportAsSVG(filename);
        break;
      case 'json':
        await exportAsJSON(filename);
        break;
      case 'csv':
        await exportAsCSV(filename);
        break;
    }

    ElMessage.success(`导出成功: ${filename}`);
    exportDialogVisible.value = false;
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('导出失败: ' + error.message);
  } finally {
    isExporting.value = false;
  }
}

// 导出为PNG
async function exportAsPNG(filename) {
  if (!myChart) return;

  const dataURL = myChart.getDataURL({
    type: 'png',
    pixelRatio: exportOptions.quality / 50, // 质量转换为像素比
    backgroundColor: '#fff'
  });

  downloadFile(dataURL, `${filename}.png`);
}

// 导出为SVG
async function exportAsSVG(filename) {
  if (!myChart) return;

  const dataURL = myChart.getDataURL({
    type: 'svg',
    backgroundColor: '#fff'
  });

  downloadFile(dataURL, `${filename}.svg`);
}

// 导出为JSON
async function exportAsJSON(filename) {
  if (!current3DModel.value) return;

  const data = {
    metadata: {
      exportTime: new Date().toISOString(),
      modelType: '3D地质块体模型',
      parameters: {
        xCol: params.x_col,
        yCol: params.y_col,
        thicknessCol: params.thickness_col,
        seamCol: params.seam_col,
        method: params.method,
        resolution: params.resolution,
        baseLevel: params.base_level,
        gap: params.gap
      }
    },
    models: current3DModel.value.models,
    statistics: modelStats.value
  };

  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  downloadFile(url, `${filename}.json`);
  URL.revokeObjectURL(url);
}

// 导出为CSV
async function exportAsCSV(filename) {
  if (!current3DModel.value) return;

  const rows = [
    ['岩层名称', 'X坐标', 'Y坐标', '顶面高程', '底面高程', '厚度']
  ];

  current3DModel.value.models.forEach(model => {
    for (let i = 0; i < model.grid_y.length; i++) {
      for (let j = 0; j < model.grid_x.length; j++) {
        const x = model.grid_x[j];
        const y = model.grid_y[i];
        const topZ = model.top_surface_z[i][j];
        const bottomZ = model.bottom_surface_z?.[i]?.[j] || 0;
        const thickness = topZ - bottomZ;

        if (isFinite(topZ) && isFinite(bottomZ)) {
          rows.push([
            model.name,
            x.toFixed(2),
            y.toFixed(2),
            topZ.toFixed(2),
            bottomZ.toFixed(2),
            thickness.toFixed(2)
          ]);
        }
      }
    }
  });

  const csvContent = rows.map(row => row.join(',')).join('\n');
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  downloadFile(url, `${filename}.csv`);
  URL.revokeObjectURL(url);
}

// 下载文件辅助函数
function downloadFile(url, filename) {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function runComparison() {
  isLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/modeling/comparison`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        x_col: params.x_col,
        y_col: params.y_col,
        z_col: params.thickness_col,
        validation_ratio: params.validation_ratio / 100,
        seams: params.selected_seams
      })
    }).then(r => r.json());
    if (res.status === 'success') {
      comparisonResults.value = res.results;
      comparisonDialogVisible.value = true;
      if(res.results.length > 0){
        const bestMethodKey = Object.keys(interpolationMethods).find(key => interpolationMethods[key] === res.results[0].method);
        if(bestMethodKey) params.method = bestMethodKey;
      }
      ElMessage.success('插值方法对比完成！');
    } else {
      ElMessage.error(res.message);
    }
  } catch (e) {
    ElMessage.error('插值对比失败: ' + e.message);
  } finally {
    isLoading.value = false;
  }
}

// ==================== 剖面功能 ====================

// 显示剖面对话框
function showCrossSectionDialog() {
  if (!current3DModel.value || !current3DModel.value.models) {
    ElMessage.warning('请先生成3D模型');
    return;
  }
  
  // 初始化剖面范围
  const models = current3DModel.value.models;
  if (models.length === 0) {
    ElMessage.warning('模型数据为空');
    return;
  }
  
  const firstModel = models[0];
  if (crossSection.direction === 'x') {
    // X方向剖面：固定X，沿Y切割
    crossSection.range.min = Math.min(...firstModel.grid_x);
    crossSection.range.max = Math.max(...firstModel.grid_x);
    crossSection.range.step = (crossSection.range.max - crossSection.range.min) / 50;
    crossSection.position = (crossSection.range.min + crossSection.range.max) / 2;
  } else {
    // Y方向剖面：固定Y，沿X切割
    crossSection.range.min = Math.min(...firstModel.grid_y);
    crossSection.range.max = Math.max(...firstModel.grid_y);
    crossSection.range.step = (crossSection.range.max - crossSection.range.min) / 50;
    crossSection.position = (crossSection.range.min + crossSection.range.max) / 2;
  }
  
  crossSectionDialogVisible.value = true;
  
  // 等待对话框打开后再初始化图表
  nextTick(() => {
    initCrossSectionChart();
    generateCrossSection();
  });
}

// 初始化剖面图表
function initCrossSectionChart() {
  if (!crossSectionChartRef.value) {
    console.error('[剖面] 图表容器未找到');
    return;
  }
  
  // 销毁旧图表
  if (crossSectionChart) {
    crossSectionChart.dispose();
    crossSectionChart = null;
  }
  
  // 创建新图表
  crossSectionChart = echarts.init(crossSectionChartRef.value);
  console.log('[剖面] 图表初始化成功');
}

// 生成剖面数据
function generateCrossSection() {
  if (!crossSectionChart || !current3DModel.value) {
    return;
  }
  
  isLoadingCrossSection.value = true;
  
  try {
    const models = current3DModel.value.models;
    const series = [];
    
    models.forEach((model, modelIndex) => {
      const layerColor = getColorForLayer(model.name);
      const crossSectionData = extractCrossSectionData(model);
      
      if (!crossSectionData || crossSectionData.length === 0) {
        console.warn(`[剖面] 岩层 ${model.name} 无剖面数据`);
        return;
      }
      
      // 创建闭合的多边形：顶线 + 底线倒序
      const topLine = crossSectionData.map(point => [point.position, point.top]);
      const bottomLine = crossSectionData.map(point => [point.position, point.bottom]).reverse();
      const polygonData = [...topLine, ...bottomLine, topLine[0]]; // 闭合多边形
      
      // 使用custom类型创建填充多边形
      series.push({
        name: model.name,
        type: 'custom',
        renderItem: (params, api) => {
          const points = polygonData.map(point => api.coord(point));
          return {
            type: 'polygon',
            shape: {
              points: points
            },
            style: {
              fill: layerColor,
              opacity: 0.85, // 提高不透明度，填充更明显
              stroke: layerColor,
              lineWidth: 2.5, // 加粗边框
              shadowBlur: 8, // 添加阴影效果
              shadowColor: 'rgba(0, 0, 0, 0.2)',
              shadowOffsetX: 2,
              shadowOffsetY: 2
            }
          };
        },
        data: [0], // 只需要一个数据点来触发renderItem
        z: 10 - modelIndex, // 确保正确的层叠顺序
        emphasis: {
          focus: 'series',
          itemStyle: {
            opacity: 1.0,
            shadowBlur: 12,
            shadowColor: 'rgba(0, 0, 0, 0.4)'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: () => {
            const thickness = crossSectionData.length > 0 
              ? (crossSectionData[0].top - crossSectionData[0].bottom).toFixed(2)
              : 'N/A';
            return `<b>${model.name}</b><br/>平均厚度: ${thickness} m<br/>点击图例可显示/隐藏`;
          }
        }
      });
      
      // 添加顶线用于显示轮廓
      series.push({
        name: `${model.name}_outline_top`,
        type: 'line',
        data: topLine,
        lineStyle: {
          color: layerColor,
          width: 2.5,
          shadowBlur: 4,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        },
        symbol: 'none',
        showInLegend: false,
        z: 20,
        smooth: true, // 平滑曲线
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const p = params[0];
            return `<b>${model.name} (顶面)</b><br/>位置: ${p.data[0].toFixed(2)} m<br/>高程: ${p.data[1].toFixed(2)} m`;
          }
        }
      });
      
      // 添加底线用于显示轮廓
      series.push({
        name: `${model.name}_outline_bottom`,
        type: 'line',
        data: crossSectionData.map(point => [point.position, point.bottom]),
        lineStyle: {
          color: layerColor,
          width: 1.5,
          type: 'dashed',
          dashOffset: 5
        },
        symbol: 'none',
        showInLegend: false,
        z: 20,
        smooth: true, // 平滑曲线
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const p = params[0];
            return `<b>${model.name} (底面)</b><br/>位置: ${p.data[0].toFixed(2)} m<br/>高程: ${p.data[1].toFixed(2)} m`;
          }
        }
      });
    });
    
    const option = {
      title: {
        text: `地质剖面图 (${crossSection.direction === 'x' ? 'X' : 'Y'} = ${crossSection.position.toFixed(2)} m)`,
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 18,
          fontWeight: 'bold',
          color: '#333'
        },
        subtext: `共 ${models.length} 个岩层`,
        subtextStyle: {
          fontSize: 12,
          color: '#666'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#ccc',
        borderWidth: 1,
        textStyle: {
          color: '#333'
        },
        formatter: (params) => {
          if (!params || params.length === 0) return '';
          
          const position = params[0].data[0];
          const axisLabel = crossSection.direction === 'x' ? 'Y' : 'X';
          
          let result = `<div style="padding: 8px;">`;
          result += `<b style="font-size: 14px;">${axisLabel}坐标: ${position.toFixed(2)} m</b><br/><br/>`;
          
          // 只显示主系列（不包括outline）
          params.filter(p => !p.seriesName.includes('_outline')).forEach(p => {
            if (p.data && p.data[1] !== undefined) {
              const elevation = p.data[1];
              result += `${p.marker} <b>${p.seriesName}</b>: ${elevation.toFixed(2)} m<br/>`;
            }
          });
          
          result += `</div>`;
          return result;
        }
      },
      legend: {
        data: models.map(m => m.name),
        top: 50,
        type: 'scroll',
        orient: 'horizontal',
        left: 'center',
        itemWidth: 30,
        itemHeight: 14,
        textStyle: {
          fontSize: 13,
          fontWeight: '500'
        },
        emphasis: {
          selectorLabel: {
            show: true
          }
        }
      },
      grid: {
        left: 90,
        right: 50,
        bottom: 90,
        top: 110,
        containLabel: true,
        backgroundColor: '#fafafa',
        borderWidth: 1,
        borderColor: '#ddd'
      },
      xAxis: {
        type: 'value',
        name: crossSection.direction === 'x' ? 'Y坐标 (m)' : 'X坐标 (m)',
        nameLocation: 'middle',
        nameGap: 40,
        nameTextStyle: {
          fontSize: 14,
          fontWeight: 'bold',
          color: '#333'
        },
        axisLine: {
          lineStyle: {
            color: '#666'
          }
        },
        axisLabel: {
          formatter: '{value}',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            type: 'dashed',
            color: '#e0e0e0'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '高程 (m)',
        nameLocation: 'middle',
        nameGap: 55,
        nameTextStyle: {
          fontSize: 14,
          fontWeight: 'bold',
          color: '#333'
        },
        axisLine: {
          lineStyle: {
            color: '#666'
          }
        },
        axisLabel: {
          formatter: '{value}',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            type: 'dashed',
            color: '#e0e0e0'
          }
        }
      },
      series: series,
      dataZoom: [
        {
          type: 'slider',
          show: true,
          xAxisIndex: [0],
          start: 0,
          end: 100,
          bottom: 20
        },
        {
          type: 'inside',
          xAxisIndex: [0],
          start: 0,
          end: 100
        }
      ]
    };
    
    crossSectionChart.setOption(option, true);
    console.log('[剖面] 剖面图生成成功');
    
  } catch (error) {
    console.error('[剖面] 生成失败:', error);
    ElMessage.error('剖面生成失败: ' + error.message);
  } finally {
    isLoadingCrossSection.value = false;
  }
}

// 提取剖面数据
function extractCrossSectionData(model) {
  const data = [];
  
  try {
    if (crossSection.direction === 'x') {
      // X方向剖面：固定X坐标，提取不同Y位置的数据
      // 找到最接近目标X的索引
      const xIndex = findClosestIndex(model.grid_x, crossSection.position);
      
      if (xIndex === -1) {
        console.warn('[剖面] 未找到匹配的X坐标');
        return data;
      }
      
      // 沿Y方向提取数据
      model.grid_y.forEach((y, yIndex) => {
        const topZ = model.top_surface_z[yIndex][xIndex];
        const bottomZ = model.bottom_surface_z[yIndex][xIndex];
        
        if (topZ !== null && topZ !== undefined && 
            bottomZ !== null && bottomZ !== undefined) {
          data.push({
            position: y,
            top: topZ,
            bottom: bottomZ
          });
        }
      });
      
    } else {
      // Y方向剖面：固定Y坐标，提取不同X位置的数据
      const yIndex = findClosestIndex(model.grid_y, crossSection.position);
      
      if (yIndex === -1) {
        console.warn('[剖面] 未找到匹配的Y坐标');
        return data;
      }
      
      // 沿X方向提取数据
      model.grid_x.forEach((x, xIndex) => {
        const topZ = model.top_surface_z[yIndex][xIndex];
        const bottomZ = model.bottom_surface_z[yIndex][xIndex];
        
        if (topZ !== null && topZ !== undefined && 
            bottomZ !== null && bottomZ !== undefined) {
          data.push({
            position: x,
            top: topZ,
            bottom: bottomZ
          });
        }
      });
    }
    
    console.log(`[剖面] ${model.name} 提取了 ${data.length} 个数据点`);
    return data;
    
  } catch (error) {
    console.error('[剖面] 数据提取失败:', error);
    return data;
  }
}

// 查找最接近目标值的索引
function findClosestIndex(array, target) {
  if (!array || array.length === 0) return -1;
  
  let closestIndex = 0;
  let minDiff = Math.abs(array[0] - target);
  
  for (let i = 1; i < array.length; i++) {
    const diff = Math.abs(array[i] - target);
    if (diff < minDiff) {
      minDiff = diff;
      closestIndex = i;
    }
  }
  
  return closestIndex;
}

// 导出剖面图
function exportCrossSection() {
  if (!crossSectionChart) {
    ElMessage.warning('请先生成剖面图');
    return;
  }
  
  try {
    const url = crossSectionChart.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    });
    
    const direction = crossSection.direction === 'x' ? 'X' : 'Y';
    const position = crossSection.position.toFixed(2);
    const filename = `地质剖面_${direction}=${position}.png`;
    
    downloadFile(url, filename);
    ElMessage.success('剖面图导出成功');
  } catch (error) {
    console.error('[剖面] 导出失败:', error);
    ElMessage.error('导出失败: ' + error.message);
  }
}

</script>

<style scoped>
.geo-modeling-container {
  height: 100%;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}
.content-row { 
  flex: 1; 
  height: 100%;
  overflow: hidden;
}
.panel-col, .chart-col { 
  height: 100%;
  display: flex;
  flex-direction: column;
}
.panel {
  height: 100%;
  padding: 14px;
  background-color: #fff;
  border-radius: 8px;
  overflow-y: auto;
  box-sizing: border-box;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.panel-step { display: flex; flex-direction: column; gap: 16px; }

/* 图表容器样式优化 */
.chart-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
}

.chart-wrapper { 
  position: relative; 
  height: 100%;
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  overflow: hidden;
}

.chart-canvas { 
  width: 100% !important; 
  height: 100% !important;
  flex: 1;
  background: #ffffff;
}

.chart-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 16px;
  pointer-events: none;
  z-index: 10;
  background-color: #ffffff;
}

/* 全局数据状态信息 */
.data-status-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 13px;
}

.data-status-info .status-icon {
  font-size: 18px;
  color: #0284c7;
}

.data-status-info .status-text {
  color: #0c4a6e;
  font-weight: 500;
}

.data-status-info .status-count {
  color: #075985;
  font-weight: 600;
  margin-left: auto;
}

/* 数据源选择器 */
.data-source-selector {
  margin-bottom: 16px;
}

.data-source-selector :deep(.el-radio-group) {
  display: flex;
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.data-source-selector :deep(.el-radio-button) {
  flex: 1;
  margin: 0;
}

.data-source-selector :deep(.el-radio-button__inner) {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  text-align: center;
  background: #ffffff;
  color: #64748b;
  margin: 0;
  box-shadow: none;
}

.data-source-selector :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  box-shadow: none;
}

/* 全局数据摘要 */
.global-data-summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border: 1px solid #bae6fd;
}

.global-data-summary .data-icon {
  font-size: 28px;
  color: #0284c7;
}

.global-data-summary .data-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.global-data-summary .data-label {
  font-size: 13px;
  color: #0c4a6e;
  font-weight: 500;
}

.global-data-summary .data-count {
  font-size: 12px;
  color: #075985;
}

.file-group {
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  padding: 12px;
  background: #f8fafc;
}
.file-group__header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.hidden-input { display: none; }
.file-scroll { max-height: 160px; }
.file-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 6px; }
.file-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #334155;
  padding: 6px 8px;
  background: #ffffff;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}
.coords-summary {
  font-size: 13px;
  color: #334155;
  background: #ffffff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}
.coords-summary .muted { color: #94a3b8; }
.coords-summary .info-text { 
  color: #0ea5e9; 
  font-weight: 500;
  display: flex;
  align-items: center;
}
.coords-summary .info-text::before {
  content: '✓';
  margin-right: 6px;
  color: #10b981;
  font-weight: bold;
}

.full-width { 
  width: 100%; 
  min-height: 40px;
  height: auto;
  white-space: normal;
  line-height: 1.4;
  padding: 10px 15px;
}
.full-width :deep(span) {
  white-space: normal;
  word-break: break-word;
  text-align: center;
}
.el-form-item { margin-bottom: 12px; }
h5 { margin: 0; font-size: 14px; color: #1f2937; }

/* 快捷工具栏 */
.quick-toolbar {
  position: absolute;
  top: 15px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 30px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  z-index: 100;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.quick-toolbar :deep(.el-button) {
  transition: all 0.3s;
}

.quick-toolbar :deep(.el-button:hover) {
  transform: scale(1.1);
}

.quick-toolbar :deep(.el-divider--vertical) {
  height: 20px;
  margin: 0 4px;
}

/* 统计信息面板 */
.stats-panel {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 360px;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 10px;
  padding: 14px 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  z-index: 100;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stats-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 6px;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #0284c7;
}

.layer-stat {
  padding: 8px;
  background: #f8fafc;
  border-radius: 4px;
  margin-bottom: 6px;
}

.layer-name {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
}

.layer-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: #64748b;
}

/* 图层控制 */
.layer-control-item {
  padding: 10px;
  margin-bottom: 8px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.layer-control-name {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
}

/* 剖面对话框样式 */
.cross-section-container {
  padding: 0;
}

.cross-section-container .el-form {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.cross-section-container .el-form-item {
  margin-bottom: 0;
}

</style>
