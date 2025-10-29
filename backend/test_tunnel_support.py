#!/usr/bin/env python
"""测试 tunnel_support 模块"""
import sys
sys.path.insert(0, 'd:/xitong/backend')

try:
    import tunnel_support
    print("✓ tunnel_support 模块导入成功")
    
    from tunnel_support import TunnelSupportCalculator, batch_calculate_tunnel_support
    print("✓ 主要类和函数导入成功")
    
    calc = TunnelSupportCalculator()
    print(f"✓ 计算器实例化成功，默认常量: {len(calc.constants)} 项")
    
    # 测试单次计算
    test_params = {
        'B': 4.0,
        'H': 3.0,
        'K': 1.0,
        'depth': 200,
        'gamma': 18.0,
        'C': 0.5,
        'phi': 30.0
    }
    result = calc.calculate_complete(test_params)
    print(f"✓ 单次计算成功，R = {result['basic']['R']} m")
    
    # 测试批量计算
    df = batch_calculate_tunnel_support([test_params])
    print(f"✓ 批量计算成功，结果行数: {len(df)}")
    
    print("\n✅ 所有测试通过！")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
