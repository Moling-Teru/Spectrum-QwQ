import sys
import numpy as np
import pandas as pd
import matplotlib
import os
matplotlib.use('Agg')  # 设置后端为非交互式 Agg
import matplotlib.pyplot as plt
def plt_drawing(audio_path):
    base_name = f"data_stft/{audio_path.split('/')[1].rsplit('.', 1)[0]}"
    csv_input = f"{base_name}/frequency_energy.csv"
    png_output= f"{base_name}/frequency_energy.png"

    # 检查CSV文件是否存在且非空
    if not os.path.exists(csv_input) or os.path.getsize(csv_input) == 0:
        print(f"警告: {csv_input} 不存在或为空，跳过绘图。")
        return

    # 读取CSV文件 - 使用header=0将第一行作为列名
    df = pd.read_csv(csv_input, header=0, encoding='utf-8')
    
    # 检查DataFrame是否为空
    if df.empty:
        print(f"警告: {csv_input} 为空或格式不正确，跳过绘图。")
        return
    
    # 获取第一行数据（即第二行，因为第一行被当作列名）
    energy_values = df.iloc[0].values
    
    # 获取频率值（列名）
    frequencies = df.columns.astype(float)
    
    # 由于文件已经限制为0-4000Hz范围，不需要过滤
    filtered_freqs = frequencies
    filtered_energy = energy_values
    
    # 找到最大值及其索引
    max_value = filtered_energy.max()
    max_index = filtered_energy.argmax()
    max_freq = filtered_freqs[max_index]
    
    # 计算相对能量值
    relative_energy = filtered_energy / max_value
    
    # 绘图
    plt.figure(figsize=(21, 9))
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(filtered_freqs, relative_energy, color='b')
    plt.xlim(20, 20000)  # 将x轴范围限制在0-4000Hz
    plt.ylim(0, 15)
    plt.title('Power Data - 20000 Hz Max (1Hz Resolution)', family="Microsoft YaHei")
    plt.xlabel('频率(Hz)', family="Microsoft YaHei")
    plt.ylabel('相对能量', family="Microsoft YaHei")
    
    # 标注最大值
    plt.annotate(f'Max: {max_freq:.0f}Hz', 
                 color='b', 
                 xy=(max_freq, 10),
                 xytext=(max_freq, 12),
                 arrowprops=dict(facecolor='b', shrink=0.03))
    
    plt.tight_layout()
    plt.savefig(png_output, dpi=150, bbox_inches='tight')
    plt.close()  # 关闭图形，释放内存

def main(audio):
    plt_drawing(audio)
    name = audio.split('/')[1].rsplit('.', 1)[0]
    print(f'Song: {name}- Plt Drawing Finished!')