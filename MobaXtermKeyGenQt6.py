import zipfile
import sys
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog
)
from PyQt6.QtGui import QFont, QIcon, QIntValidator
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

# 添加 Windows 系统支持
import ctypes
from ctypes import wintypes

# 启用视觉样式
ctypes.windll.uxtheme.SetThemeAppProperties(1)

# 设置 DPI 感知
try:
    # Windows 10 及以上版本
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except:
    # 旧版 Windows
    ctypes.windll.user32.SetProcessDPIAware()

# 全局样式定义 - 极简风格
WINDOW_STYLE = """
/* 主窗口样式 */
QMainWindow {
    background-color: #f8f9fa;
}

/* 卡片样式 - 更简洁的设计 */
QWidget#cardWidget {
    background-color: white;
    border-radius: 8px;
    margin: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* 标签样式 - 统一简洁 */
QLabel {
    color: #2c3e50;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}

QLabel[class="subtitle"] {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
}

QLabel[class="footer"] {
    font-size: 12px;
    color: #7f8c8d;
    margin-top: 5px;
}

/* 输入框样式 - 更简洁的边框和内边距 */
QLineEdit {
    padding: 8px 10px;
    border: 1px solid #e1e5e9;
    border-radius: 4px;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
    background-color: white;
    selection-background-color: #0078d7;
    selection-color: white;
}

QLineEdit:focus {
    border-color: #0078d7;
    outline: none;
    box-shadow: 0 0 0 2px rgba(0, 120, 215, 0.2);
}
"""

# 核心功能定义

def VariantBase64Encode(bs: bytes) -> bytes:
    VariantBase64Table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    result = b''
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        coding_int = int.from_bytes(bs[3 * i:3 * i + 3], 'little')
        block = VariantBase64Table[coding_int & 0x3f]
        block += VariantBase64Table[(coding_int >> 6) & 0x3f]
        block += VariantBase64Table[(coding_int >> 12) & 0x3f]
        block += VariantBase64Table[(coding_int >> 18) & 0x3f]
        result += block.encode()

    if left_bytes == 1:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Table[coding_int & 0x3f]
        block += VariantBase64Table[(coding_int >> 6) & 0x3f]
        result += block.encode()
    elif left_bytes == 2:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Table[coding_int & 0x3f]
        block += VariantBase64Table[(coding_int >> 6) & 0x3f]
        block += VariantBase64Table[(coding_int >> 12) & 0x3f]
        result += block.encode()

    return result

def EncryptBytes(key: int, bs: bytes) -> bytes:
    result = bytearray()
    for byte in bs:
        result.append(byte ^ ((key >> 8) & 0xff))
        key = result[-1] & key | 0x482D
    return bytes(result)

def GenerateLicense(license_type: int, count: int, user_name: str, major_version: int, minor_version: int) -> str:
    license_string = f'{license_type}#{user_name}|{major_version}{minor_version}#{count}#{major_version}3{minor_version}6{minor_version}#0#0#0#'
    encoded_license = VariantBase64Encode(EncryptBytes(0x787, license_string.encode())).decode()
    file_name = encoded_license.replace('/', '').replace('\\', '')
    
    with zipfile.ZipFile(file_name, 'w') as f:
        f.writestr('Pro.key', data=encoded_license)
        
    return file_name

# UI组件定义
class ModernButton(QPushButton):
    """自定义现代按钮 - 极简风格"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(34)
        self.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 应用无背景色的极简样式
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0078d7;
                border: 1px solid #0078d7;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #f0f7ff;
            }
            QPushButton:pressed {
                background-color: #e6f2ff;
            }
        """)

# 输入字段组件 - 水平布局
class InputField(QWidget):
    """自定义输入字段组件 - 极简风格统一设计"""
    def __init__(self, label_text, placeholder, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(8)  # 减小间距使界面更紧凑
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(label_text)
        self.label.setProperty("class", "subtitle")
        self.label.setFixedWidth(80)  # 设置标签固定宽度，确保对齐
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)

