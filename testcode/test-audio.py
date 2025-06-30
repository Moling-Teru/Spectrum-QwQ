import numpy as np
from scipy.io import wavfile

# 设置参数
sample_rate = 44100  # 采样率
duration = 5  # 持续时间（秒）
frequency = 5000  # 频率（Hz，A4音符）

# 生成时间数组
t = np.linspace(0, duration, int(sample_rate * duration), False)

# 生成正弦波
sine_wave = 0.5 * np.sin(2 * np.pi * frequency * t)

# 确保数据在-1到1之间
audio = sine_wave * (2**15 - 1) / np.max(np.abs(sine_wave))
audio = audio.astype(np.int16)

# 保存为WAV文件
wavfile.write('music/sine_tone.wav', sample_rate, audio)