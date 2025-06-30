import chardet

def get_encoding(file):
     with open(file, 'rb') as f:
         result = chardet.detect(f.read())
         return result['encoding']

# 示例
file_path = '../config'
encoding = get_encoding(file_path)
print(f'文件编码格式为: {encoding}')