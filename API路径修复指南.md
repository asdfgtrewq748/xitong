# 🚨 API 路径问题紧急修复

## 问题描述

**错误信息：**
```
POST http://39.97.168.66/api/api/raw/import 404 (Not Found)
```

**问题原因：**
路径中出现了两个 `/api`，因为：
1. `getApiBase()` 返回 `/api`
2. 代码中又添加了 `/api/raw/import`
3. 结果变成：`/api` + `/api/raw/import` = `/api/api/raw/import` ❌

## 已修复的文件

### 1. `frontend/src/stores/globalData.js`

**修复前：**
```javascript
const baseUrl = getApiBase()  // 返回 '/api'
const resp = await fetch(`${baseUrl}/api/raw/import`, ...)  // ❌ /api/api/raw/import
```

**修复后：**
```javascript
const baseUrl = getApiBase()  // 返回 '/api'
const resp = await fetch(`${baseUrl}/raw/import`, ...)  // ✅ /api/raw/import
```

### 2. `frontend/src/utils/dataService.js`

**修复前：**
```javascript
this.baseURL = getApiBase()  // 返回 '/api'
fetch(`${this.baseURL}/api/upload-csv`, ...)  // ❌ /api/api/upload-csv
```

**修复后：**
```javascript
this.baseURL = getApiBase()  // 返回 '/api'
fetch(`${this.baseURL}/upload-csv`, ...)  // ✅ /api/upload-csv
```

## 服务器部署步骤

### 1. 提交代码（本地）

```bash
cd d:\xitong

git add frontend/src/stores/globalData.js frontend/src/utils/dataService.js
git commit -m "修复：移除 API 路径重复的 /api 前缀"
git push origin master
```

### 2. 服务器部署

```bash
# SSH 登录服务器
ssh root@39.97.168.66

# 进入项目目录
cd /root/xitong  # 或你的项目路径

# 拉取最新代码
git pull origin master

# 停止容器
docker-compose down

# 重新构建前端（必须 --no-cache）
docker-compose build --no-cache frontend

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs frontend --tail=50
```

### 3. 验证修复

```bash
# 检查容器状态
docker-compose ps

# 测试 API 路径
curl -X POST http://localhost/api/raw/import \
  -F "files=@test.csv" \
  2>&1 | grep -i "404\|200\|401"

# 应该返回 401 或其他非 404 错误（因为没有认证/文件）
# 404 说明路径还是错的
```

## 浏览器测试

1. **清除浏览器缓存**（重要！）
   ```
   Ctrl + Shift + Delete
   → 选择"缓存的图片和文件"
   → 清除数据
   ```

2. **强制刷新页面**
   ```
   Ctrl + F5
   ```

3. **测试数据导入**
   - 访问：http://39.97.168.66/data-management
   - 点击"批量导入"
   - 上传测试文件
   - 按 F12 查看 Network 标签

4. **检查请求 URL**
   应该看到：
   ```
   ✅ POST http://39.97.168.66/api/raw/import
   ❌ POST http://39.97.168.66/api/api/raw/import
   ```

## 预期结果

修复前后对比：

| 功能 | 修复前 | 修复后 |
|------|--------|--------|
| 数据导入 | `/api/api/raw/import` → 404 | `/api/raw/import` → 200/401 |
| 数据库查询 | `/api/api/database/records` → 404 | `/api/database/records` → 200 |
| CSV上传 | `/api/api/upload-csv` → 404 | `/api/upload-csv` → 200 |

## 时间估算

- 拉取代码：10 秒
- 停止容器：10 秒
- 重新构建：2-5 分钟
- 启动服务：30 秒
- **总计：约 3-6 分钟**

## 如果问题仍未解决

### 检查构建是否使用了新代码

```bash
# 进入前端容器
docker exec -it $(docker-compose ps -q frontend) sh

# 检查 JavaScript 文件的修改时间
ls -lh /usr/share/nginx/html/js/*.js

# 应该显示最新的时间（几分钟前）
```

### 查看构建日志

```bash
# 重新构建并保存日志
docker-compose build --no-cache frontend 2>&1 | tee build.log

# 检查是否有错误
grep -i "error\|failed" build.log
```

### 检查 nginx 代理配置

```bash
# 查看 nginx 配置
docker exec $(docker-compose ps -q frontend) cat /etc/nginx/conf.d/default.conf | grep -A 15 "location /api"

# 应该看到：
# location /api/ {
#     proxy_pass http://backend:8000/api/;
#     ...
# }
```

## 相关修复文档

- `服务器页面无法打开修复指南.md` - 代码分割问题
- `服务器紧急修复命令.md` - 快速命令参考
- `修复总结.md` - 完整修复历史

## 技术说明

### 为什么会出现这个问题？

1. **设计意图：** `getApiBase()` 应该返回完整的 API 基础路径，包括 `/api` 前缀
2. **历史遗留：** 旧代码中直接使用 `http://localhost:8000`，然后添加 `/api/...`
3. **修复冲突：** 将 `localhost:8000` 改为 `getApiBase()` 后，忘记移除 `/api` 前缀
4. **结果：** `/api` + `/api/raw/import` = `/api/api/raw/import`

### 正确的 API 路径构建方式

```javascript
// ✅ 方式 1：getApiBase() 已包含 /api
const baseUrl = getApiBase()  // '/api'
fetch(`${baseUrl}/raw/import`)  // '/api/raw/import'

// ✅ 方式 2：直接使用相对路径
fetch('/api/raw/import')

// ❌ 错误：重复添加 /api
const baseUrl = getApiBase()  // '/api'
fetch(`${baseUrl}/api/raw/import`)  // '/api/api/raw/import' ❌
```

## 修复完成标志

所有这些 URL 应该正常工作：
- ✅ `GET /api/health`
- ✅ `POST /api/raw/import`
- ✅ `GET /api/database/records`
- ✅ `POST /api/upload-csv`
- ✅ `GET /api/modeling/seams`
- ✅ `POST /api/modeling/contour`

---

**最后更新：** 2025年11月10日  
**问题：** API 路径重复导致 404 错误  
**解决：** 移除代码中重复的 `/api` 前缀
