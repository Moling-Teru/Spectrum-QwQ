"""
Spectrum 分析工具主程序
此程序提供 GUI 界面来处理音频文件的频谱分析
"""

import sys
import os
import subprocess
import importlib.util

# 检查所需模块
required_modules = ['tkinter', 'numpy', 'matplotlib', 'scipy', 'psutil']
missing_modules = []

for module in required_modules:
    if importlib.util.find_spec(module) is None:
        missing_modules.append(module)

# 如果有缺失模块，提示安装
if missing_modules:
    print(f"缺少必要的模块: {', '.join(missing_modules)}")
    print("请使用以下命令安装:")
    print(f"pip install {' '.join(missing_modules)}")
    sys.exit(1)

def check_and_create_directories():
    """检查并创建必要的目录"""
    required_dirs = ['music_stft', 'data_stft', 'log_stft']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"已创建目录: {directory}")

if __name__ == "__main__":
    # 检查并创建必要的目录
    check_and_create_directories()
    
    # 导入并启动GUI
    try:
        # 方式一：直接导入模块
        import tkinter_app
        tkinter_app.main()
        # 方式二：如果上面失败，尝试执行文件
    except ImportError:
        pass