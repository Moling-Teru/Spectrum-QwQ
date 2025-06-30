import sys
import numpy as np
import librosa
import csv
import os


def calculate_frequency_energies(audio_file, freq_min=0, freq_max=4000, freq_step=1, freq_tolerance=1.0):
    """
    计算音频文件在指定频率范围内的能量总和

    参数:
        audio_file: 音频文件路径
        freq_min: 最小频率(Hz)
        freq_max: 最大频率(Hz)
        freq_step: 频率步长(Hz)
        freq_tolerance: 频率容差(Hz)

    返回:
        frequencies: 频率列表
        energies: 对应频率的能量总和列表
    """
    print(f"加载音频文件: {audio_file}...")
    # 加载音频文件
    y, sr = librosa.load(audio_file, sr=None)
    y_mono = librosa.to_mono(y)


    print(f"执行STFT分析...")
    # 设置STFT参数
    # 更合理的帧移设置，使用帧移25ms (更适合1Hz分辨率的分析)
    hop_ms = 25
    hop_length = int(sr * hop_ms / 1000)  # 将毫秒转为样本数
    
    # 窗口大小设置为采样率，这样可以提供1Hz的频率分辨率
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

    return frequencies, energies


def save_to_csv(frequencies, energies, output_file):
    """
    将频率和能量数据保存为CSV文件

    参数:
        frequencies: 频率列表
        energies: 对应频率的能量总和列表
        output_file: 输出CSV文件路径
    """
    with open(output_file, 'w', newline='',encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(frequencies)  # 第一行：频率
        writer.writerow(energies)  # 第二行：能量

    print(f"数据已保存到: {output_file}")


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
    #base_name = os.path.splitext(audio_file)[0]
    csv_output = f"{base_name}/frequency_energy.csv"

    # 计算频率能量
    print(f"Song{audio_file}- 开始分析音频文件...")
    frequencies, energies = calculate_frequency_energies(audio_file)

    # 保存CSV
    save_to_csv(frequencies, energies, csv_output)

    print(f"Song{audio_file}- 分析完成!")