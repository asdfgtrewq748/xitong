# Docker 镜像源配置修复指南

## 问题描述

Docker构建失败,错误信息: `404 Not Found` from `docker.m.daocloud.io`

## 解决方案

### 方法一: 使用官方Docker Hub (推荐,如果网络允许)

1. **打开Docker Desktop设置**
   - 点击Docker Desktop图标
   - 点击Settings (设置)

2. **移除失效的镜像源**
   - 进入 Docker Engine
   - 删除或注释掉 `docker.m.daocloud.io`

3. **使用以下配置** (保存并重启Docker):

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.baidubce.com",
    "https://dockerproxy.com"
  ]
}
```

### 方法二: 使用阿里云镜像加速器 (推荐国内用户)

1. 访问 https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
2. 登录阿里云账号
3. 获取专属加速器地址
4. 在Docker Desktop的Docker Engine中配置:

```json
{
  "registry-mirrors": [
    "https://你的专属地址.mirror.aliyuncs.com",
    "https://dockerproxy.com"
  ]
}
```

### 方法三: 暂时不使用镜像加速

Docker Desktop → Settings → Docker Engine:

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false
}
```

## 配置步骤 (详细)

### Windows Docker Desktop:

1. **打开Docker Desktop**
2. **点击右上角的设置图标** ⚙️
3. **选择 "Docker Engine"**
4. **编辑JSON配置**:

**推荐配置 (2025年可用的镜像源):**

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.baidubce.com"
  ]
}
```

5. **点击 "Apply & Restart"** (应用并重启)
6. **等待Docker重启完成** (约30秒)

## 验证配置

打开PowerShell,运行:

```powershell
docker info | Select-String "Registry Mirrors" -Context 0,5
```

应该看到新配置的镜像源。

## 重新运行部署

配置完成后,重新运行:

```powershell
.\deploy.ps1
```

## 如果仍然失败

### 选项1: 直接从Docker Hub拉取 (不使用镜像)

完全移除 `registry-mirrors` 配置,直接连接Docker Hub (需要良好的国际网络)。

### 选项2: 手动拉取镜像

```powershell
# 拉取基础镜像
docker pull python:3.11-slim
docker pull node:18-alpine
docker pull nginx:alpine

# 然后重新运行部署
.\deploy.ps1
```

### 选项3: 使用代理

如果有HTTP代理,在Docker Desktop中配置:

Settings → Resources → Proxies

```
HTTP Proxy: http://your-proxy:port
HTTPS Proxy: http://your-proxy:port
```

## 推荐的镜像源列表 (2025年可用)

按优先级排序:

1. **dockerproxy.com** - 稳定可靠
2. **docker.mirrors.ustc.edu.cn** - 中科大镜像
3. **mirror.baidubce.com** - 百度云镜像
4. **阿里云专属加速器** - 需要注册,但最稳定

## 常见问题

**Q: 修改后还是失败?**
A: 完全重启Docker Desktop,甚至重启电脑

**Q: 所有镜像源都不可用?**
A: 尝试完全移除镜像源配置,直接连接官方Docker Hub

**Q: 网络太慢怎么办?**
A: 考虑使用VPN或代理,或者在网络条件好的时候执行

## 完成

配置好镜像源后,Docker构建速度应该会大幅提升! 🚀
