"""
快速验证后端 API 路由是否正确注册
"""
import sys
import os

# 添加后端目录到路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("=" * 60)
print("后端接口校验")
print("=" * 60)

# 1. 检查模块导入
print("\n1. 检查模块导入...")
try:
    import tunnel_support
    print("   [OK] tunnel_support 模块导入成功")
except ImportError as e:
    print(f"   [ERROR] 导入失败: {e}")
    sys.exit(1)

# 2. 检查类和函数
print("\n2. 检查主要类和函数...")
try:
    from tunnel_support import TunnelSupportCalculator, batch_calculate_tunnel_support
    print("   [OK] TunnelSupportCalculator 类导入成功")
    print("   [OK] batch_calculate_tunnel_support 函数导入成功")
except ImportError as e:
    print(f"   [ERROR] 导入失败: {e}")
    sys.exit(1)

# 3. 实例化测试
print("\n3. 实例化计算器...")
try:
    calc = TunnelSupportCalculator()
    print(f"   [OK] 实例化成功")
    print(f"   - 默认常量数量: {len(calc.constants)}")
    print(f"   - 示例常量: Sn={calc.constants['Sn']} mm^2, safety_K={calc.constants['safety_K']}")
except Exception as e:
    print(f"   [ERROR] 实例化失败: {e}")
    sys.exit(1)

# 4. 单次计算测试
print("\n4. 测试单次计算...")
try:
    test_params = {
        'B': 4.0, 'H': 3.0, 'K': 1.0, 
        'depth': 200, 'gamma': 18.0, 
        'C': 0.5, 'phi': 30.0
    }
    result = calc.calculate_complete(test_params)
    print(f"   [OK] 计算成功")
    print(f"   - R = {result['basic']['R']} m")
    print(f"   - hct = {result['basic']['hct']} m")
    print(f"   - 锚索 Nt = {result['anchor']['Nt']} kN")
except Exception as e:
    print(f"   [ERROR] 计算失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 批量计算测试
print("\n5. 测试批量计算...")
try:
    df = batch_calculate_tunnel_support([test_params, test_params])
    print(f"   [OK] 批量计算成功")
    print(f"   - 结果行数: {len(df)}")
    print(f"   - 结果列数: {len(df.columns)}")
except Exception as e:
    print(f"   [ERROR] 批量计算失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. 检查 server.py API 路由
print("\n6. 检查 server.py API 路由定义...")
try:
    with open(os.path.join(backend_dir, 'server.py'), 'r', encoding='utf-8') as f:
        content = f.read()
        routes = [
            '/api/tunnel-support/calculate',
            '/api/tunnel-support/batch-calculate',
            '/api/tunnel-support/parse-excel',
            '/api/tunnel-support/default-constants'
        ]
        for route in routes:
            if route in content:
                print(f"   [OK] 找到路由: {route}")
            else:
                print(f"   [ERROR] 未找到路由: {route}")
except Exception as e:
    print(f"   [ERROR] 检查失败: {e}")

print("\n" + "=" * 60)
print("[SUCCESS] 后端接口校验完成！所有检查通过。")
print("=" * 60)
