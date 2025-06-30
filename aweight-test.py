import power_aweighted,music_format
import datetime,os,re
import time as t
import sys

def format():
    music_format.main()
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
            file.write(f'{time}: Format Finished.\n')

format()

def process_music_file(name):
    """处理单个音乐文件的函数，使用全局共享变量"""
    try:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name_new = re.sub(r'[<>:"/\\|?*]', '', name).rsplit('.', 1)[0]  # 文件夹名称

        with open(f'log_stft/log_{name_new}.txt', 'a', encoding='utf-8') as file:
            folder = f'data_stft/{name_new}'  # 目标文件夹
            os.makedirs(folder, exist_ok=True)

            power_aweighted.main(f"music_stft/{name}")
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f'{time}: STFT-Power-Plt-A-Weighting Finished!\n')

    except Exception as e:
        print(f"Error processing {name}: {str(e)}")

if __name__ == "__main__":

    # 指定文件夹路径
    directory = 'music_stft'
    # 使用os.listdir获取文件夹下所有文件名
    tot_name = os.listdir(directory)
    total=len(tot_name)
    print(f"开始处理 {len(tot_name)} 个音乐文件...")
    t1=t.time()
    process_music_file(tot_name[0])
    t2=t.time()
    delta_t=t2-t1
    print(f"所有文件处理完成! \n总共处理了 {total} 个文件.\n耗时{delta_t:.3f}s.")
    with open(f'log_stft/log_main.txt', 'a', encoding='utf-8') as file:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f'{time}: Program Finished Successfully!\n')