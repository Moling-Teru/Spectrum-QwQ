import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Scale
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
import psutil
import music_format
import stft_unified
import stft_3000_detailed
import power
import power_plt
import power_aweighted
import encryption

# 创建一个队列用于线程间通信
log_queue = queue.Queue()
process_queue = queue.Queue()

# 全局变量
is_running = False
pause_processing = False
worker_thread = None
cpu_thread = None
counter = 0
total_files = 0
max_workers = min(os.cpu_count(), 4)  # 默认最大线程数，不超过CPU核心数，默认为4
thread_executor = None

class RedirectText:
    def __init__(self, text_widget):
        """将标准输出重定向到文本部件"""
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        """写入文本"""
        self.buffer += string
        if "\n" in self.buffer:
            lines = self.buffer.split("\n")
            self.buffer = lines[-1]
            for line in lines[:-1]:
                log_queue.put(line + "\n")
        
    def flush(self):
        """刷新缓冲区"""
        if self.buffer:
            log_queue.put(self.buffer)
            self.buffer = ""

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
    music_format.main()
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f'{time_str}: Format Finished.\n'
    
    # 确保目录存在
    if not os.path.exists('log_stft'):
        os.mkdir('log_stft')
        
    with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
        file.write(log_message)
    
    log_queue.put(log_message)


def encry():
    """格式化音乐文件"""
    encryption.main()
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f'{time_str}: Encryption Finished.\n'

    # 确保目录存在
    if not os.path.exists('log_stft'):
        os.mkdir('log_stft')

    with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
        file.write(log_message)

    log_queue.put(log_message)

def open_folder(folder_path):
    """打开指定文件夹"""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            log_queue.put(f"创建并打开文件夹: {folder_path}\n")
        else:
            log_queue.put(f"打开文件夹: {folder_path}\n")
        
        # 在Windows上使用os.startfile打开文件夹
        os.startfile(os.path.abspath(folder_path))
    except Exception as e:
        log_queue.put(f"打开文件夹 {folder_path} 失败: {str(e)}\n")

def set_max_workers(val):
    """设置最大线程数"""
    global max_workers
    # 确保线程数是整数，并且不超过CPU核心数
    max_workers = min(int(float(val)), os.cpu_count())
    thread_label.config(text=f"处理线程数: {max_workers}")

