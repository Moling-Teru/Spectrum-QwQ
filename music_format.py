import os
from pydub import AudioSegment
import glob


def convert_to_wav(folder_path):
    """识别文件夹内的音频文件并转换为WAV格式"""
    # 常见的音频文件扩展名
    audio_extensions = ['*.mp3', '*.aac', '*.ogg', '*.flac', '*.m4a', '*.wma']

    for ext in audio_extensions:
        # 递归查找所有匹配的音频文件
        for input_path in glob.glob(os.path.join(folder_path, "**", ext), recursive=True):
            # 输出WAV文件路径
            output_path = os.path.splitext(input_path)[0] + '.wav'

            print(f"正在转换: {input_path} -> {output_path}")

            try:
                # 获取文件扩展名(不带点)
                file_ext = os.path.splitext(input_path)[1][1:]
                # 加载音频文件
                audio = AudioSegment.from_file(input_path, format=file_ext)
                # 导出为WAV格式
                audio.export(output_path, format="wav")
                os.remove(input_path)
                print(f"转换完成: {output_path}")
            except Exception as e:
                print(f"转换 {input_path} 时出错: {str(e)}")


# 使用示例
def main():
    folder_to_process = "music_stft"  # 修改为您的目标文件夹路径
    convert_to_wav(folder_to_process)