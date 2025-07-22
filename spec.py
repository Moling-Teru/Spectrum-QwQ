import os
import re
import datetime
import time as t
import sys
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import subprocess
import platform
import argparse

# 延迟导入标志
MODULES_AVAILABLE = None
MISSING_MODULE_ERROR = None

def check_modules():
    """检查模块是否可用"""
    global MODULES_AVAILABLE, MISSING_MODULE_ERROR
    if MODULES_AVAILABLE is not None:
        return MODULES_AVAILABLE
    
    try:
        import music_format
        import stft_unified
        import stft_3000_detailed
        import power
        import power_plt
        import power_aweighted
        import encryption
        MODULES_AVAILABLE = True
        return True
    except ImportError as e:
        MODULES_AVAILABLE = False
        MISSING_MODULE_ERROR = str(e)
        return False

# 创建一个队列用于线程间通信
log_queue = queue.Queue()

# 全局变量
is_running = False
counter = 0
total_files = 0
max_workers = min(os.cpu_count(), 4)  # 默认最大线程数，不超过CPU核心数，默认为4
thread_executor = None

class ConsoleLogger:
    def __init__(self):
        """控制台日志输出"""
        pass

    def write(self, string):
        """直接写入控制台"""
        print(string, end='')
        
    def flush(self):
        """刷新缓冲区"""
        sys.stdout.flush()

def check_and_create_directories():
    """检查并创建必要的目录"""
    required_dirs = ['music_stft', 'data_stft', 'log_stft']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"已创建目录: {directory}")
        else:
            print(f"目录已存在: {directory}")

def format_files():
    """格式化音乐文件"""
    if not check_modules():
        print(f"错误: 缺少必要模块，无法执行格式化 - {MISSING_MODULE_ERROR}")
        return
    
    import music_format
    music_format.main()
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f'{time_str}: Format Finished.\n'
    
    # 确保目录存在
    if not os.path.exists('log_stft'):
        os.mkdir('log_stft')
        
    with open(f'log_stft/log_main', 'a', encoding='utf-8') as file:
        file.write(log_message)
    
    log_output(log_message)


def encry():
    """解密文件"""
    if not check_modules():
        print(f"错误: 缺少必要模块，无法执行解密 - {MISSING_MODULE_ERROR}")
        return
    
    import encryption
    encryption.main()
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f'{time_str}: Encryption Finished.\n'

    # 确保目录存在
    if not os.path.exists('log_stft'):
        os.mkdir('log_stft')

    with open(f'log_stft/log_main', 'a', encoding='utf-8') as file:
        file.write(log_message)

    log_output(log_message)

def log_output(message):
    """统一日志输出函数"""
    print(message, end='')
    log_queue.put(message)

def set_max_workers(val):
    """设置最大线程数"""
    global max_workers
    # 确保线程数是整数，并且不超过CPU核心数
    max_workers = min(int(val), os.cpu_count())
    print(f"设置处理线程数: {max_workers}")

