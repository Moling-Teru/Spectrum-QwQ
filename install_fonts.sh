#!/bin/bash

# 安装微软雅黑字体到系统目录的脚本

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "请以root权限运行此脚本: sudo $0"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONT_SOURCE_DIR="$SCRIPT_DIR/font"
FONT_TARGET_DIR="/usr/share/fonts/msyh"

echo "开始安装微软雅黑字体..."

# 检查源字体文件夹是否存在
if [ ! -d "$FONT_SOURCE_DIR" ]; then
    echo "错误: 字体源文件夹 $FONT_SOURCE_DIR 不存在"
    exit 1
fi

# 创建目标字体目录
echo "创建目标字体目录: $FONT_TARGET_DIR"
mkdir -p "$FONT_TARGET_DIR"

# 拷贝字体文件
echo "拷贝字体文件到 $FONT_TARGET_DIR"
cp -r "$FONT_SOURCE_DIR"/* "$FONT_TARGET_DIR"/

# 检查拷贝是否成功
if [ $? -eq 0 ]; then
    echo "字体文件拷贝成功"
else
    echo "错误: 字体文件拷贝失败"
    exit 1
fi

# 设置正确的权限
echo "设置字体文件权限"
chmod 644 "$FONT_TARGET_DIR"/*.TTC
chown root:root "$FONT_TARGET_DIR"/*.TTC

# 切换到字体目录
cd "$FONT_TARGET_DIR" || exit

# 生成字体索引文件
echo "生成字体索引文件..."
if command -v mkfontscale >/dev/null 2>&1; then
    mkfontscale
    echo "mkfontscale 执行完成"
else
    echo "警告: mkfontscale 命令未找到，可能需要安装 xfonts-utils 包"
fi

if command -v mkfontdir >/dev/null 2>&1; then
    mkfontdir
    echo "mkfontdir 执行完成"
else
    echo "警告: mkfontdir 命令未找到，可能需要安装 xfonts-utils 包"
fi

# 刷新字体缓存
echo "刷新字体缓存..."
if command -v fc-cache >/dev/null 2>&1; then
    fc-cache -fv
    echo "字体缓存刷新完成"
else
    echo "警告: fc-cache 命令未找到，可能需要安装 fontconfig 包"
fi

echo "字体安装完成!"
echo "已安装的字体文件:"
ls -la "$FONT_TARGET_DIR"

# 验证字体是否可用
echo "验证字体安装..."
fc-list | grep -i "Microsoft YaHei\|MSYH" && echo "微软雅黑字体安装成功!" || echo "注意: 无法在字体列表中找到微软雅黑"

# 清除matplotlib字体缓存
echo ""
echo "清除matplotlib字体缓存..."

# 检查并清除系统级matplotlib缓存
MATPLOTLIB_CACHE_DIRS="/tmp/matplotlib-* /var/tmp/matplotlib-* $HOME/.cache/matplotlib $HOME/.matplotlib"

# 清除不同用户的matplotlib缓存
for user_home in /home/*; do
    if [ -d "$user_home" ]; then
        MATPLOTLIB_CACHE_DIRS="$MATPLOTLIB_CACHE_DIRS $user_home/.cache/matplotlib $user_home/.matplotlib"
    fi
done

# 执行清除操作
cache_cleared=false
for cache_pattern in $MATPLOTLIB_CACHE_DIRS; do
    # 处理通配符路径
    case "$cache_pattern" in
        *"*"*)
            for cache_dir in $cache_pattern; do
                if [ -d "$cache_dir" ] || [ -f "$cache_dir" ]; then
                    echo "删除matplotlib缓存: $cache_dir"
                    rm -rf "$cache_dir"
                    cache_cleared=true
                fi
            done
            ;;
        *)
            if [ -d "$cache_pattern" ]; then
                echo "删除matplotlib缓存目录: $cache_pattern"
                rm -rf "$cache_pattern"
                cache_cleared=true
            fi
            ;;
    esac
done

if [ "$cache_cleared" = true ]; then
    echo "matplotlib字体缓存清除完成"
else
    echo "未找到matplotlib字体缓存文件"
fi

# 提供Python命令来清除matplotlib缓存
echo ""
echo "如果您想要通过Python代码清除matplotlib缓存，可以运行以下命令:"
echo "python3 -c \"import matplotlib.font_manager as fm; fm._rebuild()\""
echo ""
echo "或者在Python脚本中添加以下代码:"
echo "import matplotlib.font_manager as fm"
echo "fm._rebuild()  # 重建字体缓存"
echo ""

# 运行字体检查脚本（如果存在）
if [ -f "$SCRIPT_DIR/check_msyh_font.py" ]; then
    echo "运行字体检查脚本验证安装结果..."
    echo "----------------------------------------"
    cd "$SCRIPT_DIR" || exit
    if command -v python3 >/dev/null 2>&1; then
        python3 check_msyh_font.py
    else
        echo "Python3 未安装，跳过字体检查脚本"
    fi
fi

echo ""
echo "安装和缓存清理完成!"
echo "重启Python程序或Jupyter Notebook后新字体将生效。"
