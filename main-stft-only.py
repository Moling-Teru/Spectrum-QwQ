import os
import re
import datetime
import time as t
import sys
import shutil
import multiprocessing as mp
import platform
import power_aweighted,stft_unified,stft_3000_detailed,power,power_plt,music_format


# 全局变量，将在初始化函数中设置
counter = None
total_files = None
lock = None

def format():
    music_format.main()
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
            file.write(f'{time}: Format Finished.\n')

format()

def init_worker(counter_arg, total_arg, lock_arg):
    """初始化工作进程的全局变量"""
    global counter, total_files, lock
    counter = counter_arg
    total_files = total_arg
    lock = lock_arg


def process_music_file(name):
    """处理单个音乐文件的函数，使用全局共享变量"""
    try:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 移除在Linux中不合法的文件名字符，保持跨平台兼容性
        name_new = re.sub(r'[<>:"/\\|?*]', '', name).rsplit('.', 1)[0]  # 文件夹名称

        # 使用os.path.join确保路径分隔符正确
        log_file_path = os.path.join('log_stft', f'log_{name_new}.txt')
        with open(log_file_path, 'a', encoding='utf-8') as file:
            file.write(f'{time}: Program Starting.\n')
            folder = os.path.join('data_stft', name_new)  # 目标文件夹
            os.makedirs(folder, exist_ok=True)

            # 执行三个STFT处理
            # 替换原来的三个单独STFT处理
            input_file = os.path.join("music_stft", name)
            stft_unified.main(input_file)
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{time}: STFT Finished!\n')

            stft_3000_detailed.main(input_file)
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{time}: STFT-3000 Finished!\n')

            # 新增能量计算
            power.main(input_file)
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{time}: STFT-Power-Csv Finished!\n')

            power_plt.main(input_file)
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{time}: STFT-Power-Plt Finished!\n')

            power_aweighted.main(input_file)
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{time}: STFT-Power-Plt-A-Weighting Finished!\n')

        # 移动原始文件到处理后的目录
        source_path = os.path.join('music_stft', name)
        dest_path = os.path.join('data_stft', name_new)
        shutil.move(source_path, dest_path)

        # 更新计数器并显示进度
        with lock:
            counter.value += 1
            print(f'Song-{name} Finished! [{counter.value}/{total_files}]')

        return True
    except Exception as e:
        print(f"Error processing {name}: {str(e)}")
        return False


if __name__ == "__main__":
    if not os.path.exists('data_stft'):
        os.mkdir('data_stft')
    if not os.path.exists('log_stft'):
        os.mkdir('log_stft')

    # 指定文件夹路径
    directory = 'music_stft'
    # 使用os.listdir获取文件夹下所有文件名
    tot_name = os.listdir(directory)

    print(f"开始处理 {len(tot_name)} 个音乐文件...")
    t1=t.time()

    try:
        # 创建共享计数器和锁
        counter = mp.Value('i', 0)
        total = len(tot_name)
        lock = mp.Lock()

        # 创建进程池，使用CPU核心数量减2作为进程池大小
        processes = max(1, mp.cpu_count() - 2)

        # 使用initializer和initargs正确传递共享对象
        with mp.Pool(processes=processes, initializer=init_worker,
                     initargs=(counter, total, lock)) as pool:
            # 使用map执行处理
            results = pool.map(process_music_file, tot_name)

        t2=t.time()
        delta_t=t2-t1
        print(f"所有文件处理完成! \n总共处理了 {total} 个文件.\n耗时{delta_t:.3f}s.")
        with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{time}: Program Finished Successfully!\n')

    except KeyboardInterrupt:
        time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
            file.write(f'{time}: Program Stopped!\n')
        print(f'{time1}: Program Stopped!\n')
        sys.exit(1)