import os

def check_ffmpeg_installed() -> str | None:
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

def test_import():
    try:
        import pydub
        return "pydub 导入成功"
    except ImportError:
        raise ImportError("pydub导入异常。")

if __name__ == "__main__":
    try:
        re=check_ffmpeg_installed()
        print(re)
        re2=test_import()
        print(re2)
    except (FileNotFoundError, ImportError) as e:
        print(str(e))
