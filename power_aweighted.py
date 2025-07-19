import sys
import numpy as np
import soundfile as sf
import librosa
import csv
import os
import matplotlib
matplotlib.use('Agg')  # 设置后端为非交互式 Agg
import matplotlib.pyplot as plt
import traceback


def a_weighting(frequencies):
    """
    应用A计权滤波器，模拟人耳对不同频率的敏感度
    
    参数:
        frequencies: 频率数组 (Hz)
        
    返回:
        a_weights: A计权修正值 (dB)
    """
    # A计权近似公式 (IEC 61672-1:2002)
    f2 = np.square(frequencies)
    numerator = 12194.0**2 * f2**2 #整个程序出了错，只是因为少了个.0，整数溢出了
    denominator = (f2 + 20.6**2) * np.sqrt((f2 + 107.7**2) * (f2 + 737.9**2)) * (f2 + 12194.0**2)
    
    # 计算A计权(dB)
    a_weights = 2.0 + 20 * np.log10(numerator / denominator)
    
    # 平滑处理极低频率的计权值
    a_weights = np.maximum(a_weights, -100.0)
    
    # 转换为线性比例因子
    return 10 ** (a_weights / 20)


def calculate_frequency_energies(audio_file, freq_min=0, freq_max=4000, freq_step=1, freq_tolerance=3, apply_aweighting=True):
    """
    计算音频文件在指定频率范围内的能量总和
    可选择是否应用人耳听觉特征曲线(A计权)调整

    参数:
        audio_file: 音频文件路径
        freq_min: 最小频率(Hz)
        freq_max: 最大频率(Hz)
        freq_step: 频率步长(Hz)
        freq_tolerance: 频率容差(Hz)
        apply_aweighting: 是否应用A计权调整

    返回:
        frequencies: 频率列表
        energies: 对应频率的能量总和列表
        energies_aweighted: 应用A计权后的能量总和列表(如果apply_aweighting=True)
    """
    print(f"加载音频文件: {audio_file}...")
    # 加载音频文件
    y, sr = librosa.load(audio_file, sr=None)
    y_mono = librosa.to_mono(y)

    print(f"执行STFT分析...")
    # 设置STFT参数
    # 帧移设置为25ms (适合1Hz分辨率的分析)
    hop_ms = 25
    hop_length = int(sr * hop_ms / 1000)  # 将毫秒转为样本数
    
    # 窗口大小设置为采样率，以提供1Hz的频率分辨率
    window_size = int(round(sr / freq_step))  # 1 Hz 分辨率
    window_size += window_size % 2  # 确保窗口大小为偶数

    print(f"窗口大小: {window_size}, 帧移: {hop_length}")
    
    # 执行STFT
    D = librosa.stft(y_mono, n_fft=window_size, hop_length=hop_length, window='hann')

    # 计算能量谱
    power_spectrogram = np.abs(D) ** 2

    # 获取频率bins
    freq_bins = librosa.fft_frequencies(sr=sr, n_fft=window_size)

    # 创建频率列表
    frequencies = np.arange(freq_min, freq_max + 1, freq_step)
    energies = []

    print(f"计算{len(frequencies)}个频率点的能量...")
    # 为每个目标频率计算能量
    for i, target_freq in enumerate(frequencies):
        if i % 500 == 0:  # 每计算500个频率显示一次进度
            print(f"进度: {i}/{len(frequencies)}")

        # 找到目标频率对应的bin索引
        target_bin_indices = np.where(np.abs(freq_bins - target_freq) <= freq_tolerance)[0]

        if len(target_bin_indices) == 0:
            # 如果在容差范围内没有找到匹配的频率bin，记录0能量
            energies.append(0)
        else:
            # 计算目标频率能量总和
            energy = np.sum(power_spectrogram[target_bin_indices, :])
            energies.append(energy)
    
    # 应用A计权调整能量值
    if apply_aweighting:
        # 计算A计权系数
        a_weights = a_weighting(frequencies)
        # 应用A计权到能量值
        energies_aweighted = np.array(energies) * a_weights**2
        return frequencies, energies, energies_aweighted
    else:
        return frequencies, energies, None


