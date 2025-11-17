import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
import os
from pathlib import Path
import matplotlib as mpl

def set_chinese_font():
    """设置中文字体"""
    # Windows系统
    if os.name == 'nt':
        font_path = 'C:/Windows/Fonts/SimHei.ttf'  # 黑体
        if not os.path.exists(font_path):
            font_path = 'C:/Windows/Fonts/Microsoft YaHei.ttf'  # 尝试使用微软雅黑
    
    if os.path.exists(font_path):
        from matplotlib.font_manager import FontProperties
        font_prop = FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        print("警告：未找到合适的中文字体文件")
    
    # 通用设置
    plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

def create_3d_cloud_plot(df, save_dir):
    """创建并保存3D云图"""
    
    print("开始处理数据...")
    
    # 设置中文字体
    set_chinese_font()
    mpl.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['SimHei', 'DejaVu Sans', 'Arial Unicode MS'],
        'axes.unicode_minus': False,
    })
    plt.style.use('seaborn')

    # 获取支架列
    support_columns = [col for col in df.columns if col.endswith('#')]
    num_supports = len(support_columns)
    
    print(f"检测到{num_supports}个支架数据列")
    
    # 准备数据
    print("准备坐标数据...")
    x = np.arange(len(df))
    y = np.arange(1, num_supports + 1)
    z_data = df[support_columns].values

    print("创建网格点...")
    xi = np.linspace(x.min(), x.max(), 300)
    yi = np.linspace(y.min(), y.max(), 300)
    xi, yi = np.meshgrid(xi, yi)

    x_points, y_points = np.meshgrid(x, y)
    z_points = z_data.T

    print("正在进行数据插值...")
    zi = griddata((x_points.flatten(), y_points.flatten()), 
                 z_points.flatten(), 
                 (xi, yi), 
                 method='cubic')

    print("应用平滑处理...")
    from scipy.ndimage import gaussian_filter
    zi = gaussian_filter(zi, sigma=2)

    print("创建3D图形...")
    fig = plt.figure(figsize=(15, 10), dpi=300)
    ax = fig.add_subplot(111, projection='3d')

    custom_cmap = plt.cm.get_cmap('jet')
    
    print("绘制3D曲面...")
    surf = ax.plot_surface(xi, yi, zi, 
                          cmap=custom_cmap,    
                          alpha=0.9,
                          rstride=1,
                          cstride=1,
                          linewidth=0,
                          antialiased=True,
                          vmin=np.nanpercentile(zi, 5),
                          vmax=np.nanpercentile(zi, 95))

    # 设置标签字体
    font_dict = {'family': 'SimHei'}
    ax.set_xlabel(' ', fontsize=12, labelpad=10, fontdict=font_dict)
    ax.set_ylabel(' ', fontsize=12, labelpad=10, fontdict=font_dict)
    ax.set_zlabel(' ', fontsize=12, labelpad=10, fontdict=font_dict)
    
    ax.set_box_aspect((2.5, 2, 1.5))

    cbar = plt.colorbar(surf, 
                       label=' ', 
                       pad=0.1,
                       shrink=0.8,
                       aspect=20)
    cbar.ax.tick_params(labelsize=10)
    
    # 设置标题字体
    plt.title('液压支架工作阻力三维曲面图', fontsize=14, pad=20, fontdict=font_dict)

    print("正在保存不同角度的视图...")
    angles = [
        (20, 45),
        (30, 60),
        (40, 90),
        (20, 120),
        (60, 45),
    ]
    
    ax.set_facecolor('white')
    plt.rcParams['axes.grid'] = True
    ax.set_box_aspect((8, 3, 2))
    
    # 确保保存图片时使用正确的中文字体
    for i, (elev, azim) in enumerate(angles):
        ax.view_init(elev=elev, azim=azim)
        ax.dist = 10
        plt.savefig(
            save_dir / f'3d_cloud_view_{i+1}.png',
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.2,
            facecolor='white'
        )
        print(f"已保存视角 {i+1}: elev={elev}, azim={azim}")

    print("保存完整图形...")
    plt.savefig(
        save_dir / 'final_3d_cloud.png',
        dpi=300,
        bbox_inches='tight',
        pad_inches=0.2,
        facecolor='white'
    )
    plt.close()

    print("3D云图生成完成！")

# main() 函数保持不变

def main():
    try:
         # 创建保存目录（在example文件夹下）
        current_dir = Path(__file__).parent  # 获取当前脚本所在目录
        save_dir = current_dir / '3dyuntu'
        save_dir.mkdir(exist_ok=True)
        print(f"创建保存目录: {save_dir}")

        # 读取数据 - 修正路径计算
        print("读取数据文件...")
        data_path = current_dir.parent / 'data' / 'clean_data.csv'  # 只回退一级到timeseries目录
        
        # 检查文件是否存在
        if not data_path.exists():
            raise FileNotFoundError(f"找不到数据文件: {data_path}\n"
                                  f"当前脚本目录: {current_dir}\n"
                                  f"请确保数据文件位于正确位置")
        
        print(f"正在读取数据文件: {data_path}")
        df = pd.read_csv(data_path)
        
        # 生成并保存3D云图
        create_3d_cloud_plot(df, save_dir)
        
        print(f"\n所有文件已保存到: {save_dir.absolute()}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        print("错误详细信息:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()