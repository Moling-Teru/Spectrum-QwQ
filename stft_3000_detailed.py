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

def generate_spectrogram_3000Hz_3Hz(wav_path):
    """
    生成最高3000Hz，每3Hz的声谱图 (不保存CSV)

    参数:
        wav_path: 音频文件路径
    """
    max_freq = 3000
    step_hz = 3
    hop_ms = 50 # Keep consistent hop_ms

    # 创建输出目录
    path = f"data_stft/{os.path.basename(wav_path).rsplit('.',1)[0]}"
    os.makedirs(path, exist_ok=True)

    # 获取音频时长（用于图像尺寸设置）
    time_duration = int(get_duration_librosa(wav_path))

    # 1. 读音频 ---------------------------------------------------
    print(f"加载音频文件: {wav_path}")
    t_start = time.time()
    audio, sr = sf.read(wav_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)  # 转为单声道

    # 2. STFT -----------------------------------------------------
    hop_length = int(sr * hop_ms / 1000)       # 帧移，单位为样本数
    n_fft = int(round(sr / step_hz))           # 窗口大小，决定频率分辨率
    n_fft += n_fft % 2                         # 确保是偶数

    print(f"执行STFT分析 (3000Hz, 3Hz步长)，窗口大小: {n_fft}, 帧移: {hop_length}")
    f, t, Zxx = stft(
        audio, fs=sr, window="hann",
        nperseg=n_fft, noverlap=n_fft-hop_length,
        boundary=None, padded=False
    )
    mag = np.abs(Zxx)                          # 幅值谱

    nyquist = sr / 2                           # 奈奎斯特频率（理论最大频率）
    bin_width = sr / n_fft                     # 每个频率bin的宽度

    # 3. 为指定频率范围生成数据和图像 ----------------------------
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
    floor_db = -120.0 # Keep consistent floor_db
    eps = 1e-10
    spec_db = 20*np.log10(np.maximum(spec, eps))
    spec_db -= np.max(spec_db)             # 峰值设为 0 dB
    spec_db = np.maximum(spec_db, floor_db)# 裁剪到 floor_db

    # 5. 图像尺寸设置 -----------------------------------------
    # 根据频率范围调整图像尺寸 (Using logic similar to original)
    # For 3000Hz, use the 4000Hz logic
    width, height = max(time_duration//4, 8), 16

    # 6. 保存CSV (Skipped as per requirement) -------------------
    # No CSV saving for this specific function

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
    pic_path = f"{path}/data-{max_freq}Hz-{step_hz}HzStep.png" # Unique filename
    plt.savefig(pic_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"已保存图像: {pic_path}")

    t_end = time.time()
    print(f"处理完成 (3000Hz, 3Hz步长)，耗时: {t_end-t_start:.2f}秒")

def main(audio):
    audio_file = audio
    generate_spectrogram_3000Hz_3Hz(audio_file)