def process_music_file(name):
    """处理单个音乐文件的函数"""
    global counter
    
    try:
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name_new = re.sub(r'[<>:"/\\|?*]', '', name).rsplit('.', 1)[0]  # 文件夹名称
        if os.path.exists(f'data_stft/{name_new}'):  # 检查文件夹是否存在
            os.rmdir(f'music_stft/{name_new}')  # 删除文件
            log_queue.put(f'{time_str}: 已删除 {name} 重新处理。\n')

        log_message = f'{time_str}: Processing file: {name}\n'
        log_queue.put(log_message)
        
        with open(f'log_stft/log_{name_new}.txt', 'a', encoding='utf-8') as file:
            file.write(f'{time_str}: Program Starting.\n')
            folder = f'data_stft/{name_new}'  # 目标文件夹
            os.makedirs(folder, exist_ok=True)

            # 执行STFT处理
            if pause_processing:
                log_queue.put("Processing paused...\n")
                while pause_processing and is_running:
                    t.sleep(0.5)
                if not is_running:
                    return False
                log_queue.put("Processing resumed...\n")

            log_queue.put(f'Processing {name}: STFT Unified\n')
            stft_unified.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT Finished!\n'
            file.write(log_msg)
            log_queue.put(log_msg)

            # 检查是否暂停或停止
            if pause_processing:
                log_queue.put("Processing paused...\n")
                while pause_processing and is_running:
                    t.sleep(0.5)
                if not is_running:
                    return False
                log_queue.put("Processing resumed...\n")

            log_queue.put(f'Processing {name}: STFT 3000 Detailed\n')
            stft_3000_detailed.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-3000 Finished!\n'
            file.write(log_msg)
            log_queue.put(log_msg)

            # 检查是否暂停或停止
            if pause_processing:
                log_queue.put("Processing paused...\n")
                while pause_processing and is_running:
                    t.sleep(0.5)
                if not is_running:
                    return False
                log_queue.put("Processing resumed...\n")

            log_queue.put(f'Processing {name}: Power CSV\n')
            power.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-Power-Csv Finished!\n'
            file.write(log_msg)
            log_queue.put(log_msg)

            # 检查是否暂停或停止
            if pause_processing:
                log_queue.put("Processing paused...\n")
                while pause_processing and is_running:
                    t.sleep(0.5)
                if not is_running:
                    return False
                log_queue.put("Processing resumed...\n")

            log_queue.put(f'Processing {name}: Power PLT\n')
            power_plt.main(f"music_stft/{name}")  
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-Power-Plt Finished!\n'
            file.write(log_msg)
            log_queue.put(log_msg)

            # 检查是否暂停或停止
            if pause_processing:
                log_queue.put("Processing paused...\n")
                while pause_processing and is_running:
                    t.sleep(0.5)
                if not is_running:
                    return False
                log_queue.put("Processing resumed...\n")

            log_queue.put(f'Processing {name}: Power A-Weighted\n')
            power_aweighted.main(f"music_stft/{name}")
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f'{time_str}: STFT-Power-Plt-A-Weighting Finished!\n'
            file.write(log_msg)
            log_queue.put(log_msg)

        # 移动原始文件到处理后的目录
        shutil.move(f'music_stft/{name}', f'data_stft/{name_new}')

        # 更新计数器并显示进度
        counter += 1
        process_queue.put((counter, total_files))
        log_queue.put(f'Song-{name} Finished! [{counter}/{total_files}]\n')

        return True
    except Exception as e:
        error_msg = f"Error processing {name}: {str(e)}\n"
        log_queue.put(error_msg)
        print(error_msg)
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
            log_queue.put(f"目录 '{directory}' 不存在，请先创建并放入音频文件\n")
            is_running = False
            return

        file_list = os.listdir(directory)
        global total_files
        total_files = len(file_list)
        
        if total_files == 0:
            log_queue.put(f"目录 '{directory}' 中没有音频文件\n")
            is_running = False
            return
        
        log_queue.put(f"开始处理 {total_files} 个音乐文件...(使用 {max_workers} 个线程)\n")
        
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
                    log_queue.put(f"处理文件时失败，已跳过\n")
            except Exception as e:
                log_queue.put(f"处理任务异常: {str(e)}\n")
        
        # 记录结束时间
        end_time = t.time()
        delta_t = end_time - start_time
        
        if is_running:  # 如果不是由用户主动停止的
            completion_msg = f"所有文件处理完成! \n总共处理了 {counter} 个文件.\n耗时{delta_t:.3f}s.\n"
            log_queue.put(completion_msg)
            
            # 写入日志
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
                file.write(f'{time_str}: Program Finished Successfully!\n')
        else:
            log_queue.put("处理被用户中断\n")
            
            # 写入日志
            time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
                file.write(f'{time_str}: Program Stopped by user!\n')
    
    except Exception as e:
        log_queue.put(f"处理过程中发生错误: {str(e)}\n")
    
    finally:
        # 关闭线程池
        if thread_executor:
            thread_executor.shutdown(wait=False)
        
        is_running = False
        # 通知UI线程处理已完成
        log_queue.put("PROCESSING_DONE")

def update_cpu_usage(cpu_label):
    """更新CPU使用率"""
    try:
        while is_running:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_queue_msg = f"CPU使用率: {cpu_percent:.1f}%"
            cpu_label.config(text=cpu_queue_msg)
            t.sleep(0.5)
    except Exception as e:
        print(f"CPU监控错误: {str(e)}")

def update_ui():
    """更新UI的函数，从队列中获取信息并更新UI"""
    try:
        # 处理日志队列
        while not log_queue.empty():
            message = log_queue.get_nowait()
            if message == "PROCESSING_DONE":
                start_button.config(text="开始处理", state=tk.NORMAL)
                pause_button.config(state=tk.DISABLED)
                status_label.config(text="状态: 空闲")
            else:
                log_text.insert(tk.END, message)
                log_text.see(tk.END)
        
        # 处理进度队列
        while not process_queue.empty():
            current, total = process_queue.get_nowait()
            progress = current / total * 100 if total > 0 else 0
            progress_var.set(progress)
            progress_label.config(text=f"进度: {current}/{total} ({progress:.1f}%)")
        
        # 根据处理状态更新UI
        if is_running:
            if pause_processing:
                status_label.config(text="状态: 暂停中")
                pause_button.config(text="继续")
            else:
                status_label.config(text="状态: 处理中")
                pause_button.config(text="暂停")
                
    except Exception as e:
        print(f"UI更新错误: {str(e)}")
    
    # 安排下一次更新
    root.after(100, update_ui)