class StepGuide(QWidget):
    """极简版激活步骤指南组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 使用简单的垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)  # 减小间距
        
        # 简单的3行提示消息，修复路径字符串转义问题
        step1 = QLabel("1. 生成并保存许可证文件")
        step2 = QLabel("2. 复制到MobaXterm安装目录：C:\\Pro\ngram Files (x86)\\Mobatek\\MobaXterm")
        step3 = QLabel("3. 重启软件完成激活")
        
        # 调整左外边距，使其与用户名、版本号等文字对齐
        for label in [step1, step2, step3]:
            label.setStyleSheet("font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; color: #4a4a4a; margin-left: 10px;")
            layout.addWidget(label)

class MobaXtermKeyGenApp(QMainWindow):
    """MobaXterm许可证生成器主窗口 - 极简风格设计"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MobaXterm 许可证")
        self.setFixedSize(260, 360)  # 优化的窗口尺寸
        
        # 禁用最大化按钮
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        
        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MobaXterm.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Windows系统图标设置
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('mobaxterm.keygen')
        except:
            pass
        
        self.setup_ui()
        self.center_window()
        
    def center_window(self):
        """窗口居中显示"""
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def setup_ui(self):
        """设置用户界面 - 极简风格"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 设置窗口最小大小
        self.setMinimumSize(260, 340)  # 优化的最小窗口尺寸
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 内容卡片
        card_widget = QWidget()
        card_widget.setObjectName("cardWidget")
        
        card_layout = QVBoxLayout(card_widget)
        card_layout.setSpacing(16)  # 减小组件间距使界面更紧凑
        
        # 用户名输入
        self.name_input = InputField("用户名", "输入您的名称")
        self.name_input.input_field.setText("User")  # 默认值
        self.name_input.input_field.setFixedWidth(120)  # 设置输入框固定宽度
        
        # 版本号输入
        self.version_input = InputField("版本号", "例如: 25.2")
        self.version_input.input_field.setText("25.2")  # 默认值
        self.version_input.input_field.setFixedWidth(120)  # 设置输入框固定宽度
        
        # 用户数量输入
        self.count_input = InputField("用户数", "输入用户数量")
        self.count_input.input_field.setText("1")  # 默认值
        self.count_input.input_field.setValidator(QIntValidator(1, 999))  # 添加整数验证器
        self.count_input.input_field.setFixedWidth(120)  # 设置输入框固定宽度
        
        # 生成按钮
        self.generate_button = ModernButton("生成许可证")
        self.generate_button.clicked.connect(self.generate_license)
        
        # 激活步骤指南
        self.step_guide = StepGuide()
        
        # 页脚备注
        footer_note = QLabel("仅个人学习使用，请尊重知识产权")
        footer_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_note.setProperty("class", "footer")
        
        # 添加所有组件到布局
        card_layout.addWidget(self.name_input)
        card_layout.addWidget(self.version_input)
        card_layout.addWidget(self.count_input)
        card_layout.addWidget(self.generate_button)
        card_layout.addWidget(self.step_guide)
        card_layout.addWidget(footer_note)
        
        # 添加卡片到主布局
        main_layout.addWidget(card_widget)
        
        # 应用全局样式
        self.setStyleSheet(WINDOW_STYLE)
        
    def generate_license(self):
        """生成许可证文件"""
        # 获取输入值
        name = self.name_input.input_field.text().strip()
        version = self.version_input.input_field.text().strip()
        
        # 获取并验证用户数量
        try:
            count = int(self.count_input.input_field.text())
            if count < 1 or count > 999:
                return
        except ValueError:
            return
        
        # 提取版本号
        try:
            version_parts = version.split('.')
            major_version = int(version_parts[0]) if version_parts else 25
            minor_version = int(version_parts[1]) if len(version_parts) > 1 else 0
        except (IndexError, ValueError):
            return
        
        lc = None
        try:
            # 生成许可证
            QApplication.processEvents()
            
            lc = GenerateLicense(1, count, name, major_version, minor_version)
            
            # 保存文件对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存许可证文件", "Custom.mxtpro", "MobaXterm许可证文件 (*.mxtpro)"
            )
            
            if file_path:
                shutil.copy2(lc, file_path)
        except Exception as e:
            # 错误处理可以在这里添加
            pass
        finally:
            # 确保清理临时文件
            if lc and os.path.exists(lc):
                try:
                    os.remove(lc)
                except:
                    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置应用程序名称（用于任务栏）
    app.setApplicationName("MobaXterm 许可证生成器")
    
    window = MobaXtermKeyGenApp()
    window.show()
    
    sys.exit(app.exec())