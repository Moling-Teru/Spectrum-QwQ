import os

def check_ffmpeg_installed():
    """检查 ffmpeg 是否已经安装"""
    ffmpeg_installed = False
    script_dir = os.path.dirname(os.path.abspath(__file__))
    Path=os.getenv('PATH')
    # 检查脚本目录下的 ffmpeg 子目录
    if 'ffmpeg' in Path:
        ffmpeg_installed = True
        return '环境变量中找到ffmpeg'
    elif os.path.isfile(r'C:\Windows\ffmpeg.exe'):
        ffmpeg_installed = True
        return 'Windows文件夹中找到ffmpeg'
    elif os.path.isdir(os.path.join(script_dir, 'ffmpeg')):
        ffmpeg_installed = True
        return '脚本目录下找到ffmpeg'
    # 检查 C:\Windows 目录下的 ffmpeg.exe
    if not ffmpeg_installed:
        raise FileNotFoundError("ffmpeg 未安装或未找到")

if __name__ == "__main__":
    try:
        re=check_ffmpeg_installed()
        print(re)
    except FileNotFoundError as e:
        print(str(e))
