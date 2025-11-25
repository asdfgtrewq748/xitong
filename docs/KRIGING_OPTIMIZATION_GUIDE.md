# 克里金插值优化指南

## 问题说明

### 症状
- **本地环境**：普通克里金插值正常工作
- **服务器环境**：普通克里金插值报错或超时

### 根本原因

有三个主要问题：

1. **依赖缺失**：服务器上未安装 `pykrige` 库
2. **性能限制**：克里金算法复杂度为 O(n³)，数据点过多时消耗大量内存和计算资源
3. **内存不足**：服务器内存可能不足以处理大型克里金计算

---

## 解决方案

### 1. 安装依赖（必需）

在服务器上安装 `pykrige`：

```bash
# 进入后端目录
cd /path/to/backend

# 安装依赖
pip install pykrige==1.7.1

# 或者重新安装所有依赖
pip install -r requirements.txt
```

### 2. 性能优化（已实现）

系统已添加以下优化措施：

#### 数据点限制
- **最大数据点数**：500 个点
- **超过限制**：自动随机降采样到 500 个点
- **影响**：对于密集数据，会损失部分细节，但保证可以运行

#### 多层回退机制
```
普通克里金 (pykrige)
  ↓ 失败/超时
高斯RBF近似
  ↓ 失败
线性插值（保底）
```

#### 内存保护
- 捕获 `MemoryError` 异常
- 自动降级到轻量级算法

---

## 性能对比

### 克里金算法复杂度

| 数据点数 | 计算时间（估算） | 内存占用（估算） | 建议 |
|---------|----------------|----------------|------|
| 50 | <1秒 | ~10MB | ✅ 推荐 |
| 100 | ~3秒 | ~40MB | ✅ 安全 |
| 200 | ~15秒 | ~150MB | ⚠️ 谨慎 |
| 500 | ~2分钟 | ~1GB | ⚠️ 限制 |
| 1000 | ~15分钟 | ~4GB | ❌ 禁止 |

### 优化效果

**优化前**：
- 1000个数据点 → 内存溢出/超时

**优化后**：
- 1000个数据点 → 自动降采样到500个 → 2分钟完成
- 500个以下 → 直接计算
- 失败 → 自动回退到RBF/线性插值

---

## 服务器部署步骤

### 步骤 1: 更新代码

```bash
# SSH 登录服务器
ssh user@your-server

# 进入项目目录
cd /path/to/xitong

# 拉取最新代码
git pull origin master
```

### 步骤 2: 安装依赖

```bash
# 进入后端目录
cd backend

# 激活虚拟环境（如果有）
source venv/bin/activate  # Linux
# 或
conda activate xitong     # Conda

# 安装/更新依赖
pip install -r requirements.txt

# 验证安装
python -c "import pykrige; print('pykrige version:', pykrige.__version__)"
```

### 步骤 3: 重启服务

```bash
# 如果使用 systemd
sudo systemctl restart xitong-backend

# 如果使用 Docker
docker-compose restart backend

# 如果手动启动
# 先停止旧进程，然后启动新进程
pkill -f "uvicorn server:app"
nohup uvicorn server:app --host 0.0.0.0 --port 8000 &
```

### 步骤 4: 验证功能

1. 访问 API 文档：`http://your-server:8000/docs`
2. 测试克里金插值接口
3. 检查日志输出：
   ```bash
   # 查看是否有 [KRIGING] 相关日志
   tail -f /path/to/logs/backend.log
   ```

---

## 日志说明

### 正常日志

```
[KRIGING] 🔧 使用spherical变差模型，数据点=245
[KRIGING] ✓ 克里金插值完成
```

### 降采样日志

```
[KRIGING] ⚠️ 数据点过多(856 > 500)，使用降采样
[KRIGING] ✓ 降采样完成，使用500个数据点
[KRIGING] 🔧 使用spherical变差模型，数据点=500
[KRIGING] ✓ 克里金插值完成
```

### 回退日志

```
[KRIGING] ⚠️ pykrige未安装，使用高斯RBF近似
[KRIGING-FALLBACK] 使用高斯RBF近似，数据点=245
[KRIGING-FALLBACK] ⚠️ 裁剪12个异常值
```

### 错误日志

```
[KRIGING] ✗ 内存不足: Cannot allocate memory
[KRIGING-FALLBACK] 使用高斯RBF近似，数据点=500
```

---

## 常见问题

### Q1: 为什么本地正常，服务器报错？

**A**: 可能原因：
1. 服务器未安装 `pykrige` → 安装依赖
2. 服务器内存较小 → 已自动降采样
3. 服务器 CPU 较慢 → 计算时间较长，耐心等待

### Q2: 降采样会影响结果吗？

**A**: 
- **轻微影响**：对于密集均匀分布的数据，影响较小
- **显著影响**：如果数据分布不均匀，可能丢失局部细节
- **建议**：优先使用其他插值方法（如 cubic、idw）处理大数据集

### Q3: 如何禁用降采样？

**A**: 修改 `backend/interpolation.py`：

```python
# 找到这行
MAX_KRIGING_POINTS = 500

# 修改为更大的值（需要确保服务器有足够内存）
MAX_KRIGING_POINTS = 1000  # 风险：可能内存溢出
```

### Q4: 克里金插值一直失败怎么办？

**A**: 系统会自动回退到：
1. 高斯RBF近似（效果接近克里金）
2. 线性插值（保底方案）

可以直接使用其他插值方法：
- `cubic` - 三次样条（快速、平滑）
- `idw` - 反距离加权（稳定、保守）
- `multiquadric` - 多二次RBF（全局平滑）

---

## 推荐配置

### 小数据集（<100个点）
- ✅ 使用 `ordinary_kriging`
- 分辨率：150-200

### 中等数据集（100-500个点）
- ✅ 使用 `ordinary_kriging`（自动优化）
- ⚠️ 分辨率：100-150（避免过高）

### 大数据集（>500个点）
- ⚠️ `ordinary_kriging` 会自动降采样
- ✅ 推荐改用 `cubic` 或 `idw`
- 分辨率：80-100

---

## 性能调优建议

### 服务器端优化

1. **增加内存**：
   - 推荐：至少 4GB RAM
   - 理想：8GB+ RAM

2. **使用缓存**：
   - 系统已实现插值结果缓存
   - 相同参数不会重复计算

3. **并发限制**：
   - 限制同时进行的克里金计算数量
   - 使用队列系统排队处理

### 客户端优化

1. **降低分辨率**：
   - 从 200 降到 100
   - 速度提升 4 倍

2. **选择合适的插值方法**：
   - 快速预览：`linear`
   - 平衡：`cubic`、`idw`
   - 精细：`ordinary_kriging`（小数据集）

3. **数据预处理**：
   - 移除冗余点
   - 均匀化采样

---

## 监控和调试

### 检查依赖

```bash
# 检查 pykrige 是否安装
pip show pykrige

# 检查版本
python -c "import pykrige; print(pykrige.__version__)"
```

### 查看日志

```bash
# 实时查看后端日志
tail -f /var/log/xitong/backend.log

# 过滤克里金相关日志
grep "KRIGING" /var/log/xitong/backend.log
```

### 性能监控

```bash
# 监控内存使用
watch -n 1 "ps aux | grep python | grep uvicorn"

# 监控 CPU
top -p $(pgrep -f "uvicorn server:app")
```

---

**最后更新**: 2025年11月25日