def save_to_csv(frequencies, energies, energies_aweighted, output_file, output_file_aweighted):
    """
    将频率和能量数据保存为CSV文件

    参数:
        frequencies: 频率列表
        energies: 对应频率的能量总和列表
        energies_aweighted: A计权后的能量总和列表
        output_file: 原始能量CSV输出文件路径
        output_file_aweighted: A计权能量CSV输出文件路径
    """
    # 保存原始能量数据
    '''
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(frequencies)  # 第一行：频率
        writer.writerow(energies)  # 第二行：能量

    print(f"原始能量数据已保存到: {output_file}")
    '''
    
    # 保存A计权能量数据
    with open(output_file_aweighted, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(frequencies)  # 第一行：频率
        writer.writerow(energies_aweighted)  # 第二行：A计权能量

    print(f"A计权能量数据已保存到: {output_file_aweighted}")


def plot_aweighted_relative_energy(frequencies, energies_aweighted, output_folder):
    """
    绘制A计权后的相对能量图并保存到输出文件夹
    
    参数:
        frequencies: 频率列表
        energies_aweighted: A计权后的能量总和列表
        output_folder: 输出文件夹路径
    """
    # 计算相对能量值
    max_value = max(energies_aweighted)
    relative_energy = np.array(energies_aweighted) / max_value
    
    # 找到最大值及其索引
    max_index = np.argmax(energies_aweighted)
    max_freq = frequencies[max_index]
    
    # 绘图
    plt.figure(figsize=(16, 9))
    plt.plot(frequencies, relative_energy, color='b')
    plt.xlim(0, 4000)  # 将x轴范围限制在0-4000Hz
    plt.ylim(0, 1.2)
    plt.title('A-Weighted Power Data - 4000 Hz Max (1Hz Resolution)', family="Microsoft YaHei")
    plt.xlabel('频率(Hz)', family="Microsoft YaHei")
    plt.ylabel('A计权相对能量', family="Microsoft YaHei")
    
    # 标注最大值
    plt.annotate(f'Max: {max_freq:.0f}Hz', 
                 color='b', 
                 xy=(max_freq, 1), 
                 xytext=(max_freq, 1.1),
                 arrowprops=dict(facecolor='b', shrink=0.03),
                 family="Microsoft YaHei")
    
    plt.tight_layout()
    plt.savefig(f"{output_folder}/frequency_energy_aweighted.png", dpi=150, bbox_inches='tight')
    plt.close()  # 关闭图形，释放内存
    print(f"A计权相对能量图已保存到: {output_folder}/frequency_energy_aweighted.png")


def main(audio):
    # 输入音频文件路径
    audio_file = audio

    # 检查文件是否存在
    if not os.path.exists(audio_file):
        print(f"错误: 文件 '{audio_file}' 不存在!")
        return

    # 检查文件格式
    if not audio_file.lower().endswith('.wav'):
        print(f"警告: 文件不是.wav格式，可能无法正确处理")

    # 生成输出文件名（基于输入文件名）
    base_name = f"data_stft/{audio_file.split('/')[1].rsplit('.', 1)[0]}"
    csv_output = f"{base_name}/frequency_energy.csv"
    csv_output_aweighted = f"{base_name}/frequency_energy_aweighted.csv"

    # 计算频率能量
    print(f"Song{audio_file}- 开始分析音频文件...")
    frequencies, energies, energies_aweighted = calculate_frequency_energies(audio_file, apply_aweighting=True)

    # 保存CSV
    try:
        save_to_csv(frequencies, energies, energies_aweighted, csv_output, csv_output_aweighted)
    
    # 绘制A计权后的相对能量图
        plot_aweighted_relative_energy(frequencies, energies_aweighted, base_name)

        print(f"Song{audio_file}- 分析完成!")

    except Exception as e:
        print(f"Song{audio_file}- 分析过程中出错: {str(e)}")
        print("错误信息:")
        traceback.print_exc()  # 打印详细的错误信息
