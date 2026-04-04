import os
import sys
import tempfile

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QTextEdit, QGroupBox, QFileDialog,
    QMessageBox, QSizePolicy, QGraphicsView, QGraphicsScene, QCheckBox
)
from PyQt6.QtGui import QKeySequence, QShortcut  # QShortcut在QtGui中
from PyQt6.QtCore import Qt, QTimer  # 添加QTimer导入
import pyperclip

# 尝试导入 latex2mathml 库用于 LaTeX 到 MathML 转换
try:
    import latex2mathml.converter
    LATEX2MATHML_AVAILABLE = True
except ImportError:
    LATEX2MATHML_AVAILABLE = False

# 尝试导入 pynput 库，用于触发系统快捷键
try:
    from pynput.keyboard import Key, Controller
except ImportError:
    # 如果没有安装 pynput，则设置为 None，稍后会提示用户安装
    Key = None
    Controller = None

# 禁用Python字节码缓存
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True

from main_window import MainWindow
from api_client import FormulaAPIClient
from image_handler import ImageHandler
from image_display_panel import ImageDisplayPanel  # 更新导入
from api_and_recognition_panel import APIAndRecognitionPanel
from api_config import TEST_CONFIG  # 测试配置 - 用于开发调试


def create_temp_file(suffix='.png'):
    """创建可靠的临时文件，兼容 PyInstaller 打包"""
    try:
        # 尝试使用系统临时目录
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, dir=temp_dir)
        return temp_file.name
    except Exception as e:
        # 如果失败，尝试使用当前工作目录
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            return temp_file.name
        except Exception:
            # 最后的备用方案：使用固定临时文件名
            import time
            temp_name = f"temp_image_{int(time.time() * 1000)}{suffix}"
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller 打包模式
                temp_path = os.path.join(sys._MEIPASS, temp_name)
            else:
                temp_path = temp_name
            return temp_path