def start_processing():
    """开始处理"""
    global is_running, worker_thread, cpu_thread, counter, pause_processing
    
    if is_running:
        return
    
    # 重置状态
    is_running = True
    pause_processing = False
    counter = 0
    progress_var.set(0)
    progress_label.config(text="进度: 0/0 (0.0%)")
    
    # 更新UI状态
    start_button.config(text="处理中...", state=tk.DISABLED)
    pause_button.config(state=tk.NORMAL, text="暂停")
    status_label.config(text="状态: 初始化中")
    
    # 清空日志区域
    log_text.delete(1.0, tk.END)

    #解密文件
    log_queue.put("执行解密...\n")
    encry()
    
    # 格式化音乐文件
    log_queue.put("执行格式化...\n")
    format_files()
    
    # 启动工作线程
    worker_thread = threading.Thread(target=worker_function)
    worker_thread.daemon = True
    worker_thread.start()
    
    # 启动CPU监控线程
    cpu_thread = threading.Thread(target=update_cpu_usage, args=(cpu_label,))
    cpu_thread.daemon = True
    cpu_thread.start()

def toggle_pause():
    """暂停/继续处理"""
    global pause_processing
    
    if not is_running:
        return
    
    pause_processing = not pause_processing
    
    if pause_processing:
        pause_button.config(text="继续")
        status_label.config(text="状态: 暂停中")
    else:
        pause_button.config(text="暂停")
        status_label.config(text="状态: 处理中")

def stop_processing():
    """停止处理"""
    global is_running, thread_executor
    
    if not is_running:
        return
    
    # 确认是否真的要停止
    if messagebox.askyesno("确认停止", "确定要停止处理吗？\n已经处理的文件将不会丢失。"):
        is_running = False
        log_queue.put("正在停止处理...\n")
        
        # 关闭线程池
        if thread_executor:
            thread_executor.shutdown(wait=False)
        
        # 等待主工作线程结束
        if worker_thread and worker_thread.is_alive():
            worker_thread.join(2.0)  # 最多等待2秒
        
        # 更新UI状态
        start_button.config(text="开始处理", state=tk.NORMAL)
        pause_button.config(state=tk.DISABLED)
        status_label.config(text="状态: 已停止")

def check_and_install_dependencies():
    """检查并安装所需的依赖包"""
    print("正在检查依赖包...")
    
    # 读取requirements.txt文件
    requirements_file = 'requirements.txt'
    if not os.path.exists(requirements_file):
        print(f"警告: 未找到 {requirements_file} 文件")
        return True
    
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            required_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing_packages = []
        
        # 检查每个包是否已安装
        for package in required_packages:
            try:
                print(f"✓ {package} 已安装")
            except ImportError:
                print(f"✗ {package} 未安装")
                missing_packages.append(package)
        
        # 如果有缺失的包，则安装它们
        if missing_packages:
            print(f"\n发现缺失的依赖包: {', '.join(missing_packages)}")
            print("正在安装缺失的依赖包...")
            
            try:
                # 执行 pip install -r requirements.txt
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("依赖包安装成功!")
                print(result.stdout)
                return True
            except subprocess.CalledProcessError as e:
                print(f"依赖包安装失败: {e}")
                print(f"错误输出: {e.stderr}")
                return False
            except Exception as e:
                print(f"安装过程中发生错误: {str(e)}")
                return False
        else:
            print("✓ 所有依赖包都已安装")
            return True
            
    except Exception as e:
        print(f"检查依赖包时发生错误: {str(e)}")
        return False

def check_ffmpeg_installed():
    """检查 ffmpeg 是否已经安装"""
    ffmpeg_installed = False
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 检查脚本目录下的 ffmpeg 子目录
    if os.path.isdir(os.path.join(script_dir, 'ffmpeg')) and os.path.isfile(r'C:\Windows\ffmpeg.exe'):
        ffmpeg_installed = True
    # 检查 C:\Windows 目录下的 ffmpeg.exe
    if not ffmpeg_installed:
        print("错误: 未检测到 ffmpeg。请先安装 ffmpeg 或将其放到脚本目录下的 'ffmpeg' 子目录中，或在 C:\Windows 下放置 ffmpeg.exe")
        sys.exit(1)

def on_closing():
    """关闭窗口时的处理"""
    global is_running
    if is_running:
        if not messagebox.askyesno("确认退出", "处理正在进行中，确定要退出吗？"):
            return
        is_running = False
    
    root.destroy()
    sys.exit(0)

