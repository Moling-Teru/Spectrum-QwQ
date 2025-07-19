import os
import subprocess
import glob
import platform

def path()-> str:
    """返回当前脚本的路径"""
    return os.path.dirname(os.path.abspath(__file__))


def encryption(folder_path):
    """识别文件夹内的音频文件并转换为WAV格式"""
    # 常见的音频文件扩展名
    audio_extensions = ['*.ncm', '*.kgm', '*.kwm']
    not_recommended_ext = ['*.mflac', '*.qmc', '*.mgg']

    # 根据操作系统选择合适的可执行文件
    system = platform.system()
    if system == "Windows":
        exe_name = 'um.exe'
    else:  # Linux和其他Unix系统
        exe_name = 'um'  # Linux下通常不需要.exe扩展名

    exe_path = os.path.join(path(), exe_name)

    # 检查可执行文件是否存在
    if not os.path.exists(exe_path):
        print(f"错误: 找不到解密工具 {exe_path}")
        if system != "Windows":
            print("提示: 在Linux系统中，请确保um工具已正确编译并具有执行权限")
            print("可以尝试运行: chmod +x um")
        return

    for ext in audio_extensions:
        # 递归查找所有匹配的音频文件
        for input_path in glob.glob(os.path.join(folder_path, "**", ext), recursive=True):

            try:
                # 获取文件扩展名(不带点)
                file_ext = os.path.splitext(input_path)[1][1:]

                if file_ext in not_recommended_ext:
                    print(f"不推荐使用 {file_ext} 格式，可能会导致转换失败。")
                    continue

                # 使用绝对路径确保跨平台兼容性
                subprocess.run([exe_path, os.path.abspath(input_path)], check=True)
                os.remove(input_path)
                print(f"转换完成: {input_path}")

            except Exception as e:
                print(f"转换 {input_path} 时出错: {str(e)}")


def main():
    folder_to_process = "music_stft"  # 修改为您的目标文件夹路径
    encryption(folder_to_process)