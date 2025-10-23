# 项目文档索引

> 本目录包含所有项目相关的说明文档、优化指南和部署脚本。

## 📚 文档目录结构

```
docs/
├── INDEX.md (本文件)
├── backend/ (后端文档)
├── frontend/ (前端文档)
├── scripts/ (部署脚本)
└── *.md (各类说明文档)
```

## 📖 核心文档

### 快速开始
- **QUICKSTART.md** - 快速开始指南，新用户必读

### 修复文档
- **完整修复方案.md** - 数据库 API 错误修复完整方案
- **错误修复说明.md** - 详细的错误修复说明
- **数据库API修复总结.md** - 数据库 API 修复技术文档
- **测试清单.md** - 修复测试验证清单

### 功能增强
- **MODELING_IMPROVEMENTS.md** - 地质建模功能改进说明
- **HOMEPAGE_ENHANCEMENT.md** - 主页功能增强说明

### 优化指南
- **系统优化建议.txt** - 系统性能优化建议

### Docker 部署
- **DOCKER部署指南.md** - Docker 部署完整指南（推荐）
- **DOCKER_DEPLOYMENT.md** - Docker 部署配置
- **DOCKER_README.md** - Docker 使用说明
- **DOCKER_REGISTRY_FIX.md** - Docker 镜像仓库修复
- **Docker和自动化部署总结.txt** - 部署总结

## 🔧 后端文档 (backend/)

- **性能优化总结.md** - 后端性能优化总结
- **快速上手.md** - 后端开发快速上手
- **PERFORMANCE_GUIDE.md** - 性能优化详细指南
- **README_性能优化.txt** - 性能优化说明
- **requirements_performance.txt** - 性能优化相关依赖

## 🎨 前端文档 (frontend/)

- **前端性能优化指南.md** - 前端性能优化详细指南
- **前端优化总结.txt** - 前端优化总结
- **用户体验优化指南.md** - 用户体验优化详细指南
- **用户体验优化总结.txt** - 用户体验优化总结

## 📜 部署脚本 (scripts/)

### 备份脚本
- **backup.ps1** - Windows 备份脚本
- **backup.sh** - Linux/Mac 备份脚本

### 部署脚本
- **deploy.ps1** - Windows 部署脚本
- **deploy.sh** - Linux/Mac 部署脚本

### 维护脚本
- **fix-docker-registry.ps1** - Docker 镜像仓库修复脚本
- **health-check.sh** - 健康检查脚本
- **healthcheck.sh** - 健康检查脚本（备用）

## 🚀 快速导航

### 我是新用户
1. 📖 阅读 [../README.md](../README.md) - 项目主说明
2. 🚀 查看 [QUICKSTART.md](QUICKSTART.md) - 快速开始
3. 🐳 参考 [DOCKER部署指南.md](DOCKER部署指南.md) - 部署应用

### 我是开发者

#### Backend 开发
1. 📚 查看 [backend/快速上手.md](backend/快速上手.md)
2. ⚡ 参考 [backend/PERFORMANCE_GUIDE.md](backend/PERFORMANCE_GUIDE.md)
3. 📝 阅读 [backend/性能优化总结.md](backend/性能优化总结.md)

#### Frontend 开发
1. 🎨 查看 [frontend/前端性能优化指南.md](frontend/前端性能优化指南.md)
2. 💡 参考 [frontend/用户体验优化指南.md](frontend/用户体验优化指南.md)

### 我是运维人员
1. 🐳 部署: [DOCKER部署指南.md](DOCKER部署指南.md)
2. 📜 脚本: [scripts/](scripts/) 目录
3. ⚡ 优化: 性能优化相关文档

### 我遇到了问题
1. 🔍 查看 [错误修复说明.md](错误修复说明.md)
2. 📋 参考 [测试清单.md](测试清单.md)
3. 💾 查看 [完整修复方案.md](完整修复方案.md)

## 📂 项目根目录保留文件

以下重要文件保留在项目根目录：

- **README.md** - 项目主说明文档
- **启动代码** - 快速启动命令
- **requirements.txt** - Python 依赖
- **docker-compose.yml** - Docker 编排文件
- **Makefile** - 构建脚本

## 📝 文档维护说明

### 添加新文档
1. 根据文档类型放入对应目录
2. 更新本索引文件
3. 确保文档使用 UTF-8 编码

### 文档分类规则
- **根目录**: 核心说明文档
- **backend/**: 后端相关文档
- **frontend/**: 前端相关文档
- **scripts/**: 可执行脚本

## 📊 整理统计

- ✅ 移动文档: 22 个
- ✅ 移动脚本: 7 个
- ✅ 删除临时文件: 11 个
- ✅ 创建目录: 4 个

## 📅 更新日志

- **2025-10-20**: 完成项目文档整理
  - 创建 docs 目录结构
  - 移动所有说明文档
  - 清理临时测试文件
  - 创建文档索引

---

**返回项目根目录**: [../README.md](../README.md)  
**最后更新**: 2025年10月20日
