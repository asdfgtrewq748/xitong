"""
测试所有插值方法,验证结果范围是否合理
"""
import sys
import os
sys.path.insert(0, 'backend')

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from interpolation import interpolate
import numpy as np

# 创建测试数据 - 模拟地层厚度
np.random.seed(42)
n_points = 15
x = np.random.rand(n_points) * 1000  # 0-1000m范围
y = np.random.rand(n_points) * 800   # 0-800m范围
z = np.random.rand(n_points) * 15 + 5  # 5-20m厚度

# 创建插值网格
xi = np.linspace(0, 1000, 30)
yi = np.linspace(0, 800, 30)

print("="*60)
print("地质建模插值方法测试")
print("="*60)
print(f"测试数据: {n_points}个数据点")
print(f"厚度范围: {z.min():.2f}m - {z.max():.2f}m")
print(f"厚度平均值: {z.mean():.2f}m")
print(f"插值目标: {len(xi)}个点")
print("="*60)

# 测试所有方法
methods = [
    'linear',
    'nearest', 
    'cubic',
    'modified_shepard',
    'idw',
    'natural_neighbor',
    'multiquadric',
    'gaussian',
    'thin_plate',
    'linear_rbf',
    'cubic_rbf',
    'quintic_rbf',
    'anisotropic',
    'ordinary_kriging',
    'universal_kriging',
]

results = {}

for method in methods:
    print(f"\n测试方法: {method}")
    print("-" * 40)
    try:
        result = interpolate(x, y, z, xi, yi, method)
        results[method] = result
        
        # 检查结果
        r_min, r_max = result.min(), result.max()
        r_mean = result.mean()
        
        print(f"[OK] 成功!")
        print(f"   结果范围: {r_min:.2f}m - {r_max:.2f}m")
        print(f"   结果平均: {r_mean:.2f}m")
        
        # 检查是否有异常外推
        safe_min = z.min() - (z.max() - z.min()) * 0.5
        safe_max = z.max() + (z.max() - z.min()) * 0.5
        
        if r_min < safe_min or r_max > safe_max:
            print(f"   [WARN] 结果超出安全范围 [{safe_min:.2f}, {safe_max:.2f}]")
        else:
            print(f"   [PASS] 结果在合理范围内")
            
    except Exception as e:
        print(f"[FAIL] {str(e)[:100]}")

print("\n" + "="*60)
print("汇总对比")
print("="*60)
print(f"{'方法':<20} {'最小值':<12} {'最大值':<12} {'平均值':<12}")
print("-" * 60)
for method, result in results.items():
    print(f"{method:<20} {result.min():<12.2f} {result.max():<12.2f} {result.mean():<12.2f}")

print("\n原始数据参考:")
print(f"{'原始数据':<20} {z.min():<12.2f} {z.max():<12.2f} {z.mean():<12.2f}")
print("="*60)
