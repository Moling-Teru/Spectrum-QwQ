import os
folder_path='music_stft'
ext='*.mp3'
n=os.path.join(folder_path, "**", ext)
print(n)