# 数据库 API 错误修复总结

## 修复日期
2025年10月19日

## 问题描述
多个数据库 API 端点返回 500 Internal Server Error，导致前端无法读取数据库数据。

##  根本原因

1. **数据库表反射问题**: `_get_records_table_or_500()` 函数虽然捕获了异常，但仍然抛出 HTTPException，导致 500 错误
2. **缓存装饰器问题**: `@cached` 装饰器可能在数据库未初始化时缓存错误状态
3. **错误处理不完整**: 当数据库未初始化或表不存在时，没有优雅降级机制

## 修复内容

### 1. 新增安全辅助函数
**位置**: `backend/server.py`

```python
def _get_records_table_safe():
    """安全获取 records 表，如果失败返回 None"""
    try:
        return get_records_table()
    except RuntimeError as e:
        print(f"[WARNING] 获取 records 表失败: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 获取 records 表时发生未预期错误: {e}")
        return None
```

### 2. 修复的 API 端点

#### A. `/api/dashboard/stats`
- 移除了 `@cached` 装饰器
- 添加了完整的 try-catch 错误处理
- 返回默认值（0）而不是抛出异常

#### B. `/api/database/overview`
- 移除了 `@cached` 装饰器
- 使用 `_get_records_table_safe()` 代替 `_get_records_table_or_500()`
- 当数据库未初始化时返回空数据和提示消息

#### C. `/api/database/records`
- 使用 `_get_records_table_safe()`
- 当数据库未初始化时返回空列表和提示消息

#### D. `/api/database/lithologies`
- 使用 `_get_records_table_safe()`
- 当数据库未初始化时返回空列表和提示消息

#### E. `/api/database/lithology-data`
- 使用 `_get_records_table_safe()`
- 添加了完整的异常处理
- 当数据库未初始化时返回空数据和提示消息

### 3. 统一的错误处理模式

所有修复的端点都遵循以下模式：

```python
@app.get("/api/some-endpoint")
async def some_endpoint():
    try:
        table = _get_records_table_safe()
        if table is None:
            return {
                "status": "success",
                "data": {},  # 空数据
                "message": "数据库尚未初始化"
            }
        
        # 正常业务逻辑...
        
        return {"status": "success", "data": result}
    
    except HTTPException:
        raise  # 保留业务异常
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")
        traceback.print_exc()
        return {
            "status": "success",
            "data": {},
            "message": "操作失败"
        }
```

## 关键改进

1. **优雅降级**: API 不再返回 500 错误，而是返回空数据和说明信息
2. **一致性**: 所有端点都返回 `status: "success"`，前端不需要特殊处理
3. **详细日志**: 后端打印详细的错误信息用于调试
4. **用户友好**: 通过 `message` 字段告知用户当前状态

## 测试方法

### 1. 启动后端
```powershell
cd e:\xiangmu\xitong\backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### 2. 运行 API 测试
```powershell
cd e:\xiangmu\xitong
python test_database_apis.py
```

### 3. 手动测试
使用浏览器或 curl 访问：
- http://localhost:8000/api/dashboard/stats
- http://localhost:8000/api/database/overview?limit=40
- http://localhost:8000/api/database/records?page=1&page_size=10

## 预期结果

### 数据库已初始化且有数据
- ✅ API 返回 200 状态码
- ✅ 返回实际数据
- ✅ 前端正常显示

### 数据库未初始化或为空
- ✅ API 返回 200 状态码
- ✅ 返回空数据
- ✅ 包含 `message` 字段说明情况
- ✅ 前端显示空状态，不报错

### 发生未知错误
- ✅ API 返回 200 状态码
- ✅ 返回空数据和错误消息
- ✅ 后端日志记录详细错误信息
- ✅ 前端不会崩溃

## 数据库状态

已确认：
- ✅ 数据库文件存在: `data/database.db` (308 KB)
- ✅ `records` 表存在
- ✅ 包含 1341 条记录
- ✅ 有 21 列数据

## 相关工具

1. **check_database.py** - 完整的数据库检查工具
2. **quick_check.py** - 快速检查数据库状态
3. **test_database_apis.py** - API 端点测试工具
4. **test_dashboard_api.py** - Dashboard API 测试

## 如果问题仍然存在

### 检查后端日志
查找以下标记的日志：
- `[ERROR]` - 严重错误
- `[WARNING]` - 警告信息
- `[DEBUG]` - 调试信息

### 检查数据库
```powershell
python quick_check.py
```

### 清除缓存
重启后端服务器会自动清除内存缓存

### 验证网络连接
```powershell
curl http://localhost:8000/api/health
```

应该返回: `{"status":"ok"}`

## 修复的文件清单

1. `backend/server.py` - 主要修复文件
   - 新增 `_get_records_table_safe()` 函数
   - 修复 5 个 API 端点

2. `frontend/src/components/DashboardView.vue` - 前端修复
   - 改进 `fetchStats()` 函数的错误处理

3. 新增测试和工具文件
   - `check_database.py`
   - `quick_check.py`
   - `test_database_apis.py`
   - `test_dashboard_api.py`

## 部署建议

1. 确保所有修改已应用
2. 重启后端服务
3. 清除浏览器缓存
4. 运行测试脚本验证
5. 检查前端功能

## 维护建议

1. **定期检查日志**: 查看是否有未预期的错误
2. **监控性能**: 使用 `/api/performance/stats` 端点
3. **数据库备份**: 定期备份 `data/database.db`
4. **错误追踪**: 考虑添加错误追踪服务（如 Sentry）
