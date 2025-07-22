#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查matplotlib中微软雅黑字体是否可用的程序
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
import shutil

shutil.rmtree(matplotlib.get_cachedir())  # 重建字体缓存
print("已清除matplotlib字体缓存，重新加载字体...\n")

def check_msyh_fonts():
    """检查微软雅黑字体是否可用"""
    print("=== 微软雅黑字体可用性检查 ===\n")

    # 获取系统中所有可用字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # 微软雅黑的各种可能名称
    msyh_names = [
        'Microsoft YaHei',
        'Microsoft YaHei UI',
        'Microsoft YaHei Light',
        'Microsoft YaHei Bold',
        '微软雅黑',
        'msyh',
        'MSYH'
    ]

    print("1. 检查系统字体列表中的微软雅黑:")
    found_fonts = []
    for font_name in msyh_names:
        if font_name in available_fonts:
            print(f"   ✓ 找到字体: {font_name}")
            found_fonts.append(font_name)
        else:
            print(f"   ✗ 未找到字体: {font_name}")

    print(f"\n找到的微软雅黑字体数量: {len(found_fonts)}")

    # 检查本地字体文件
    print("\n2. 检查本地字体文件:")
    import os
    font_dir = "/home/moling-teru/Spec/font"
    if os.path.exists(font_dir):
        font_files = os.listdir(font_dir)
        print(f"   字体目录: {font_dir}")
        for file in font_files:
            if file.upper().startswith('MSYH'):
                print(f"   ✓ 找到字体文件: {file}")

                # 尝试加载字体文件
                try:
                    font_path = os.path.join(font_dir, file)
                    prop = FontProperties(fname=font_path)
                    print(f"     字体名称: {prop.get_name()}")
                    print(f"     字体样式: {prop.get_style()}")
                    print(f"     字体粗细: {prop.get_weight()}")
                except Exception as e:
                    print(f"     ✗ 加载字体文件失败: {e}")
    else:
        print(f"   ✗ 字体目录不存在: {font_dir}")

    # 测试matplotlib中的字体渲染
    print("\n3. 测试matplotlib字体渲染:")

    # 测试默认字体设置
    try:
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "微软雅黑字体测试\nMicrosoft YaHei Font Test",
                fontsize=16, ha='center', va='center',
                transform=ax.transAxes)
        ax.set_title("字体渲染测试", fontsize=14)

        # 保存测试图片
        output_path = "/home/moling-teru/Spec/font_test.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"   ✓ 字体渲染测试完成，图片已保存至: {output_path}")

    except Exception as e:
        print(f"   ✗ 字体渲染测试失败: {e}")

    # 使用本地字体文件进行测试
    if os.path.exists(font_dir):
        print("\n4. 使用本地字体文件测试:")
        try:
            msyh_path = os.path.join(font_dir, "MSYH.TTC")
            if os.path.exists(msyh_path):
                prop = FontProperties(fname=msyh_path)

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.text(0.5, 0.5, "本地微软雅黑字体测试\nLocal MSYH Font Test",
                        fontproperties=prop, fontsize=16,
                        ha='center', va='center', transform=ax.transAxes)
                ax.set_title("本地字体文件测试", fontproperties=prop, fontsize=14)

                output_path = "/home/moling-teru/Spec/local_font_test.png"
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                plt.close()

                print(f"   ✓ 本地字体文件测试完成，图片已保存至: {output_path}")
            else:
                print(f"   ✗ 本地字体文件不存在: {msyh_path}")

        except Exception as e:
            print(f"   ✗ 本地字体文件测试失败: {e}")

    # 显示当前matplotlib字体配置
    print("\n5. 当前matplotlib字体配置:")
    print(f"   font.family: {plt.rcParams.get('font.family', 'N/A')}")
    print(f"   font.sans-serif: {plt.rcParams.get('font.sans-serif', 'N/A')}")
    print(f"   font.size: {plt.rcParams.get('font.size', 'N/A')}")

    # 推荐解决方案
    print("\n=== 解决方案建议 ===")
    if found_fonts:
        print("✓ 系统已安装微软雅黑字体，可以直接使用")
        print("  推荐设置: plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']")
    elif os.path.exists(os.path.join(font_dir, "MSYH.TTC")):
        print("✓ 找到本地字体文件，可以使用FontProperties指定字体路径")
        print("  推荐方法: prop = FontProperties(fname='font/MSYH.TTC')")
    else:
        print("✗ 未找到微软雅黑字体")
        print("  建议:")
        print("  1. 安装微软雅黑字体到系统")
        print("  2. 或将字体文件放到 font/ 目录下")
        print("  3. 或使用其他中文字体如 SimHei")


if __name__ == "__main__":
    check_msyh_fonts()
