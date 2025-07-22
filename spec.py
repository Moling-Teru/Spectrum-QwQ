import os
import re
import datetime
import time as t
import sys
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import subprocess
import platform
import argparse
import multiprocessing
import psutil

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
# 智能计算最大线程数：考虑CPU核心数、内存和IO密集型任务特性
def calculate_optimal_workers():
    cpu_count = os.cpu_count()
    # 获取可用内存（GB）
    try:
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
    except:
        available_memory_gb = 8  # 默认假设8GB可用内存
    
    # 对于音频处理这种CPU+IO密集型任务，使用更多线程
    # 每个线程大约需要500MB-1GB内存处理音频
    memory_based_workers = max(1, int(available_memory_gb // 0.8))
    
    # CPU密集型建议使用CPU核心数的1.5-2倍（考虑超线程和IO等待）
    cpu_based_workers = int(cpu_count * 1.8)
    
    # 取较小值，但至少为CPU核心数
    optimal_workers = max(cpu_count, min(memory_based_workers, cpu_based_workers, 16))
    
    return optimal_workers

max_workers = calculate_optimal_workers()
thread_executor = None
processing_lock = threading.Lock()  # 用于保护计数器等共享变量

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
    """统一日志输出函数 - 线程安全"""
    # 使用锁保护控制台输出，避免输出混乱
    with processing_lock:
        print(message, end='')
    log_queue.put(message)

def set_max_workers(val):
    """设置最大线程数"""
    global max_workers
    # 确保线程数是整数，并且不超过合理上限
    max_workers = min(int(val), os.cpu_count() * 2, 32)  # 最多32个线程
    log_output(f"设置处理线程数: {max_workers}\n")

def process_music_file(name):
    """处理单个音乐文件的函数 - 优化版本"""
    global counter
    
    if not check_modules():
        log_output(f"错误: 缺少必要模块，无法处理文件 {name} - {MISSING_MODULE_ERROR}\n")
        return False, name
    
    # 导入需要的模块 - 在函数内导入以避免线程间冲突
    import stft_unified
    import stft_3000_detailed
    import power
    import power_plt
    import power_aweighted
    
    # 确保matplotlib线程安全
    import matplotlib
    matplotlib.use('Agg')  # 强制使用非交互式后端
    
    try:
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name_new = re.sub(r'[<>:"/\\|?*]', '', name).rsplit('.', 1)[0]  # 文件夹名称
        
        # 检查文件夹是否存在，如果存在则删除（确保重新处理）
        folder_path = f'data_stft/{name_new}'
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            log_output(f'{time_str}: 已删除 {name} 重新处理。\n')

        log_message = f'{time_str}: Processing file: {name}\n'
        log_output(log_message)
        
        # 创建目标文件夹
        os.makedirs(folder_path, exist_ok=True)
        
        # 创建日志文件路径
        log_file_path = f'log_stft/log_{name_new}'
        
        with open(log_file_path, 'a', encoding='utf-8') as file:
            file.write(f'{time_str}: Program Starting.\n')

            # 处理步骤函数，用于减少重复代码
            def process_step(step_name, func, input_path):
                if not is_running:
                    return False
                
                log_output(f'Processing {name}: {step_name}\n')
                try:
                    func(input_path)
                    step_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_msg = f'{step_time}: {step_name} Finished!\n'
                    file.write(log_msg)
                    log_output(log_msg)
                    return True
                except Exception as e:
                    error_msg = f'Error in {step_name} for {name}: {str(e)}\n'
                    log_output(error_msg)
                    file.write(error_msg)
                    return False

            # 执行各个处理步骤
            steps = [
                ("STFT Unified", stft_unified.main),
                ("STFT 3000 Detailed", stft_3000_detailed.main),
                ("Power CSV", power.main),
                ("Power PLT", power_plt.main),
                ("Power A-Weighted", power_aweighted.main)
            ]
            
            input_path = f"music_stft/{name}"
            
            for step_name, func in steps:
                if not process_step(step_name, func, input_path):
                    if is_running:  # 如果不是用户停止，则是处理错误
                        log_output(f"处理步骤 {step_name} 失败，跳过文件 {name}\n")
                    return False, name

        # 移动原始文件到处理后的目录
        try:
            shutil.move(f'music_stft/{name}', f'data_stft/{name_new}')
        except Exception as e:
            log_output(f"移动文件 {name} 时出错: {str(e)}\n")

        # 线程安全地更新计数器
        with processing_lock:
            counter += 1
            current_counter = counter

        log_output(f'Song-{name} Finished! [{current_counter}/{total_files}]\n')
        return True, name

    except Exception as e:
        error_msg = f"Error processing {name}: {str(e)}\n"
        log_output(error_msg)
        return False, name

def worker_function():
    """后台处理线程函数 - 优化版本"""
    global is_running, counter, thread_executor, max_workers
    
    try:
        # 确保目录存在
        required_dirs = ['data_stft', 'log_stft']
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.mkdir(directory)

        # 获取文件列表
        directory = 'music_stft'
        if not os.path.exists(directory):
            log_output(f"目录 '{directory}' 不存在，请先创建并放入音频文件\n")
            is_running = False
            return

        file_list = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        global total_files
        total_files = len(file_list)
        
        if total_files == 0:
            log_output(f"目录 '{directory}' 中没有音频文件\n")
            is_running = False
            return
        
        log_output(f"开始处理 {total_files} 个音乐文件...(使用 {max_workers} 个线程)\n")
        log_output(f"系统信息: CPU核心数={os.cpu_count()}, 可用内存={psutil.virtual_memory().available/(1024**3):.1f}GB\n")
        
        # 记录开始时间
        start_time = t.time()

        # 使用优化的线程池处理文件
        counter = 0
        successful_files = []
        failed_files = []
        
        # 设置线程池参数
        thread_executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="AudioProcessor"
        )
        
        try:
            # 提交所有任务
            future_to_file = {
                thread_executor.submit(process_music_file, name): name 
                for name in file_list
            }
            
            # 使用as_completed来处理完成的任务，提高响应性
            for future in as_completed(future_to_file):
                if not is_running:
                    # 如果用户停止了处理，取消所有未完成的任务
                    for f in future_to_file:
                        f.cancel()
                    break
                
                filename = future_to_file[future]
                try:
                    success, processed_file = future.result(timeout=300)  # 5分钟超时
                    if success:
                        successful_files.append(processed_file)
                    else:
                        failed_files.append(processed_file)
                        log_output(f"处理文件 {processed_file} 失败\n")
                        
                except Exception as e:
                    failed_files.append(filename)
                    log_output(f"处理文件 {filename} 时发生异常: {str(e)}\n")
                
                # 实时显示进度
                completed = len(successful_files) + len(failed_files)
                progress = (completed / total_files) * 100
                log_output(f"进度: {completed}/{total_files} ({progress:.1f}%) - 成功: {len(successful_files)}, 失败: {len(failed_files)}\n")
        
        finally:
            # 确保线程池正确关闭
            thread_executor.shutdown(wait=True, timeout=30)
        
        # 记录结束时间和统计信息
        end_time = t.time()
        delta_t = end_time - start_time
        
        if is_running:  # 如果不是由用户主动停止的
            completion_msg = f"处理完成!\n总共: {total_files} 个文件\n成功: {len(successful_files)} 个\n失败: {len(failed_files)} 个\n耗时: {delta_t:.3f}s\n平均每文件: {delta_t/total_files:.2f}s\n"
            if failed_files:
                completion_msg += f"失败的文件: {', '.join(failed_files)}\n"
            log_output(completion_msg)
            
            # 写入日志
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f'log_stft/log_main', 'a', encoding='utf-8') as file:
                file.write(f'{time_str}: Program Finished Successfully! Processed {len(successful_files)}/{total_files} files.\n')
        else:
            log_output("处理被用户中断\n")
            
            # 写入日志
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f'log_stft/log_main', 'a', encoding='utf-8') as file:
                file.write(f'{time_str}: Program Stopped by user! Processed {len(successful_files)}/{total_files} files.\n')
    
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
    optimal_workers = calculate_optimal_workers()
    parser = argparse.ArgumentParser(description='音频频谱分析工具 - 多线程优化版')
    parser.add_argument('command', nargs='?', choices=['start'], help='要执行的命令')
    parser.add_argument('-t', '--threads', type=int, default=optimal_workers,
                      help=f'处理线程数 (推荐: {optimal_workers}, 最大: {os.cpu_count() * 2})')
    parser.add_argument('--monitor', action='store_true',
                      help='启用系统资源监控')
    return parser.parse_args()

