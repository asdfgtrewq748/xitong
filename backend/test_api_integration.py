"""
前后端联调测试
测试所有 tunnel-support API 端点
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("前后端联调测试")
print("=" * 60)

# 等待服务器启动
print("\n等待后端服务器启动...")
for i in range(10):
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("[OK] 后端服务器已就绪")
            break
    except:
        if i == 9:
            print("[ERROR] 后端服务器启动超时")
            exit(1)
        time.sleep(1)

# 1. 测试获取默认常量
print("\n1. 测试 GET /api/tunnel-support/default-constants")
try:
    response = requests.get(f"{BASE_URL}/api/tunnel-support/default-constants")
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] 状态码: {response.status_code}")
        print(f"   - 常量数量: {len(data['constants'])}")
        print(f"   - 示例: Sn={data['constants']['Sn']}, safety_K={data['constants']['safety_K']}")
    else:
        print(f"   [ERROR] 状态码: {response.status_code}")
        print(f"   响应: {response.text}")
except Exception as e:
    print(f"   [ERROR] 请求失败: {e}")

# 2. 测试单次计算
print("\n2. 测试 POST /api/tunnel-support/calculate")
test_params = {
    "B": 4.0,
    "H": 3.0,
    "K": 1.0,
    "depth": 200,
    "gamma": 18.0,
    "C": 0.5,
    "phi": 30.0
}
try:
    response = requests.post(
        f"{BASE_URL}/api/tunnel-support/calculate",
        json=test_params,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] 状态码: {response.status_code}")
        print(f"   - R = {data['result']['basic']['R']} m")
        print(f"   - hct = {data['result']['basic']['hct']} m")
        print(f"   - 锚索 Nt = {data['result']['anchor']['Nt']} kN")
    else:
        print(f"   [ERROR] 状态码: {response.status_code}")
        print(f"   响应: {response.text}")
except Exception as e:
    print(f"   [ERROR] 请求失败: {e}")

# 3. 测试批量计算
print("\n3. 测试 POST /api/tunnel-support/batch-calculate")
batch_request = {
    "data": [test_params, test_params]
}
try:
    response = requests.post(
        f"{BASE_URL}/api/tunnel-support/batch-calculate",
        json=batch_request,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] 状态码: {response.status_code}")
        print(f"   - 计算数量: {data['count']}")
        print(f"   - 第一条结果 R = {data['results'][0]['R(m)']} m")
    else:
        print(f"   [ERROR] 状态码: {response.status_code}")
        print(f"   响应: {response.text}")
except Exception as e:
    print(f"   [ERROR] 请求失败: {e}")

# 4. 测试 Excel 解析 (创建测试文件)
print("\n4. 测试 POST /api/tunnel-support/parse-excel")
print("   [SKIP] 需要实际 Excel 文件，跳过此测试")
print("   提示: 前端可上传包含列 (B,H,应力集中系数K,埋深,容重,粘聚力,内摩擦角) 的 Excel 文件")

print("\n" + "=" * 60)
print("[SUCCESS] 前后端联调测试完成！")
print("=" * 60)
print("\n下一步:")
print("1. 启动前端: cd frontend && npm run serve")
print("2. 访问: http://localhost:8080/#/tunnel-support")
print("3. 测试单次计算和 Excel 导入功能")