# 主程序入口
if __name__ == "__main__":
#def main():
    # 检查并安装依赖包
    if not check_and_install_dependencies():
        print("\n依赖包检查/安装失败，程序可能无法正常运行")
        input("按回车键继续...")

    # 检查 ffmpeg 是否已经安装
    check_ffmpeg_installed()

    # 创建主窗口
    root = tk.Tk()
    root.title("Spectrum分析工具")
    root.geometry("800x600")
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.iconphoto(True, tk.PhotoImage(file='icon.png'))  # 设置窗口图标
    
    # 创建UI组件
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 顶部控制区
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=5)
    
    # 按钮区
    button_frame = ttk.Frame(control_frame)
    button_frame.pack(side=tk.LEFT)
    
    start_button = ttk.Button(button_frame, text="开始处理", command=start_processing)
    start_button.pack(side=tk.LEFT, padx=5)
    
    pause_button = ttk.Button(button_frame, text="暂停", command=toggle_pause, state=tk.DISABLED)
    pause_button.pack(side=tk.LEFT, padx=5)
    
    stop_button = ttk.Button(button_frame, text="停止", command=stop_processing)
    stop_button.pack(side=tk.LEFT, padx=5)
    
    # 文件夹快捷按钮
    folder_frame = ttk.Frame(main_frame)
    folder_frame.pack(fill=tk.X, pady=5)
    
    folder_label = ttk.Label(folder_frame, text="快捷打开文件夹:")
    folder_label.pack(side=tk.LEFT, padx=5)
    
    music_folder_btn = ttk.Button(folder_frame, text="音乐文件夹", 
                                 command=lambda: open_folder("music_stft"))
    music_folder_btn.pack(side=tk.LEFT, padx=5)
    
    data_folder_btn = ttk.Button(folder_frame, text="数据文件夹", 
                                command=lambda: open_folder("data_stft"))
    data_folder_btn.pack(side=tk.LEFT, padx=5)
    
    log_folder_btn = ttk.Button(folder_frame, text="日志文件夹", 
                               command=lambda: open_folder("log_stft"))
    log_folder_btn.pack(side=tk.LEFT, padx=5)
    
    # 线程控制
    thread_frame = ttk.Frame(main_frame)
    thread_frame.pack(fill=tk.X, pady=5)
    
    thread_label = ttk.Label(thread_frame, text=f"处理线程数: {max_workers}", width=15) # width 设定宽度
    thread_label.pack(side=tk.LEFT, padx=5)
    
    # 创建滑块，用于设置线程数
    cpu_count = os.cpu_count() or 4
    thread_scale = Scale(thread_frame, from_=1, to=cpu_count, orient=tk.HORIZONTAL,
                        command=set_max_workers, length=200, resolution=1)
    thread_scale.set(max_workers)
    thread_scale.pack(side=tk.LEFT, padx=5)
    
    # 信息显示区
    info_frame = ttk.Frame(control_frame)
    info_frame.pack(side=tk.RIGHT)
    
    # CPU使用率标签
    cpu_label = ttk.Label(info_frame, text="CPU使用率: 0.0%")
    cpu_label.pack(side=tk.RIGHT, padx=10)
    
    # 状态标签
    status_label = ttk.Label(control_frame, text="状态: 空闲")
    status_label.pack(side=tk.RIGHT, padx=20)
    
    # 进度条区
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill=tk.X, pady=5)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    progress_label = ttk.Label(progress_frame, text="进度: 0/0 (0.0%)")
    progress_label.pack(side=tk.RIGHT, padx=10)
    
    # 日志区域
    log_frame = ttk.LabelFrame(main_frame, text="处理日志")
    log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    log_text = scrolledtext.ScrolledText(log_frame)
    log_text.pack(fill=tk.BOTH, expand=True)
    
    # 重定向标准输出到日志区域
    sys.stdout = RedirectText(log_text)
    sys.stderr = RedirectText(log_text)

    check_and_create_directories()
    
    # 初始消息
    log_text.insert(tk.END, "工具已启动，点击'开��处理'按钮开始处理音乐文件\n")
    log_text.insert(tk.END, "请确保'music_stft'目录中已放入要处理的音频文件\n")
    log_text.see(tk.END)
    
    # 启动UI更新
    update_ui()
    
    # 启动主循环
    root.mainloop()