class FormulaRecognizer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和初始大小 - 修改为宽600高500
        self.setWindowTitle("公式识别软件")
        self.resize(600, 500)  # 宽度600px，高度500px
        self.setMinimumSize(600, 500)
        
        # Windows特定：设置应用程序ID以确保任务栏图标正常显示
        if sys.platform == "win32":
            import ctypes
            myappid = 'mytex.formularecognizer.1.0'  # 应用程序ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # 创建中心部件 - 使用标准窗口标志，不包含置顶标志
        central_widget = MainWindow()
        self.setCentralWidget(central_widget)
        
        # 初始化各个模块
        self.api_client = FormulaAPIClient()
        self.image_handler = ImageHandler(self)
        self.ui = central_widget
        
        # 连接信号
        self.ui.right_panel.input_panel.original_view  # 确保右侧面板（图片显示）可用
        self.ui.left_panel.select_image_requested.connect(self.select_image)
        self.ui.left_panel.take_screenshot_requested.connect(self.take_screenshot)
        self.ui.left_panel.retry_recognition_requested.connect(self.retry_recognition)
        self.ui.left_panel.screenshot_shortcut_changed.connect(self.on_screenshot_shortcut_changed)
        self.ui.left_panel.compact_mode_toggled.connect(self.toggle_compact_mode)
        self.ui.left_panel.always_on_top_toggled.connect(self.toggle_always_on_top)
        
        # 状态变量
        self.selected_image_path = None
        self.is_waiting_for_screenshot = False
        self.success_count = 0
        self.fail_count = 0
        self.ui.left_panel.update_record_count(self.success_count, self.fail_count)
        self.is_compact_mode = True  # 默认开启精简模式
        self.normal_window_size = self.size()  # 保存初始正常窗口大小
        
        # 绑定快捷键
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.paste_shortcut.activated.connect(self.paste_image_from_clipboard)
        
        # 加载测试配置（仅用于开发调试）
        if TEST_CONFIG.app_id and TEST_CONFIG.app_secret:
            self.ui.left_panel.set_app_config(TEST_CONFIG.app_id, TEST_CONFIG.app_secret)
        
        # 定时器用于检测超时
        self.timeout_timer = None
        
    def _initialize_default_state(self):
        """延迟初始化默认状态（精简模式和置顶）"""
        # 确保窗口已经完全显示
        if not self.isVisible():
            return
            
        # 先设置置顶状态
        self.toggle_always_on_top(True)
        # 再进入精简模式
        self.is_compact_mode = True
        self.toggle_compact_mode(True)
        
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
            
        # 确保窗口显示后设置置顶
        if not hasattr(self, '_default_state_initialized'):
            self._default_state_initialized = True
            QTimer.singleShot(300, self._initialize_default_state)
        
    def on_screenshot_shortcut_changed(self, shortcut):
        """截图快捷键变化处理"""
        pass  # 暂时留空
        
    def toggle_always_on_top(self, checked):
        """切换窗口置顶状态 - 完全使用Windows API"""
        if sys.platform == "win32":
            try:
                import ctypes
                
                # 获取窗口句柄并转换为整数
                hwnd = int(self.winId())
                
                # Windows常量
                HWND_TOPMOST = ctypes.c_int(-1)
                HWND_NOTOPMOST = ctypes.c_int(-2)
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOACTIVATE = 0x0010
                SWP_ASYNCWINDOWPOS = 0x4000
                
                flags = SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS
                
                if checked:
                    result = ctypes.windll.user32.SetWindowPos(
                        ctypes.c_void_p(hwnd), 
                        HWND_TOPMOST, 
                        0, 0, 0, 0, 
                        flags
                    )
                else:
                    result = ctypes.windll.user32.SetWindowPos(
                        ctypes.c_void_p(hwnd), 
                        HWND_NOTOPMOST, 
                        0, 0, 0, 0, 
                        flags
                    )
                    
                if not result:
                    raise ctypes.WinError()
                    
            except Exception:
                # Windows API置顶失败，尝试重试
                retry_count = getattr(self, '_toggle_always_on_top_retry_count', 0)
                if retry_count < 5:
                    self._toggle_always_on_top_retry_count = retry_count + 1
                    QTimer.singleShot(200, lambda: self.toggle_always_on_top(checked))
                else:
                    # 超过最大重试次数，清理计数器
                    if hasattr(self, '_toggle_always_on_top_retry_count'):
                        delattr(self, '_toggle_always_on_top_retry_count')
        else:
            # Windows平台重新设置应用程序ID以保护任务栏图标
            try:
                import ctypes
                myappid = 'mytex.formularecognizer.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except:
                pass
        
    def toggle_compact_mode(self, checked):
        """切换精简模式 - 只显示图片识别框"""
        self.is_compact_mode = checked
        if self.is_compact_mode:
            # 保存当前正常窗口几何尺寸（必须使用geometry()全量保存）
            self.normal_window_geometry = self.geometry()
            
            # 保存右侧面板的原始尺寸策略
            self.normal_left_size_policy = self.ui.right_panel.sizePolicy()
            
            self.ui.left_panel.compact_mode_btn.setText("完整模式")
            self.ui.left_panel.compact_mode_btn.setChecked(True)  # 同步按钮选中状态
            
            # 隐藏右侧面板，并临时将其水平尺寸策略设为Ignored
            self.ui.right_panel.hide()
            left_policy_ignored = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
            self.ui.right_panel.setSizePolicy(left_policy_ignored)
            
            # 隐藏左侧面板中的非目标组件，只保留图片识别按钮面板
            self.ui.left_panel.config_panel.hide()
            self.ui.left_panel.latex_panel.hide()
            
            # 确保图片识别按钮面板可见
            self.ui.left_panel.buttons_panel.setVisible(True)
            self.ui.left_panel.buttons_panel.adjustSize()
            
            # 获取图片识别框的实际尺寸（包括标题栏）
            buttons_size = self.ui.left_panel.buttons_panel.sizeHint()
            buttons_width = buttons_size.width()
            buttons_height = buttons_size.height()
            
            # 使用主窗口固定边距(10,10,10,10)计算精简模式窗口大小
            # 主窗口边距固定为10px，严禁在模式切换时动态修改
            window_width = buttons_width + 20  # 左右边距各10px
            window_height = buttons_height + 20  # 上下边距各10px
            self.resize(window_width, window_height)
            self.adjustSize()
            
            # 使用最小和最大尺寸限制替代setFixedSize
            self.setMinimumSize(window_width, window_height)
            self.setMaximumSize(window_width, window_height)
            
            # 添加强制布局重算
            self.ui.layout().update()
            
        else:
            self.ui.left_panel.compact_mode_btn.setText("精简模式")
            self.ui.left_panel.compact_mode_btn.setChecked(False)  # 同步按钮选中状态
            
            # 恢复右侧面板的原始尺寸策略
            self.ui.right_panel.setSizePolicy(self.normal_left_size_policy)
            # 显示所有面板
            self.ui.right_panel.show()
            self.ui.left_panel.config_panel.show()
            self.ui.left_panel.latex_panel.show()
            
            # 强制左侧面板及其内部布局重新计算
            self.ui.left_panel.layout().update()
            self.ui.left_panel.adjustSize()
            
            # 先清除固定尺寸限制（符合规范顺序要求）
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            
            # 恢复之前保存的窗口几何尺寸
            self.setGeometry(self.normal_window_geometry)
            
            # 重新设置主布局参数
            main_layout = self.ui.layout()
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            main_layout.setStretch(0, 0)
            main_layout.setStretch(1, 1)
            
            # 最后设置最小尺寸限制（符合规范：清除限制 -> 恢复几何 -> 设置新限制）
            self.setMinimumSize(600, 500)
            
            # 确保窗口正确显示
            self.show()
            
            # 添加强制布局重算
            self.ui.layout().update()
            
    def select_image(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片文件",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;所有文件 (*.*)"
        )

        if file_path:
            self.selected_image_path = file_path
            # 显示原图在上方区域
            self.image_handler.display_original_image(file_path, self.ui.right_panel)
            self.ui.left_panel.clear_result_text()
            self.ui.left_panel.show_processing_message()
            
            # 自动执行识别
            self.auto_recognize_formula()

    def paste_image_from_clipboard(self):
        """从剪贴板粘贴图片"""
        from PIL import ImageGrab
        
        try:
            image = ImageGrab.grabclipboard()
            
            if image is not None:
                temp_path = create_temp_file('.png')
                image.save(temp_path, 'PNG')
                self.selected_image_path = temp_path
                self.image_handler.display_original_image(temp_path, self.ui.right_panel)
                self.ui.left_panel.clear_result_text()
                self.ui.left_panel.show_processing_message()
                self.auto_recognize_formula()
            else:
                # 根据项目规范，剪贴板无图片时静默返回，不弹窗警告
                return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"从剪贴板读取图片失败: {str(e)}")

    def start_clipboard_monitoring(self):
        """启动剪贴板变化监听 - 立即开始检查"""
        # 记录当前剪贴板的图片内容作为基准（触发截图前绝不清理剪贴板）
        try:
            from PIL import ImageGrab
            current_image = ImageGrab.grabclipboard()
            if current_image is not None:
                # 将图片转换为可比较的形式（使用临时文件路径或哈希）
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                current_image.save(temp_path, 'PNG')
                self.clipboard_baseline_path = temp_path
                self.clipboard_has_baseline = True
            else:
                self.clipboard_baseline_path = None
                self.clipboard_has_baseline = False
        except:
            self.clipboard_baseline_path = None
            self.clipboard_has_baseline = False
            
        self.is_waiting_for_screenshot = True
        # 立即开始检查（不等待）
        self.check_clipboard_for_changes()
        
    def _images_are_different(self, current_image, baseline_path):
        """比较当前图片与基准图片是否不同"""
        if not baseline_path or not os.path.exists(baseline_path):
            return True
            
        try:
            # 保存当前图片到临时文件进行比较
            temp_current = create_temp_file('.png')
            current_image.save(temp_current, 'PNG')
            
            # 比较文件大小
            current_size = os.path.getsize(temp_current)
            baseline_size = os.path.getsize(baseline_path)
            
            if current_size != baseline_size:
                # 文件大小不同，肯定是不同图片
                os.remove(temp_current)
                return True
                
            # 如果文件大小相同，进一步比较内容（读取前几个字节）
            with open(temp_current, 'rb') as f1, open(baseline_path, 'rb') as f2:
                current_header = f1.read(1024)
                baseline_header = f2.read(1024)
                
            os.remove(temp_current)
            
            return current_header != baseline_header
            
        except Exception:
            # 如果比较失败，保守认为是不同图片
            if 'temp_current' in locals() and os.path.exists(temp_current):
                try:
                    os.remove(temp_current)
                except:
                    pass
            return True
        
    def check_clipboard_for_changes(self):
        """检查剪贴板是否发生变化 - 改进的比较逻辑"""
        if not self.is_waiting_for_screenshot:
            return
            
        try:
            from PIL import ImageGrab
            current_image = ImageGrab.grabclipboard()
            
            # 检查是否有新图片
            if current_image is not None:
                # 有图片，检查是否与基准不同
                if not self.clipboard_has_baseline:
                    # 之前没有图片，现在有图片 -> 新截图
                    self.process_new_screenshot(current_image)
                    return
                else:
                    # 之前有图片，需要比较是否相同
                    if self._images_are_different(current_image, self.clipboard_baseline_path):
                        # 图片不同 -> 新截图
                        self.process_new_screenshot(current_image)
                        return
                    # 图片相同，继续监听
            else:
                # 当前没有图片
                if self.clipboard_has_baseline:
                    # 之前有图片，现在没有 -> 剪贴板被清空
                    # 更新基准状态
                    self.clipboard_has_baseline = False
                    if hasattr(self, 'clipboard_baseline_path') and self.clipboard_baseline_path:
                        try:
                            os.remove(self.clipboard_baseline_path)
                        except:
                            pass
                        self.clipboard_baseline_path = None
                
            # 继续监听（延长到30秒，每100ms检查一次，共300次）
            if not hasattr(self, 'clipboard_check_count'):
                self.clipboard_check_count = 0
                
            self.clipboard_check_count += 1
            
            # 监听30秒（300次检查，每次100ms）
            if self.clipboard_check_count <= 300:
                QTimer.singleShot(100, self.check_clipboard_for_changes)
            else:
                # 超时，停止监听
                self.cleanup_clipboard_monitoring()
                
        except Exception as e:
            # 只在真正出错时才显示错误
            self.cleanup_clipboard_monitoring()
            self.fail_count += 1
            self.ui.left_panel.update_record_count(self.success_count, self.fail_count)
            self.ui.left_panel.show_error("截图处理失败", str(e))
            
    def process_new_screenshot(self, image):
        """处理新的截图"""
        try:
            temp_path = create_temp_file('.png')
            image.save(temp_path, 'PNG')
            self.selected_image_path = temp_path
            self.image_handler.display_original_image(temp_path, self.ui.right_panel)
            self.ui.left_panel.clear_result_text()
            self.ui.left_panel.show_processing_message()
            self.auto_recognize_formula()
            
            # 清理旧的基准文件（如果有）
            if hasattr(self, 'clipboard_baseline_path') and self.clipboard_baseline_path:
                try:
                    os.remove(self.clipboard_baseline_path)
                except:
                    pass
            
            # 更新基准状态为当前图片
            self.clipboard_has_baseline = True
            self.clipboard_baseline_path = temp_path
            
        except Exception as e:
            self.ui.left_panel.show_error("处理截图失败", str(e))
            
    def cleanup_clipboard_monitoring(self):
        """清理剪贴板监听资源"""
        self.is_waiting_for_screenshot = False
        if hasattr(self, 'clipboard_check_count'):
            delattr(self, 'clipboard_check_count')
        # 清理临时文件
        if hasattr(self, 'clipboard_baseline_path') and self.clipboard_baseline_path:
            try:
                os.remove(self.clipboard_baseline_path)
            except:
                pass
            self.clipboard_baseline_path = None
            
    def check_clipboard_for_screenshot(self):
        """保留原有方法以避免引用错误"""
        self.check_clipboard_for_changes()
        
    def take_screenshot(self):
        """截图功能 - 触发系统区域截图快捷键"""
        screenshot_method = self.ui.left_panel.get_current_screenshot_shortcut()
        
        if screenshot_method == "printscreen":
            # 对于PrintScreen，触发Win+Shift+S（Windows区域截图）
            self.trigger_win_shift_s()
        elif screenshot_method == "alt+c":
            self.trigger_alt_c_keys()
        elif screenshot_method == "ctrl+c":
            self.trigger_ctrl_c_keys()
        else:
            # 自定义快捷键
            self.trigger_custom_shortcut(screenshot_method)
            
    def trigger_win_shift_s(self):
        """触发 Windows 区域截图快捷键 Win+Shift+S"""
        if Controller is None or Key is None:
            # 如果没有 pynput，提示用户手动截图
            self.is_waiting_for_screenshot = True
            QMessageBox.information(self, "区域截图", "请按 Win+Shift+S 进行区域截图")
            QTimer.singleShot(100, self.check_clipboard_for_screenshot)
            return
            
        try:
            keyboard = Controller()
            # 按下 Win+Shift+S
            keyboard.press(Key.cmd)
            keyboard.press(Key.shift)
            keyboard.press('s')
            keyboard.release('s')
            keyboard.release(Key.shift)
            keyboard.release(Key.cmd)
            
            # 启动剪贴板监听
            self.start_clipboard_monitoring()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"触发区域截图失败：{str(e)}")
            
    def trigger_alt_c_keys(self):
        """触发 Alt+C 组合键"""
        if Controller is None or Key is None:
            # 如果没有 pynput，回退到手动提示
            self.is_waiting_for_screenshot = True
            QMessageBox.information(self, "区域截图", "请按 Alt+C 进行区域截图")
            QTimer.singleShot(100, self.check_clipboard_for_screenshot)
            return
            
        try:
            keyboard = Controller()
            keyboard.press(Key.alt)
            keyboard.press('c')
            keyboard.release('c')
            keyboard.release(Key.alt)
            # 启动剪贴板监听
            self.start_clipboard_monitoring()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"触发 Alt+C 失败：{str(e)}")
            
    def trigger_ctrl_c_keys(self):
        """触发 Ctrl+C 组合键 - 仍然使用剪贴板方式"""
        if Controller is None or Key is None:
            # 如果没有 pynput，回退到原来的逻辑
            self.fallback_ctrl_c_logic()
            return
            
        try:
            keyboard = Controller()
            keyboard.press(Key.ctrl)
            keyboard.press('c')
            keyboard.release('c')
            keyboard.release(Key.ctrl)
            # 对于Ctrl+C，仍然需要监听剪贴板
            self.paste_image_from_clipboard()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"触发 Ctrl+C 失败：{str(e)}")
            
    def fallback_ctrl_c_logic(self):
        """当没有 pynput 库时的 Ctrl+C 回退逻辑 - 直接从剪贴板获取图片"""
        from PIL import ImageGrab
        
        try:
            image = ImageGrab.grabclipboard()
            
            if image is not None:
                temp_path = create_temp_file('.png')
                image.save(temp_path, 'PNG')
                self.selected_image_path = temp_path
                self.image_handler.display_original_image(temp_path, self.ui.right_panel)
                self.ui.left_panel.clear_result_text()
                self.ui.left_panel.show_processing_message()
                self.auto_recognize_formula()
            else:
                # 对于 Ctrl+C 方式，如果没有图片，提示用户
                QMessageBox.information(self, "提示", "剪贴板中没有图片，请先复制一张图片。")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"从剪贴板读取图片失败: {str(e)}")
            
    def trigger_custom_shortcut(self, shortcut_str):
        """触发自定义快捷键"""
        if Controller is None or Key is None:
            QMessageBox.warning(self, "警告", "缺少 pynput 库，无法触发自定义快捷键。\n请安装：pip install pynput")
            return
            
        try:
            keyboard = Controller()
            keys = shortcut_str.split('+')
            pressed_keys = []
            
            # 按下所有键
            for key in keys:
                key_lower = key.lower()
                if key_lower == 'ctrl':
                    keyboard.press(Key.ctrl)
                    pressed_keys.append(Key.ctrl)
                elif key_lower == 'alt':
                    keyboard.press(Key.alt)
                    pressed_keys.append(Key.alt)
                elif key_lower == 'shift':
                    keyboard.press(Key.shift)
                    pressed_keys.append(Key.shift)
                elif key_lower == 'meta':
                    keyboard.press(Key.cmd)
                    pressed_keys.append(Key.cmd)
                else:
                    # 普通字符键
                    keyboard.press(key.lower())
                    pressed_keys.append(key.lower())
                    
            # 释放所有键（反向顺序）
            for key in reversed(pressed_keys):
                keyboard.release(key)
                
            # 触发后启动剪贴板监听
            self.start_clipboard_monitoring()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"触发自定义快捷键失败：{str(e)}")
            
    def stop_timeout_timer(self):
        """停止超时定时器 - 现在为空方法"""
        pass
        
    def start_timeout_timer(self):
        """启动超时定时器 - 现在为空方法"""
        pass
        
    def on_timeout(self):
        """超时处理"""
        self.is_waiting_for_screenshot = False
        self.timeout_timer = None
        self.fail_count += 1
        self.ui.left_panel.update_record_count(self.success_count, self.fail_count)
        self.ui.left_panel.show_error("截图超时", "5秒内未检测到剪贴板中的图片")
        
    def retry_recognition(self):
        """重试识别功能 - 永远激活，无提示"""
        if not self.selected_image_path:
            # 没有图片时直接返回，不显示任何提示
            return
            
        self.ui.left_panel.clear_result_text()
        self.ui.left_panel.show_processing_message()
        self.auto_recognize_formula()

    def auto_recognize_formula(self):
        """自动执行公式识别"""
        if not self.selected_image_path:
            return

        # 获取API配置
        app_id = self.ui.left_panel.get_app_id()
        app_secret = self.ui.left_panel.get_app_secret()

        if not app_id or not app_secret:
            self.ui.left_panel.clear_result_text()
            self.ui.left_panel.show_config_prompt()
            return

        try:
            # 调用API
            result = self.api_client.recognize_formula_api(
                self.selected_image_path, app_id, app_secret, self.ui.left_panel.get_endpoint_choice()
            )

            if "error" in result:
                self.ui.left_panel.clear_result_text()
                self.ui.left_panel.show_error(result['error'], result.get('details', ''))
                self.fail_count += 1
                self.ui.left_panel.update_record_count(self.success_count, self.fail_count)
            else:
                # 成功识别，显示结果
                self.ui.left_panel.clear_result_text()
                self.ui.left_panel.show_success_result(result)
                
                # 提取置信度并设置
                confidence = 0.0
                if "res" in result:
                    res_data = result["res"]
                    if "conf" in res_data:  # SimpleTex API 使用 conf 字段
                        confidence = float(res_data["conf"])
                    elif "confidence" in res_data:
                        confidence = float(res_data["confidence"])
                    elif "score" in res_data:
                        confidence = float(res_data["score"])
                    elif "prob" in res_data:
                        confidence = float(res_data["prob"])
                    elif "accuracy" in res_data:
                        confidence = float(res_data["accuracy"])
                    # 确保置信度在0-1范围内
                    confidence = max(0.0, min(1.0, confidence))
                
                # 设置置信度显示
                self.ui.left_panel.set_confidence(confidence)
                
                # 在下方区域显示识别结果
                if "res" in result and "latex" in result["res"]:
                    latex_formula = result["res"]["latex"]
                    self.image_handler.display_result_visualization(latex_formula, self.ui.right_panel)
                    
                    # 默认转换为MathML格式并复制到剪贴板
                    if LATEX2MATHML_AVAILABLE:
                        try:
                            mathml_formula = latex2mathml.converter.convert(latex_formula)
                            pyperclip.copy(mathml_formula)
                        except Exception:
                            # 如果转换失败，回退到LaTeX
                            pyperclip.copy(latex_formula)
                    else:
                        # 如果没有latex2mathml库，只复制LaTeX
                        pyperclip.copy(latex_formula)
                
                # 增加成功计数（无论是否有latex字段，只要API调用成功就算成功）
                self.success_count += 1
                self.ui.left_panel.update_record_count(self.success_count, self.fail_count)

        except Exception as e:
            self.ui.left_panel.clear_result_text()
            self.ui.left_panel.show_error(f"识别过程中发生错误: {str(e)}", "")
            self.fail_count += 1
            self.ui.left_panel.update_record_count(self.success_count, self.fail_count)


def main():
    """主函数"""
    # 根据项目规范，启动时严禁在控制台打印任何使用说明或状态信息
    # 所有启动提示已在 GUI 界面中显示
    
    try:
        app = QApplication(sys.argv)
        # 设置全局字体以支持中文显示
        from PyQt6.QtGui import QFont
        font = QFont("Microsoft YaHei", 9)
        app.setFont(font)
        
        window = FormulaRecognizer()
        window.show()
        sys.exit(app.exec())
    except ImportError:
        # 依赖错误，静默退出或可根据需要记录日志
        sys.exit(1)
    except Exception:
        # 其他启动错误，静默退出
        sys.exit(1)


if __name__ == "__main__":
    main()