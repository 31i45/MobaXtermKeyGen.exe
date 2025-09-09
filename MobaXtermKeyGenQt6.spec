# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files

# 修复__file__未定义的问题
try:
    basedir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    basedir = os.path.abspath(os.getcwd())

sys.path.append(basedir)

block_cipher = None

# 分析应用程序依赖
a = Analysis(
    ['MobaXtermKeyGenQt6.py'],
    pathex=[basedir],
    binaries=[],
    datas=[
        ('MobaXterm.png', '.'),  # 图标文件
    ],
    # 使用PyInstaller内置方法自动收集PyQt6依赖，减少手动声明
    hiddenimports=[
    ],
    hookspath=[],
    hooksconfig={
        # 优化PyQt6的钩子配置
        'pyqt6': {
            'exclude_dlls': ['opengl32sw.dll'],  # 排除不需要的OpenGL库，减小体积
        }
    },
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',  # 排除常见但未使用的大型库
        'scipy',
        'sympy',
        'PIL',
        'IPython',
        'setuptools',
        'pkg_resources',
        'distutils',
    ],
    noarchive=False,
    optimize=2,  # 提高优化级别到2
    cipher=block_cipher,
)

# 收集并排除不必要的Qt翻译文件，显著减小体积
del_list = []
for i, data in enumerate(a.datas):
    # 只保留中文和英文翻译文件
    if 'translations' in data[0] and not ('zh' in data[0] or 'en' in data[0]):
        del_list.append(i)

# 从后往前删除，避免索引偏移
for i in reversed(del_list):
    del a.datas[i]

pyz = PYZ(a.pure, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MobaXtermKeyGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # 禁用strip功能避免Windows上找不到strip命令的错误
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='MobaXterm.png',
)

# 如果需要创建安装包，可取消下面的注释
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.datas,
#     strip=True,
#     upx=True,
#     upx_exclude=[],
#     name='MobaXtermKeyGen',
# )