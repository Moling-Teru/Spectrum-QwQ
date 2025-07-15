import os
ffmpeg_path = os.path.expandvars(r"%ProgramFiles%\\ffmpeg\\bin")
location=os.path.dirname(os.path.abspath(__file__))+'\\ffmpeg'
#if not os.path.exists(location + '\\ffmpeg'):
#    os.makedirs(location + '\\ffmpeg')
print(ffmpeg_path)
print(location)
print('\\\\'.replace('\\\\', '\\'))


print("setx", "PATH", f'"%PATH%;{location+'\\bin'}"', "/m")