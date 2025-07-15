import os
import subprocess
import sys
import ffmpeg_find_dir

def install_ffmpeg():
    """使用winget安装ffmpeg并配置环境变量"""
    try:
        # 检查winget是否可用
        subprocess.run(["winget", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("错误: winget 未安装或不可用。请先安装winget。")
        sys.exit(1)

    try:
        # 使用winget安装ffmpeg
        location=os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(location + '\\ffmpeg'):
            os.makedirs(location + '\\ffmpeg')
        print("正在安装ffmpeg...")
        subprocess.run(["winget", "install", "ffmpeg", "-e", "--id", "Gyan.FFmpeg", "-l", f"{location+'\\ffmpeg'}"], check=True)
        print("ffmpeg安装完成。")
    except subprocess.CalledProcessError as e:
        print(f"安装ffmpeg时出错: {e}")
        sys.exit(1)

    # 获取ffmpeg的安装路径
    ffmpeg_path = ffmpeg_find_dir.find_ffmpeg_subfolder(location + '\\ffmpeg')
    ffmpeg_path = ffmpeg_path.replace('\\\\', '\\')
    if ffmpeg_path is None:
        print("错误: 未找到ffmpeg的安装目录。请检查安装是否成功。")
        sys.exit(1)

    try:
        # 将ffmpeg的bin目录添加到系统环境变量
        print("正在配置环境变量...")
        print("setx", "PATH", f'"%PATH%;{ffmpeg_path+'\\bin'}"', "/m")
        # 方法一：setx设置
        subprocess.run(
            f'setx PATH "%PATH%;{ffmpeg_path}\\bin" /M',
            check=True,
            shell=True
        )
        print("环境变量配置完成。")
        # 方法二： 软链接到系统目录

    except subprocess.CalledProcessError as e:
        print(f"配置环境变量时出错: {e}")
        sys.exit(1)

    # 运行soft_link.bat，并传入ffmpeg_path作为参数
    try:
        subprocess.run(["soft_link.bat", ffmpeg_path], check=True)
        print("备份方法执行完成。")
    except subprocess.CalledProcessError as e:
        print(f"运行备份方法时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_ffmpeg()
