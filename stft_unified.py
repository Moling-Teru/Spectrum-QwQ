# 多频率范围STFT分析器 - 统一版本
# 输入文件music/... 输出文件data_stft/name/csv,png
import sys
import os
import numpy as np
import soundfile as sf
from scipy.signal import stft
import pandas as pd
import librosa
import matplotlib
matplotlib.use('Agg')  # 设置后端为非交互式 Agg
import matplotlib.pyplot as plt
import time

def get_duration_librosa(file_path):
    """获取音频文件的播放时长"""
    audio_data, sample_rate = librosa.load(file_path)
    duration = librosa.get_duration(y=audio_data, sr=sample_rate)
    return duration

def generate_spectrogram(wav_path, freq_ranges=None, hop_ms=50, step_hz=10, floor_db=-120.0, csv_digits=3):
    """
    生成多个频率范围的声谱图
    
    参数:
        wav_path: 音频文件路径
        freq_ranges: 频率上限列表，默认为[4000, 8000, 20000]
        hop_ms: 帧移（毫秒）
        step_hz: 频率分辨率
        floor_db: dB下限
        csv_digits: CSV保留小数位
    """
    if freq_ranges is None:
        freq_ranges = [4000, 8000, 20000]
    
    # 创建输出目录
    path = f"data_stft/{os.path.basename(wav_path).rsplit('.',1)[0]}"
    os.makedirs(path, exist_ok=True)
    
    # 获取音频时长（用于图像尺寸设置）
    time_duration = int(get_duration_librosa(wav_path))
    
    # 1. 读音频 ---------------------------------------------------
    print(f"加载音频文件: {wav_path}")
    audio, sr = sf.read(wav_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)  # 转为单声道
    
    # 2. STFT -----------------------------------------------------
    hop_length = int(sr * hop_ms / 1000)       # 帧移，单位为样本数
    n_fft = int(round(sr / step_hz))           # 窗口大小，决定频率分辨率
    n_fft += n_fft % 2                         # 确保是偶数
    
    print(f"执行STFT分析，窗口大小: {n_fft}, 帧移: {hop_length}")
    f, t, Zxx = stft(
        audio, fs=sr, window="hann",
        nperseg=n_fft, noverlap=n_fft-hop_length,
        boundary=None, padded=False
    )
    mag = np.abs(Zxx)                          # 幅值谱
    
    nyquist = sr / 2                           # 奈奎斯特频率（理论最大频率）
    bin_width = sr / n_fft                     # 每个频率bin的宽度
    
    # 3. 为每个频率范围生成数据和图像 ----------------------------
    for max_freq in freq_ranges:
        # 限制最大频率不超过奈奎斯特频率
        actual_max_freq = min(max_freq, nyquist)
        print(f"处理频率范围: 0-{actual_max_freq} Hz")
        
        # 创建目标频率数组
        target_freq = np.arange(0, actual_max_freq+1, step_hz)
        
        # 获取频率索引
        idx = np.clip(np.round(target_freq/bin_width).astype(int),
                      0, len(f)-1)
        
        # 提取对应频率范围的数据
        spec = mag[idx, :]
        
        # 4. 线性幅值 → 对数振幅 + dB 下限 ------------------------
        eps = 1e-10
        spec_db = 20*np.log10(np.maximum(spec, eps))
        spec_db -= np.max(spec_db)             # 峰值设为 0 dB
        spec_db = np.maximum(spec_db, floor_db)# 裁剪到 floor_db
        
        # 5. 图像尺寸设置 -----------------------------------------
        # 根据频率范围调整图像尺寸
        if max_freq <= 4000:
            width, height = max(time_duration//4, 8), 4
        elif max_freq <= 8000:
            width, height = max(time_duration//4, 10), 6
        else:
            width, height = max(time_duration//4, 20), 12
        
        # 6. 保存CSV（仅为8000Hz版本保存CSV，与原代码保持一致）---
        if max_freq == 8000:
            time_s = t  # 直接使用STFT返回的时间(秒)
            df = pd.DataFrame(spec_db,
                            index=target_freq,  # 行：频率
                            columns=time_s)     # 列：时间(秒)
            csv_path = f"{path}/data.csv"
            df = df.T
            df.to_csv(csv_path, float_format=f"%.{csv_digits}f")
            print(f"已保存CSV: {csv_path}")
        
        # 7. 绘制频谱图 -------------------------------------------
        plt.figure(figsize=(width, height))
        plt.imshow(spec_db,
                origin="lower", aspect="auto",
                extent=[float(t[0]), float(t[-1]),
                        float(target_freq[0]), float(target_freq[-1])],
                cmap="magma", vmin=floor_db, vmax=0)
        plt.colorbar(label="Amplitude (dB)")
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")
        plt.title(f"Log-Amplitude Spectrogram "
                f"({step_hz} Hz × {hop_ms} ms, ≤{max_freq} Hz)")
        plt.tight_layout()
        
        # 保存图像
        pic_path = f"{path}/data-{max_freq}.png"
        plt.savefig(pic_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"已保存图像: {pic_path}")


def main(audio):
    # 输入音频文件路径
    audio_file = audio
    # 检查文件格式
    if not audio_file.lower().endswith('.wav'):
        print(f"警告: 文件不是.wav格式，可能无法正确处理")
    generate_spectrogram(audio_file)