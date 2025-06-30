import numpy as np
freq_min = 0
freq_max = 1000
freq_step = 1
frequencies = np.arange(freq_min, freq_max + 1, freq_step)
f2 = np.square(frequencies)
numerator = np.double(12194.0**2 * f2**2) #整个程序出了错，只是因为少了个.0，整数溢出了
denominator = np.double((f2 + 20.6**2) * np.sqrt((f2 + 107.7**2) * (f2 + 737.9**2)) * (f2 + 12194.0**2))

# 计算A计权(dB)
a_weights = 2.0 + 20 * np.log10(numerator / denominator)

# 转换为线性比例因子
print( 10 ** (a_weights / 20) )