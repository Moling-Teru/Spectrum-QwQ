import os

def find_ffmpeg_subfolder(folder):
    # 遍历文件夹中的每个项
    for entry in os.listdir(folder):
        path = os.path.join(folder, entry)
        # 如果为目录并且名称包含'ffmpeg'（不区分大小写），则返回该路径
        if os.path.isdir(path) and 'ffmpeg' in entry.lower():
            return path
    return None
