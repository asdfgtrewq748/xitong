# backend/main.py
import webview
import os
from api import Api

# 实例化API类，它将暴露给前端
api_instance = Api()

def get_entrypoint():
    """ 确定前端应用的入口点 """
    # 在生产模式（打包后），前端文件在 'frontend/dist' 目录
    if os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist', 'index.html')):
        print("INFO: Running in production mode")
        # pyinstaller打包后，相对路径会变化，需要这样定位
        return os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist', 'index.html')
    
    # 在开发模式，直接连接到Vue的开发服务器
    print("INFO: Running in development mode")
    return 'http://localhost:8080' # Vue CLI默认端口

if __name__ == '__main__':
    entry_point = get_entrypoint()

    # 创建PyWebView窗口
    window = webview.create_window(
        '矿山工程分析系统 v4.0 (Vue + PyWebView)',
        entry_point,
        js_api=api_instance, # 核心：将api_instance暴露给前端
        width=1600,
        height=900,
        min_size=(1200, 720),
        frameless=False # 可以设为True以自定义标题栏
    )

    # 启动应用，debug=True允许在前端右键打开“检查”
    webview.start(debug=True)