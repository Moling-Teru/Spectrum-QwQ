import os
import subprocess
import glob

def path()-> str:
    """返回当前脚本的路径"""
    return os.path.dirname(os.path.abspath(__file__))


def encryption(folder_path):
    """识别文件夹内的音频文件并转换为WAV格式"""
    # 常见的音频文件扩展名
    audio_extensions = ['*.ncm', '*.kgm', '*.kwm']
    not_recommended_ext = ['*.mflac', '*.qmc', '*.mgg']
    exe_path=r'um.exe'

    for ext in audio_extensions:
        # 递归查找所有匹配的音频文件
        for input_path in glob.glob(os.path.join(folder_path, "**", ext), recursive=True):

            try:
                # 获取文件扩展名(不带点)
                file_ext = os.path.splitext(input_path)[1][1:]
                #print(os.path.join(path(),exe_path))
                if file_ext in not_recommended_ext:
                    print(f"不推荐使用 {file_ext} 格式，可能会导致转换失败。")
                    continue
                subprocess.run([os.path.join(path(),exe_path), os.path.join(path(),input_path)], check=True)
                os.remove(input_path)
                print(f"转换完成: {input_path}")

            except Exception as e:
                print(f"转换 {input_path} 时出错: {str(e)}")


def main():
    folder_to_process = "music_stft"  # 修改为您的目标文件夹路径
    encryption(folder_to_process)