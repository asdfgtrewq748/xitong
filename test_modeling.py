"""
测试脚本:验证3D建模功能
"""
import sys
sys.path.insert(0, 'backend')

import numpy as np
import pandas as pd
from coal_seam_blocks.modeling import build_block_models

# 创建测试数据
np.random.seed(42)
n_points = 50

# 生成随机钻孔数据
data = {
    'X': np.random.uniform(0, 100, n_points),
    'Y': np.random.uniform(0, 100, n_points),
    '岩层名称': np.random.choice(['煤1', '煤2', '砂岩'], n_points),
    '厚度/m': np.random.uniform(1, 5, n_points)
}
df = pd.DataFrame(data)

print("测试数据预览:")
print(df.head(10))
print(f"\n数据维度: {df.shape}")
print(f"岩层种类: {df['岩层名称'].unique()}")

# 定义简单的插值函数
def simple_interpolation(x, y, z, xi, yi):
    from scipy.interpolate import griddata
    return griddata((x, y), z, (xi, yi), method='linear')

# 测试构建块体模型
try:
    print("\n开始构建块体模型...")
    block_models, skipped, (XI, YI) = build_block_models(
        merged_df=df,
        seam_column='岩层名称',
        x_col='X',
        y_col='Y',
        thickness_col='厚度/m',
        selected_seams=['煤1', '煤2', '砂岩'],
        method_callable=simple_interpolation,
        resolution=30,
        base_level=0.0,
        gap_value=1.0
    )
    
    print(f"\n✅ 成功构建 {len(block_models)} 个块体模型")
    print(f"网格维度: XI.shape={XI.shape}, YI.shape={YI.shape}")
    
    for i, model in enumerate(block_models):
        print(f"\n模型 {i+1}: {model.name}")
        print(f"  - 数据点数: {model.points}")
        print(f"  - 平均厚度: {model.avg_thickness:.2f} m")
        print(f"  - 最大厚度: {model.max_thickness:.2f} m")
        print(f"  - 平均高程: {model.avg_height:.2f} m")
        print(f"  - 顶面维度: {model.top_surface.shape}")
        print(f"  - 底面维度: {model.bottom_surface.shape}")
    
    if skipped:
        print(f"\n⚠️ 跳过的岩层: {skipped}")
    
    # 测试数据格式转换 (模拟后端API的输出格式)
    print("\n测试数据格式转换 (用于前端)...")
    test_model = block_models[0]
    top_data = []
    for i in range(min(5, XI.shape[0])):  # 只测试前5行
        for j in range(min(5, XI.shape[1])):  # 只测试前5列
            x_val = float(XI[i, j])
            y_val = float(YI[i, j])
            z_val = float(test_model.top_surface[i, j])
            top_data.append([x_val, y_val, z_val])
    
    print(f"转换后的数据样本 (前25个点):")
    for point in top_data[:5]:
        print(f"  {point}")
    print(f"  ... (共 {len(top_data)} 个点)")
    
    print("\n✅ 所有测试通过!")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