def process_music_file(name):
    """处理单个音乐文件的函数"""
    global counter
    
    if not check_modules():
        log_output(f"错误: 缺少必要模块，无法处理文件 {name} - {MISSING_MODULE_ERROR}\n")
        return False
    
    # 导入需要的模块
    import stft_unified
    import stft_3000_detailed
    import power
    import power_plt
    import power_aweighted
    
    try:
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name_new = re.sub(r'[<>:"/\\|?*]', '', name).rsplit('.', 1)[0]  # 文件夹名称
        if os.path.exists(f'data_stft/{name_new}'):  # 检查文件夹是否存在
            shutil.rmtree(f'data_stft/{name_new}')  # 删除文件
            log_output(f'{time_str}: 已删除 {name} 重新处理。\n')

        log_message = f'{time_str}: Processing file: {name}\n'
        log_output(log_message)
        
        with open(f'log_stft/log_{name_new}', 'a', encoding='utf-8') as file:
            file.write(f'{time_str}: Program Starting.\n')
            folder = f'data_stft/{name_new}'  # 目标文件夹
            os.makedirs(folder, exist_ok=True)

            # 执行STFT处理
            if not is_running:
                return False

            log_output(f'Processing {name}: STFT Unified\n')
            stft_unified.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT Finished!\n'
            file.write(log_msg)
            log_output(log_msg)

            # 检查是否停止
            if not is_running:
                return False

            log_output(f'Processing {name}: STFT 3000 Detailed\n')
            stft_3000_detailed.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-3000 Finished!\n'
            file.write(log_msg)
            log_output(log_msg)

            # 检查是否停止
            if not is_running:
                return False

            log_output(f'Processing {name}: Power CSV\n')
            power.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-Power-Csv Finished!\n'
            file.write(log_msg)
            log_output(log_msg)

            # 检查是否停止
            if not is_running:
                return False

            log_output(f'Processing {name}: Power PLT\n')
            power_plt.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-Power-Plt Finished!\n'
            file.write(log_msg)
            log_output(log_msg)

            # 检查是否停止
            if not is_running:
                return False

            log_output(f'Processing {name}: Power A-Weighted\n')
            power_aweighted.main(f"music_stft/{name}")
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-Power-Plt-A-Weighting Finished!\n'
            file.write(log_msg)
            log_output(log_msg)

        # 移动原始文件到处理后的目录
        shutil.move(f'music_stft/{name}', f'data_stft/{name_new}')

        # 更新计数器并显示进度
        counter += 1
        log_output(f'Song-{name} Finished! [{counter}/{total_files}]\n')

        return True
    except Exception as e:
        error_msg = f"Error processing {name}: {str(e)}\n"
        log_output(error_msg)
        return False

def worker_function():
    """后台处理线程函数"""
    global is_running, counter, thread_executor, max_workers
    
    try:
        # 确保目录存在
        if not os.path.exists('data_stft'):
            os.mkdir('data_stft')
        if not os.path.exists('log_stft'):
            os.mkdir('log_stft')

        # 获取文件列表
        directory = 'music_stft'
        if not os.path.exists(directory):
            log_output(f"目录 '{directory}' 不存在，请先创建并放入音频文件\n")
            is_running = False
            return

        file_list = os.listdir(directory)
        global total_files
        total_files = len(file_list)
        
        if total_files == 0:
            log_output(f"目录 '{directory}' 中没有音频文件\n")
            is_running = False
            return
        
        log_output(f"开始处理 {total_files} 个音乐文件...(使用 {max_workers} 个线程)\n")
        
        # 记录开始时间
        start_time = t.time()

        # 使用线程池处理文件
        counter = 0
        thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        futures = []
        
        for name in file_list:
            if not is_running:
                break
            # 将任务提交到线程池
            future = thread_executor.submit(process_music_file, name)
            futures.append(future)
        
        # 等待所有任务完成
        for future in futures:
            if not is_running:
                break
            try:
                result = future.result()
                if not result and is_running:  # 如果处理失败但未主动停止
                    log_output(f"处理文件时失败，已跳过\n")
            except Exception as e:
                log_output(f"处理任务异常: {str(e)}\n")
        
        # 记录结束时间
        end_time = t.time()
        delta_t = end_time - start_time
        
        if is_running:  # 如果不是由用户主动停止的
            completion_msg = f"所有文件处理完成! \n总共处理了 {counter} 个文件.\n耗时{delta_t:.3f}s.\n"
            log_output(completion_msg)
            
            # 写入日志
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f'log_stft/log_main', 'a', encoding='utf-8') as file:
                file.write(f'{time_str}: Program Finished Successfully!\n')
        else:
            log_output("处理被用户中断\n")
            
            # 写入日志
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f'log_stft/log_main', 'a', encoding='utf-8') as file:
                file.write(f'{time_str}: Program Stopped by user!\n')
    
    except Exception as e:
        log_output(f"处理过程中发生错误: {str(e)}\n")
    
    finally:
        # 关闭线程池
        if thread_executor:
            thread_executor.shutdown(wait=False)
        
        is_running = False

