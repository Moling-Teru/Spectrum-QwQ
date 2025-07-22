"""
matplotlib线程安全配置模块
确保matplotlib在多线程环境下安全运行
"""

import threading
import os

# 全局锁，用于保护matplotlib操作
_matplotlib_lock = threading.Lock()

def configure_matplotlib_for_threading():
    """配置matplotlib以支持多线程环境"""
    import matplotlib
    
    # 设置非交互式后端
    matplotlib.use('Agg')
    
    # 设置matplotlib不使用GUI
    os.environ['MPLBACKEND'] = 'Agg'
    
    # 禁用交互式模式
    import matplotlib.pyplot as plt
    plt.ioff()
    
    return True

def safe_matplotlib_operation(func, *args, **kwargs):
    """线程安全的matplotlib操作包装器"""
    with _matplotlib_lock:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Matplotlib operation failed: {e}")
            raise

class ThreadSafePlot:
    """线程安全的绘图类"""
    
    def __init__(self):
        configure_matplotlib_for_threading()
    
    def __enter__(self):
        _matplotlib_lock.acquire()
        import matplotlib.pyplot as plt
        self.plt = plt
        return self.plt
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # 确保图形被关闭，释放内存
            self.plt.close('all')
        finally:
            _matplotlib_lock.release()

# 使用示例：
# with ThreadSafePlot() as plt:
#     plt.figure(figsize=(10, 6))
#     plt.plot(data)
#     plt.savefig('output.png')