def monitor_system_resources():
    """监控系统资源使用情况"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        log_output(f"系统监控 - CPU: {cpu_percent:.1f}%, "
                  f"内存: {memory.percent:.1f}% ({memory.available/(1024**3):.1f}GB可用), "
                  f"磁盘: {disk.percent:.1f}%\n")
    except Exception as e:
        log_output(f"监控系统资源时出错: {str(e)}\n")

# 主程序入口
if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置线程数
    if args.threads:
        max_workers = min(args.threads, os.cpu_count() * 2, 32)  # 限制最大32个线程
        log_output(f"设置线程数为: {max_workers} (CPU核心数: {os.cpu_count()})\n")
    
    # 显示系统信息
    try:
        memory_info = psutil.virtual_memory()
        log_output(f"系统信息: CPU={os.cpu_count()}核心, 内存={memory_info.total/(1024**3):.1f}GB\n")
        log_output(f"推荐线程数: {calculate_optimal_workers()}, 当前设置: {max_workers}\n")
    except:
        log_output(f"当前线程设置: {max_workers}\n")
    
    # 如果指定了start命令，检查依赖并开始处理
    if args.command == 'start':
        # 检查依赖环境
        if not check_dependencies():
            log_output("\n依赖包检查失败，程序无法正常运行\n")
            sys.exit(1)

        # 检查并创建必要目录
        check_and_create_directories()
        
        # 启动系统监控（如果启用）
        monitor_thread = None
        if args.monitor:
            log_output("启用系统资源监控...\n")
            def monitor_loop():
                while is_running:
                    monitor_system_resources()
                    t.sleep(30)  # 每30秒监控一次
            
            monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
            monitor_thread.start()
        
        start_processing()
        
        # 停止监控线程
        if monitor_thread and monitor_thread.is_alive():
            monitor_thread.join(timeout=1)
    else:
        # 显示使用帮助
        log_output("音频频谱分析工具 - 多线程优化版\n")
        log_output("使用方法: python spec.py start [-t <线程数>] [--monitor]\n")
        log_output("示例: python spec.py start -t 12 --monitor\n")
        log_output(f"系统推荐线程数: {calculate_optimal_workers()}\n")
        log_output(f"当前CPU核心数: {os.cpu_count()}\n")
        log_output("请确保 'music_stft' 目录中已放入要处理的音频文件\n")
        if not check_modules():
            log_output(f"\n警告: 缺少必要的模块 - {MISSING_MODULE_ERROR}\n")
            log_output("请先安装依赖包: pip install -r requirements.txt\n")