def start_processing():
    """开始处理"""
    global is_running, counter
    
    if not check_modules():
        print(f"错误: 缺少必要的模块 - {MISSING_MODULE_ERROR}")
        print("请先安装依赖包: pip install -r requirements.txt")
        return
    
    if is_running:
        return
    
    # 重置状态
    is_running = True
    counter = 0
    
    print("开始音频处理...")
    
    # 解密文件
    print("执行解密...")
    encry()
    
    # 格式化音乐文件
    print("执行格式化...")
    format_files()
    
    # 启动工作线程
    worker_thread = threading.Thread(target=worker_function)
    worker_thread.daemon = True
    worker_thread.start()
    
    # 等待处理完成
    worker_thread.join()

def check_ffmpeg():
    """检查FFmpeg是否可用（跨平台）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 检查多个可能的FFmpeg位置
    possible_paths = [
        # 当前目录下的ffmpeg子目录
        os.path.join(script_dir, 'ffmpeg', 'bin', 'ffmpeg'),
        os.path.join(script_dir, 'ffmpeg', 'ffmpeg'),
        # 系统PATH中的ffmpeg
        'ffmpeg'
    ]

    # Windows特定路径
    if platform.system() == "Windows":
        possible_paths.extend([
            os.path.join(script_dir, 'ffmpeg', 'bin', 'ffmpeg.exe'),
            os.path.join(script_dir, 'ffmpeg', 'ffmpeg.exe'),
            r'C:\Windows\ffmpeg.exe'
        ])

    for ffmpeg_path in possible_paths:
        try:
            # 尝试运行ffmpeg -version来检查是否可用
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            continue

    return False

def check_dependencies():
    """检查依赖环境"""
    if not check_ffmpeg():
        system = platform.system()
        if system == "Windows":
            error_msg = "错误: 未检测到 ffmpeg。请先安装 ffmpeg 或将其放到脚本目录下的 'ffmpeg' 子目录中，或在 C:\\Windows 下放置 ffmpeg.exe"
        else:
            error_msg = "错误: 未检测到 ffmpeg。请安装 ffmpeg：\n" + \
                       "Ubuntu/Debian: sudo apt install ffmpeg\n" + \
                       "CentOS/RHEL: sudo yum install ffmpeg\n" + \
                       "macOS: brew install ffmpeg"
        print(error_msg)
        sys.exit(1)
        return False
    return True

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='音频频谱分析工具')
    parser.add_argument('command', nargs='?', choices=['start'], help='要执行的命令')
    parser.add_argument('-t', '--threads', type=int, default=max_workers,
                      help=f'处理线程数 (默认: {max_workers}, 最大: {os.cpu_count()})')
    return parser.parse_args()

# 主程序入口
if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置线程数
    if args.threads:
        max_workers = min(args.threads, os.cpu_count())
        print(f"设置线程数为: {max_workers}")
    
    # 如果指定了start命令，检查依赖并开始处理
    if args.command == 'start':
        # 检查依赖环境
        if not check_dependencies():
            print("\n依赖包检查失败，程序无法正常运行")
            sys.exit(1)

        # 检查并创建必要目录
        check_and_create_directories()
        
        start_processing()
    else:
        # 显示使用帮助
        print("音频频谱分析工具")
        print("使用方法: python spec.py start [-t <线程数>]")
        print("示例: python spec.py start -t 8")
        print(f"当前最大线程数: {os.cpu_count()}")
        print("请确保 'music_stft' 目录中已放入要处理的音频文件")
        if not check_modules():
            print(f"\n警告: 缺少必要的模块 - {MISSING_MODULE_ERROR}")
            print("请先安装依赖包: pip install -r requirements.txt")