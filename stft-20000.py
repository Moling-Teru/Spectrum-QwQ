# 输入文件music/... 输出文件data/name/csv,png
import sys
import numpy as np
import soundfile as sf
from scipy.signal import stft
import pandas as pd
import librosa
import matplotlib.pyplot as plt

if len(sys.argv)!=2:
    print("参数错误!")
    sys.exit(1)

def get_duration_librosa(file_path):
    audio_data, sample_rate = librosa.load(file_path)
    duration = librosa.get_duration(y=audio_data, sr=sample_rate)
    return duration

# ========= 可调参数 ==========================================
wav_path   = sys.argv[1]  # 音频文件
hop_ms     = 50             # 帧移（毫秒）
step_hz    = 10             # 频率分辨率
max_freq   = 20_000          # 最高保留到多少 Hz（<= sr/2）
floor_db   = -120.0          # dB 下限，小于该值写成 floor_db
csv_digits = 3              # CSV 保留小数位
# ============================================================

# 1. 读音频 ---------------------------------------------------
audio, sr = sf.read(wav_path)
if audio.ndim > 1:
    audio = audio.mean(axis=1)

# 2. STFT -----------------------------------------------------
hop_length = int(sr * hop_ms / 1000)       # 50 ms → 样本数
n_fft      = int(round(sr / step_hz))      # 10 Hz 分辨率
n_fft     += n_fft % 2                     # 偶数
f, t, Zxx  = stft(
    audio, fs=sr, window="hann",
    nperseg=n_fft, noverlap=n_fft-hop_length,
    boundary=None, padded=False
)
mag = np.abs(Zxx)                          # 幅值谱

# 3. 频率截断并重采样 -----------------------------------------
nyquist     = sr / 2
max_freq    = min(max_freq, nyquist)
target_freq = np.arange(0, max_freq+1, step_hz)     # 0,10,20…
bin_width   = sr / n_fft
idx         = np.clip(np.round(target_freq/bin_width).astype(int),
                      0, len(f)-1)
spec = mag[idx, :]                         # shape = (freq, time)

# 4. 线性幅值 → 对数振幅 + dB 下限 ----------------------------
eps     = 1e-10
spec_db = 20*np.log10(np.maximum(spec, eps))
spec_db -= np.max(spec_db)                 # 峰值设为 0 dB
spec_db  = np.maximum(spec_db, floor_db)   # 裁剪到 floor_db

# 5. 画图 -----------------------------------------------------
path = f"data_stft/{wav_path.split('/')[1].rsplit('.',1)[0]}"
time=int(get_duration_librosa(wav_path))
width=max(time//4,20)
plt.figure(figsize=(width,20))          #等待长度动态更改修复
plt.imshow(spec_db,
           origin="lower", aspect="auto",
           extent=[float(t[0]), float(t[-1]),
                   float(target_freq[0]), float(target_freq[-1])],
           cmap="magma", vmin=floor_db, vmax=0)
plt.colorbar(label="Amplitude (dB)")
plt.xlabel("Time (s)")  # 修改标签为秒
plt.ylabel("Frequency (Hz)")
plt.title(f"Log-Amplitude Spectrogram "
          f"({step_hz} Hz × {hop_ms} ms, ≤{max_freq} Hz)")
plt.tight_layout()
pic_path=path+'/data-20000.png'
plt.savefig(pic_path, dpi=150, bbox_inches="tight")
print("已保存：", pic_path)